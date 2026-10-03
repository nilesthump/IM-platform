package core

import (
	"bufio"
	"bytes"
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"encoding/binary"
	"encoding/json"
	"errors"
	"io"
	"math"
	"net/http"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/jackc/pgx/v5"
)

var syncNumber = regexp.MustCompile(`^(-?)([0-9]+)(?:\.([0-9]+))?(?:[eE]([+-]?[0-9]+))?$`)

// JSON integer means mathematical integrality, including decimal/exponent forms.
// Saturate only after proving integrality; memory is bounded by the input, not exponent.
func syncInteger(raw json.RawMessage, cap int64) (int64, bool) {
	m := syncNumber.FindStringSubmatch(string(raw))
	if m == nil {
		return 0, false
	}
	digits := strings.TrimLeft(m[2]+m[3], "0")
	if digits == "" {
		return 0, true
	}
	if m[1] == "-" {
		return 0, false
	}
	exponent := int64(0)
	if m[4] != "" {
		value, e := strconv.ParseInt(m[4], 10, 64)
		if e != nil {
			if strings.HasPrefix(m[4], "-") {
				return 0, false
			}
			return cap, true
		}
		exponent = value
	}
	fraction := int64(len(m[3]))
	// An exponent too negative cannot turn nonzero finite input into an integer.
	if exponent < -int64(len(digits)) {
		return 0, false
	}
	if exponent < fraction {
		remove := fraction - exponent
		if remove > int64(len(digits)) {
			return 0, false
		}
		tail := digits[len(digits)-int(remove):]
		if strings.Trim(tail, "0") != "" {
			return 0, false
		}
		digits = digits[:len(digits)-int(remove)]
		exponent = fraction
	}
	zeros := exponent - fraction
	capText := strconv.FormatInt(cap, 10)
	if zeros > int64(len(capText)) || int64(len(digits))+zeros > int64(len(capText)) {
		return cap, true
	}
	digits += strings.Repeat("0", int(zeros))
	if len(digits) == len(capText) && digits > capText {
		return cap, true
	}
	value, e := strconv.ParseInt(digits, 10, 64)
	return value, e == nil
}

func syncFailure(w http.ResponseWriter, id string, err error) {
	var e apiError
	if !errors.As(err, &e) {
		http.Error(w, "Sync unavailable", http.StatusServiceUnavailable)
		return
	}
	writeJSON(w, e.Status, map[string]any{"error": map[string]string{"code": e.Code, "message": e.Message}, "requestId": id})
}

func (s *authService) syncInput(w http.ResponseWriter, r *http.Request, conversation bool) (map[string]json.RawMessage, string, string, claims, bool) {
	w.Header().Set("Cache-Control", "no-store")
	id, _ := uuid()
	body, err := syncJSON(r.Body)
	var fields map[string]json.RawMessage
	if err == nil {
		err = json.Unmarshal(body, &fields)
	}
	var decoded string
	if err == nil && json.Unmarshal(fields["requestId"], &decoded) == nil && socialUUIDPattern.MatchString(decoded) {
		id = decoded
	}
	reject := func(e error) (map[string]json.RawMessage, string, string, claims, bool) {
		syncFailure(w, id, e)
		return nil, id, "", claims{}, false
	}
	if r.URL.RawQuery != "" || r.URL.ForceQuery || err != nil || fields == nil || !socialUUIDPattern.MatchString(decoded) {
		return reject(fail(400, "VALIDATION_FAILED", "Request body or query is invalid."))
	}
	token, err := bearer(r)
	if err != nil {
		return reject(err)
	}
	c, err := s.authenticate(r.Context(), token)
	if err != nil {
		return reject(err)
	}
	var version string
	if string(fields["syncVersion"]) == "null" || json.Unmarshal(fields["syncVersion"], &version) != nil {
		return reject(fail(400, "VALIDATION_FAILED", "Sync version is invalid."))
	}
	if version != "1.0" {
		return reject(fail(426, "PROTOCOL_VERSION_UNSUPPORTED", "Sync version is unsupported."))
	}
	expected := map[string]bool{"syncVersion": true, "type": true, "requestId": true, "limit": true}
	kind := "sync.user.request"
	if conversation {
		expected["conversationId"] = true
		expected["afterSeq"] = true
		kind = "sync.conversation.request"
	} else {
		expected["cursor"] = true
	}
	if len(fields) != len(expected) {
		return reject(fail(400, "VALIDATION_FAILED", "Sync fields are invalid."))
	}
	for key := range fields {
		if !expected[key] {
			return reject(fail(400, "VALIDATION_FAILED", "Sync fields are invalid."))
		}
	}
	var typ string
	if json.Unmarshal(fields["type"], &typ) != nil || typ != kind {
		return reject(fail(400, "VALIDATION_FAILED", "Sync type is invalid."))
	}
	return fields, id, token, c, true
}

func (s *authService) syncCursor(user string, position int64) string {
	payload := make([]byte, 8)
	binary.BigEndian.PutUint64(payload, uint64(position))
	mac := hmac.New(sha256.New, s.codec.Key)
	mac.Write([]byte("im-sync-user-cursor-v1\x00" + strings.ToLower(user) + "\x00"))
	mac.Write(payload)
	return base64.RawURLEncoding.EncodeToString(append(payload, mac.Sum(nil)...))
}

func (s *authService) syncPosition(user, cursor string) (int64, bool) {
	if cursor == "0" {
		return 0, true
	}
	b, err := base64.RawURLEncoding.DecodeString(cursor)
	if err != nil || len(b) != 40 {
		return 0, false
	}
	position := binary.BigEndian.Uint64(b[:8])
	if position == 0 || position > math.MaxInt64 {
		return 0, false
	}
	canonical := s.syncCursor(user, int64(position))
	return int64(position), hmac.Equal([]byte(cursor), []byte(canonical))
}

type syncUserEvent struct {
	EventID   string      `json:"eventId"`
	Cursor    string      `json:"cursor"`
	Kind      string      `json:"kind"`
	SubjectID string      `json:"subjectId"`
	Revision  json.Number `json:"revision"`
}

func (s *authService) syncUser(w http.ResponseWriter, r *http.Request) {
	fields, id, token, c, ok := s.syncInput(w, r, false)
	if !ok {
		return
	}
	reject := func(err error) { syncFailure(w, id, err) }
	var cursor string
	limit, ok := syncInteger(fields["limit"], 100)
	if !ok || limit == 0 || json.Unmarshal(fields["cursor"], &cursor) != nil || len(cursor) == 0 || len(cursor) > 256 {
		reject(fail(400, "VALIDATION_FAILED", "Sync cursor or limit is invalid."))
		return
	}
	after, ok := s.syncPosition(c.UserID, cursor)
	if !ok {
		reject(fail(400, "VALIDATION_FAILED", "Sync cursor is invalid."))
		return
	}
	ctx := r.Context()
	tx, err := s.db.Begin(ctx)
	if err != nil {
		reject(err)
		return
	}
	defer tx.Rollback(ctx)
	var locked string
	// Social producers lock the same user before allocating IDs. Waiting here,
	// then reading at READ COMMITTED, includes every earlier allocated eligible ID.
	if err = tx.QueryRow(ctx, `SELECT u.user_id FROM users u WHERE u.user_id=$1 FOR SHARE`, c.UserID).Scan(&locked); err != nil {
		reject(err)
		return
	}
	if err = tx.QueryRow(ctx, `SELECT session_id FROM sessions WHERE user_id=$1 AND client_type=$2 FOR SHARE`, c.UserID, c.ClientType).Scan(&locked); err != nil && !errors.Is(err, pgx.ErrNoRows) {
		reject(err)
		return
	}
	// Reparse token and recheck exact canonical auth failures after blocking locks.
	if _, err = s.syncAuthenticate(ctx, tx, token); err != nil {
		reject(err)
		return
	}
	if after != 0 {
		var exists bool
		err = tx.QueryRow(ctx, `SELECT EXISTS(SELECT 1 FROM user_sync_events WHERE user_id=$1 AND cursor_id=$2 AND event_type IN ('friend.changed','conversation.changed','membership.changed','plugin.changed'))`, c.UserID, after).Scan(&exists)
		if err != nil {
			reject(err)
			return
		}
		if !exists {
			reject(fail(400, "VALIDATION_FAILED", "Sync cursor is invalid."))
			return
		}
	}
	rows, err := tx.Query(ctx, `SELECT cursor_id,event_type,payload FROM user_sync_events WHERE user_id=$1 AND cursor_id>$2 AND event_type IN ('friend.changed','conversation.changed','membership.changed','plugin.changed') ORDER BY cursor_id LIMIT $3`, c.UserID, after, limit+1)
	if err != nil {
		reject(err)
		return
	}
	events := make([]syncUserEvent, 0)
	for rows.Next() {
		var position int64
		var payload []byte
		var kind string
		if err = rows.Scan(&position, &kind, &payload); err != nil {
			break
		}
		var event syncUserEvent
		d := json.NewDecoder(bytes.NewReader(payload))
		d.UseNumber()
		if err = d.Decode(&event); err != nil {
			break
		}
		revision, valid := syncInteger(json.RawMessage(event.Revision), 1)
		if !valid || revision == 0 || !socialUUIDPattern.MatchString(event.EventID) || !socialUUIDPattern.MatchString(event.SubjectID) || event.Kind != kind {
			err = errors.New("invalid authoritative metadata")
			break
		}
		event.Cursor = s.syncCursor(c.UserID, position)
		events = append(events, event)
	}
	if err == nil {
		err = rows.Err()
	}
	rows.Close()
	if err != nil {
		reject(err)
		return
	}
	if err = tx.Commit(ctx); err != nil {
		reject(err)
		return
	}
	more := len(events) > int(limit)
	if more {
		events = events[:limit]
	}
	next := cursor
	if len(events) > 0 {
		next = events[len(events)-1].Cursor
	}
	writeJSON(w, 200, map[string]any{"syncVersion": "1.0", "type": "sync.user.page", "requestId": id, "events": events, "nextCursor": next, "hasMore": more})
}

func (s *authService) syncConversation(w http.ResponseWriter, r *http.Request) {
	fields, id, token, c, ok := s.syncInput(w, r, true)
	if !ok {
		return
	}
	reject := func(err error) { syncFailure(w, id, err) }
	limit, ok := syncInteger(fields["limit"], 100)
	after, valid := syncInteger(fields["afterSeq"], math.MaxInt64)
	var conversation string
	if !ok || limit == 0 || !valid || json.Unmarshal(fields["conversationId"], &conversation) != nil || !socialUUIDPattern.MatchString(conversation) {
		reject(fail(400, "VALIDATION_FAILED", "Sync fields are invalid."))
		return
	}
	conversation = strings.ToLower(conversation)
	ctx := r.Context()
	tx, err := s.db.Begin(ctx)
	if err != nil {
		reject(err)
		return
	}
	defer tx.Rollback(ctx)
	var locked string
	if err = tx.QueryRow(ctx, `SELECT session_id FROM sessions WHERE user_id=$1 AND client_type=$2 FOR SHARE`, c.UserID, c.ClientType).Scan(&locked); err != nil && !errors.Is(err, pgx.ErrNoRows) {
		reject(err)
		return
	}
	if _, err = s.syncAuthenticate(ctx, tx, token); err != nil {
		reject(err)
		return
	}
	err = tx.QueryRow(ctx, `SELECT user_id FROM conversation_members WHERE conversation_id=$1 AND user_id=$2 AND left_at IS NULL FOR SHARE`, conversation, c.UserID).Scan(&locked)
	if err != nil && !errors.Is(err, pgx.ErrNoRows) {
		reject(err)
		return
	}
	if _, authErr := s.syncAuthenticate(ctx, tx, token); authErr != nil {
		reject(authErr)
		return
	}
	if errors.Is(err, pgx.ErrNoRows) {
		reject(fail(403, "AUTHORIZATION_DENIED", "Conversation access is denied."))
		return
	}
	rows, err := tx.Query(ctx, `SELECT conversation_id,seq,server_message_id,sender_id,request_id,created_at,text_body FROM messages WHERE conversation_id=$1 AND seq>$2 ORDER BY seq LIMIT $3`, conversation, after, limit+1)
	if err != nil {
		reject(err)
		return
	}
	messages := make([]storedMessage, 0)
	previous := after
	for rows.Next() {
		var m storedMessage
		m.Content.Kind = "TEXT"
		if err = rows.Scan(&m.ConversationID, &m.Seq, &m.MessageID, &m.SenderID, &m.RequestID, &m.CreatedAt, &m.Content.Text); err != nil {
			break
		}
		if previous == math.MaxInt64 || m.Seq != previous+1 {
			err = errors.New("noncontiguous authoritative message history")
			break
		}
		previous = m.Seq
		messages = append(messages, m)
	}
	if err == nil {
		err = rows.Err()
	}
	rows.Close()
	if err != nil {
		reject(err)
		return
	}
	if err = tx.Commit(ctx); err != nil {
		reject(err)
		return
	}
	more := len(messages) > int(limit)
	if more {
		messages = messages[:limit]
	}
	writeJSON(w, 200, map[string]any{"syncVersion": "1.0", "type": "sync.conversation.page", "requestId": id, "conversationId": conversation, "messages": messages, "hasMore": more})
}

type conversationRequest struct {
	SyncVersion    string `json:"syncVersion"`
	Type           string `json:"type"`
	RequestID      string `json:"requestId"`
	ConversationID string `json:"conversationId"`
	AfterSeq       *int64 `json:"afterSeq"`
	Limit          int64  `json:"limit"`
}

// Only the existing canonical per-Conversation gap shape is served privately.
// User Sync and client cursor/materialization are outside this task.
func (s *authService) conversationHistory(w http.ResponseWriter, r *http.Request) {
	var v conversationRequest
	if decode(r, &v) != nil || v.SyncVersion != "1.0" || v.Type != "sync.conversation.request" || !socialUUIDPattern.MatchString(v.RequestID) || !socialUUIDPattern.MatchString(v.ConversationID) || v.AfterSeq == nil || *v.AfterSeq < 0 || v.Limit < 1 || r.URL.RawQuery != "" {
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
	rows, err := tx.Query(ctx, `SELECT server_message_id,sender_id,request_id,seq,created_at,text_body FROM messages WHERE conversation_id=$1 AND seq>$2 AND kind='TEXT' ORDER BY seq LIMIT $3`, conversation, *v.AfterSeq, v.Limit)
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
	after := *v.AfterSeq
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

// Validate within the held transaction: never wait for another pool connection
// while holding locks/connection needed by other concurrent Sync readers.
func (s *authService) syncAuthenticate(ctx context.Context, tx pgx.Tx, token string) (claims, error) {
	c, err := s.codec.Parse(token)
	if err != nil {
		return c, err
	}
	var sid, typ, status string
	var epoch int64
	var expiry time.Time
	err = tx.QueryRow(ctx, `SELECT session_id, client_type, session_epoch, status, expires_at FROM sessions WHERE user_id=$1 AND client_type=$2`, c.UserID, c.ClientType).Scan(&sid, &typ, &epoch, &status, &expiry)
	if errors.Is(err, pgx.ErrNoRows) {
		var actualType string
		if tx.QueryRow(ctx, `SELECT client_type FROM sessions WHERE user_id=$1 AND session_id=$2`, c.UserID, c.SessionID).Scan(&actualType) == nil && actualType != c.ClientType {
			return c, fail(401, "AUTH_CLIENT_TYPE_MISMATCH", "Access token does not match the active client session.")
		}
		return c, fail(401, "AUTH_SESSION_REVOKED", "Session has been revoked.")
	}
	if err != nil {
		return c, err
	}
	if status != "ACTIVE" || !expiry.After(s.now()) {
		return c, fail(401, "AUTH_SESSION_REVOKED", "Session has been revoked.")
	}
	if epoch != c.SessionEpoch {
		return c, fail(401, "AUTH_SESSION_EPOCH_STALE", "Access token carries a stale session epoch.")
	}
	if sid != c.SessionID || typ != c.ClientType {
		var actualType string
		if tx.QueryRow(ctx, `SELECT client_type FROM sessions WHERE user_id=$1 AND session_id=$2`, c.UserID, c.SessionID).Scan(&actualType) == nil && actualType != c.ClientType {
			return c, fail(401, "AUTH_CLIENT_TYPE_MISMATCH", "Access token does not match the active client session.")
		}
		return c, fail(401, "AUTH_TOKEN_INVALID", "Access token and session binding disagree.")
	}
	return c, nil
}

// Only Sync integer fields require unbounded numeric magnitude. Normalize their
// JSON numeric tokens before buffering: the buffer and coefficient/exponent
// state stay bounded even for a valid coefficient larger than 64 KiB.
// Strings and original JSON grammar remain unchanged; strict body validation
// still follows authentication. No general JSON/value framework is introduced.
func syncJSON(input io.Reader) ([]byte, error) {
	reader := bufio.NewReader(input)
	result := make([]byte, 0, 512)
	inString, escaped := false, false
	for {
		b, err := reader.ReadByte()
		if err == io.EOF {
			return result, nil
		}
		if err != nil {
			return nil, err
		}
		if inString {
			result = append(result, b)
			if escaped {
				escaped = false
			} else if b == '\\' {
				escaped = true
			} else if b == '"' {
				inString = false
			}
		} else if b == ' ' || b == '\n' || b == '\r' || b == '\t' {
			// Keep a separator: removing it could legalize malformed "1 2" as 12.
			if len(result) == 0 || result[len(result)-1] != ' ' {
				result = append(result, ' ')
			}
		} else if b == '-' || (b >= '0' && b <= '9') {
			if err = reader.UnreadByte(); err != nil {
				return nil, err
			}
			number, err := syncJSONNumber(reader)
			if err != nil {
				return nil, err
			}
			result = append(result, number...)
		} else {
			result = append(result, b)
			if b == '"' {
				inString = true
			}
		}
		if len(result) > 65536 {
			return nil, errors.New("Sync nonnumeric JSON exceeds bounded buffer")
		}
	}
}

func syncJSONNumber(reader *bufio.Reader) (string, error) {
	bad := errors.New("invalid JSON number")
	peek := func() byte {
		b, err := reader.Peek(1)
		if err != nil {
			return 0
		}
		return b[0]
	}
	take := func() byte { b, _ := reader.ReadByte(); return b }
	digit := func(b byte) bool { return b >= '0' && b <= '9' }
	negative := false
	if peek() == '-' {
		take()
		negative = true
	}
	if !digit(peek()) {
		return "", bad
	}
	prefix := make([]byte, 0, 19)
	var digits, fraction, trailing int64
	coefficient := func(b byte, decimal bool) {
		if decimal {
			fraction++
		}
		if digits == 0 && b == '0' {
			return
		}
		digits++
		if len(prefix) < 19 {
			prefix = append(prefix, b)
		}
		if b == '0' {
			trailing++
		} else {
			trailing = 0
		}
	}
	first := take()
	coefficient(first, false)
	if first == '0' && digit(peek()) {
		return "", bad
	}
	if first != '0' {
		for digit(peek()) {
			coefficient(take(), false)
		}
	}
	if peek() == '.' {
		take()
		if !digit(peek()) {
			return "", bad
		}
		for digit(peek()) {
			coefficient(take(), true)
		}
	}
	var exponent int64
	expNegative := false
	if peek() == 'e' || peek() == 'E' {
		take()
		if peek() == '-' || peek() == '+' {
			expNegative = take() == '-'
		}
		if !digit(peek()) {
			return "", bad
		}
		for digit(peek()) {
			d := int64(take() - '0')
			if exponent > (math.MaxInt64-d)/10 {
				exponent = math.MaxInt64
			} else {
				exponent = exponent*10 + d
			}
		}
	}
	switch peek() {
	case 0, ',', ']', '}', ' ', '\n', '\r', '\t':
	default:
		return "", bad
	}
	if digits == 0 {
		return "0", nil
	}
	if negative {
		return "-1", nil
	}
	var remove, add int64
	if expNegative {
		if exponent > trailing || fraction > trailing-exponent {
			return "0.5", nil
		}
		remove = fraction + exponent
	} else if exponent >= fraction {
		add = exponent - fraction
	} else {
		remove = fraction - exponent
		if remove > trailing {
			return "0.5", nil
		}
	}
	remaining := digits - remove
	if remaining > 19 || add > 19 || remaining+add > 19 {
		return strconv.FormatInt(math.MaxInt64, 10), nil
	}
	value := string(prefix[:int(remaining)]) + strings.Repeat("0", int(add))
	maximum := strconv.FormatInt(math.MaxInt64, 10)
	if len(value) == 19 && value > maximum {
		return maximum, nil
	}
	return value, nil
}
