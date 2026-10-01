package core

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"strings"
	"time"
	"unicode/utf8"

	"github.com/jackc/pgx/v5"
)

type textContent struct {
	Kind string `json:"kind"`
	Text string `json:"text"`
}
type sendFrame struct {
	ProtocolVersion string `json:"protocolVersion"`
	Type            string `json:"type"`
	RequestID       string `json:"requestId"`
	Payload         struct {
		ConversationID string      `json:"conversationId"`
		Content        textContent `json:"content"`
	} `json:"payload"`
}
type storedMessage struct {
	ConversationID string      `json:"conversationId"`
	Seq            int64       `json:"seq"`
	MessageID      string      `json:"messageId"`
	SenderID       string      `json:"senderId"`
	RequestID      string      `json:"requestId"`
	CreatedAt      time.Time   `json:"createdAt"`
	Content        textContent `json:"content"`
}

func messageFrame(kind, id string, payload any) any {
	return map[string]any{"protocolVersion": "1.0", "type": kind, "requestId": id, "payload": payload}
}
func rejectedMessage(id, code string) any {
	return messageFrame("message.ack", id, map[string]any{"status": "rejected", "error": map[string]string{"code": code, "message": "Request rejected"}})
}
func committedMessage(m storedMessage) any {
	return messageFrame("message.ack", m.RequestID, map[string]any{"status": "committed", "conversationId": m.ConversationID, "messageId": m.MessageID, "seq": m.Seq, "createdAt": m.CreatedAt})
}
func createdMessage(m storedMessage) any {
	return messageFrame("message.created", m.RequestID, map[string]any{"conversationId": m.ConversationID, "messageId": m.MessageID, "senderId": m.SenderID, "seq": m.Seq, "createdAt": m.CreatedAt, "content": m.Content})
}
func (v sendFrame) valid() bool {
	n := utf8.RuneCountInString(v.Payload.Content.Text)
	return v.ProtocolVersion == "1.0" && v.Type == "message.send" && socialUUIDPattern.MatchString(v.RequestID) && socialUUIDPattern.MatchString(v.Payload.ConversationID) && v.Payload.Content.Kind == "TEXT" && n >= 1 && n <= 4096
}

// This private adapter reuses the canonical frame and bound bearer. It is never
// registered under the Gateway's public /v1 reverse proxy.
func (s *authService) sendMessage(w http.ResponseWriter, r *http.Request) {
	var v sendFrame
	if decode(r, &v) != nil || !v.valid() || r.URL.RawQuery != "" {
		writeJSON(w, 200, rejectedMessage(v.RequestID, "VALIDATION_FAILED"))
		return
	}
	token, err := bearer(r)
	if err != nil {
		writeJSON(w, 200, rejectedMessage(v.RequestID, "AUTH_REQUIRED"))
		return
	}
	c, err := s.codec.Parse(token)
	if err != nil {
		writeJSON(w, 200, rejectedMessage(v.RequestID, "AUTH_SESSION_REVOKED"))
		return
	}
	m, err := s.commitMessage(r.Context(), c, v)
	if err != nil {
		code := "MESSAGE_COMMIT_FAILED"
		var e apiError
		if errors.As(err, &e) {
			code = e.Code
		}
		writeJSON(w, 200, rejectedMessage(v.RequestID, code))
		return
	}
	m.RequestID = v.RequestID // ACK echoes the request spelling; storage identity is UUID-normalized.
	writeJSON(w, 200, committedMessage(m))
}

func (s *authService) authorizeMessage(ctx context.Context, tx pgx.Tx, c claims, conversation string) error {
	// Holding the slot shared lock until commit serializes against logout and
	// replacement login, without giving Gateway ownership of Session writes.
	var sid, status string
	var epoch int64
	var expiry time.Time
	err := tx.QueryRow(ctx, `SELECT session_id,session_epoch,status,expires_at FROM sessions WHERE user_id=$1 AND client_type=$2 FOR SHARE`, c.UserID, c.ClientType).Scan(&sid, &epoch, &status, &expiry)
	if errors.Is(err, pgx.ErrNoRows) {
		return fail(401, "AUTH_SESSION_REVOKED", "Request rejected")
	}
	if err != nil {
		return err
	}
	if status != "ACTIVE" || sid != c.SessionID || epoch != c.SessionEpoch || !expiry.After(s.now()) || c.ExpiresAt <= s.now().Unix() {
		return fail(401, "AUTH_SESSION_REVOKED", "Request rejected")
	}
	var member string
	err = tx.QueryRow(ctx, `SELECT user_id FROM conversation_members WHERE conversation_id=$1 AND user_id=$2 AND left_at IS NULL FOR SHARE`, conversation, c.UserID).Scan(&member)
	if errors.Is(err, pgx.ErrNoRows) {
		return fail(403, "AUTHORIZATION_DENIED", "Request rejected")
	}
	return err
}

func (s *authService) commitMessage(ctx context.Context, c claims, v sendFrame) (m storedMessage, err error) {
	tx, err := s.db.Begin(ctx)
	if err != nil {
		return m, err
	}
	defer tx.Rollback(ctx)
	conversation := strings.ToLower(v.Payload.ConversationID)
	request := strings.ToLower(v.RequestID)
	if err = s.authorizeMessage(ctx, tx, c, conversation); err != nil {
		return m, err
	}
	var next int64
	if err = tx.QueryRow(ctx, `SELECT next_seq FROM conversations WHERE conversation_id=$1 FOR UPDATE`, conversation).Scan(&next); err != nil {
		return m, err
	}
	m.ConversationID = conversation
	m.RequestID = request
	m.Content.Kind = "TEXT"
	err = tx.QueryRow(ctx, `SELECT server_message_id,sender_id,seq,created_at,text_body FROM messages WHERE conversation_id=$1 AND request_id=$2`, conversation, request).Scan(&m.MessageID, &m.SenderID, &m.Seq, &m.CreatedAt, &m.Content.Text)
	if err == nil {
		if m.SenderID != c.UserID || m.Content.Text != v.Payload.Content.Text {
			return m, fail(409, "MESSAGE_REQUEST_CONFLICT", "Request rejected")
		}
		err = tx.Commit(ctx)
		return m, err
	}
	if !errors.Is(err, pgx.ErrNoRows) {
		return m, err
	}
	m.MessageID, err = uuid()
	if err != nil {
		return m, err
	}
	m.SenderID = c.UserID
	m.Seq = next
	m.Content = v.Payload.Content
	_, err = tx.Exec(ctx, `UPDATE conversations SET next_seq=next_seq+1 WHERE conversation_id=$1`, conversation)
	if err != nil {
		return m, err
	}
	err = tx.QueryRow(ctx, `INSERT INTO messages(server_message_id,conversation_id,sender_id,request_id,seq,kind,text_body) VALUES($1,$2,$3,$4,$5,'TEXT',$6) RETURNING created_at`, m.MessageID, conversation, c.UserID, request, next, m.Content.Text).Scan(&m.CreatedAt)
	if err != nil {
		return m, err
	}
	payload, err := json.Marshal(createdMessage(m))
	if err != nil {
		return m, err
	}
	event, err := uuid()
	if err != nil {
		return m, err
	}
	_, err = tx.Exec(ctx, `INSERT INTO outbox_events(event_id,aggregate_type,aggregate_id,event_type,conversation_id,message_id,payload) VALUES($1,'message',$2,'message.created',$3,$2,$4)`, event, m.MessageID, conversation, payload)
	if err != nil {
		return m, err
	}
	err = tx.Commit(ctx)
	return m, err
}
