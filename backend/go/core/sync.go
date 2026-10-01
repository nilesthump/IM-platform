package core

import (
	"net/http"
	"strings"
)

type conversationRequest struct {
	SyncVersion    string `json:"syncVersion"`
	Type           string `json:"type"`
	RequestID      string `json:"requestId"`
	ConversationID string `json:"conversationId"`
	AfterSeq       int64  `json:"afterSeq"`
	Limit          int64  `json:"limit"`
}

// Only the existing canonical per-Conversation gap shape is served privately.
// User Sync and client cursor/materialization are outside this task.
func (s *authService) conversationHistory(w http.ResponseWriter, r *http.Request) {
	var v conversationRequest
	if decode(r, &v) != nil || v.SyncVersion != "1.0" || v.Type != "sync.conversation.request" || !socialUUIDPattern.MatchString(v.RequestID) || !socialUUIDPattern.MatchString(v.ConversationID) || v.AfterSeq < 0 || v.Limit < 1 || r.URL.RawQuery != "" {
		writeError(w, r, fail(400, "VALIDATION_FAILED", "Request body is invalid."))
		return
	}
	token, err := bearer(r)
	if err != nil {
		writeError(w, r, fail(401, "AUTH_REQUIRED", "Authentication is required."))
		return
	}
	c, err := s.codec.Parse(token)
	if err != nil {
		writeError(w, r, fail(401, "AUTH_SESSION_REVOKED", "Request rejected"))
		return
	}
	ctx := r.Context()
	tx, err := s.db.Begin(ctx)
	if err != nil {
		writeError(w, r, err)
		return
	}
	defer tx.Rollback(ctx)
	conversation := strings.ToLower(v.ConversationID)
	if err = s.authorizeMessage(ctx, tx, c, conversation); err != nil {
		writeError(w, r, err)
		return
	}
	rows, err := tx.Query(ctx, `SELECT server_message_id,sender_id,request_id,seq,created_at,text_body FROM messages WHERE conversation_id=$1 AND seq>$2 AND kind='TEXT' ORDER BY seq LIMIT $3`, conversation, v.AfterSeq, v.Limit)
	if err != nil {
		writeError(w, r, err)
		return
	}
	messages := make([]storedMessage, 0)
	for rows.Next() {
		m := storedMessage{ConversationID: conversation, Content: textContent{Kind: "TEXT"}}
		if err = rows.Scan(&m.MessageID, &m.SenderID, &m.RequestID, &m.Seq, &m.CreatedAt, &m.Content.Text); err != nil {
			rows.Close()
			writeError(w, r, err)
			return
		}
		messages = append(messages, m)
	}
	err = rows.Err()
	rows.Close()
	if err != nil {
		writeError(w, r, err)
		return
	}
	after := v.AfterSeq
	if len(messages) > 0 {
		after = messages[len(messages)-1].Seq
	}
	var more bool
	if err = tx.QueryRow(ctx, `SELECT EXISTS(SELECT 1 FROM messages WHERE conversation_id=$1 AND seq>$2 AND kind='TEXT')`, conversation, after).Scan(&more); err != nil {
		writeError(w, r, err)
		return
	}
	if err = tx.Commit(ctx); err != nil {
		writeError(w, r, err)
		return
	}
	writeJSON(w, 200, map[string]any{"syncVersion": "1.0", "type": "sync.conversation.page", "requestId": v.RequestID, "conversationId": conversation, "messages": messages, "hasMore": more})
}
