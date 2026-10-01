package core

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http/httptest"
	"testing"
)

func TestAuthorizedHistoryGapPages(t *testing.T) {
	f := newMessageFixture(t, 2)
	for i := 0; i < 3; i++ {
		id, _ := uuid()
		if _, err := f.s.commitMessage(context.Background(), f.claims[0], f.send(id, "history")); err != nil {
			t.Fatal(err)
		}
	}
	request, _ := uuid()
	afterSeq := int64(0)
	v := conversationRequest{SyncVersion: "1.0", Type: "sync.conversation.request", RequestID: request, ConversationID: f.conversation, AfterSeq: &afterSeq, Limit: 2}
	call := func() *httptest.ResponseRecorder {
		b, _ := json.Marshal(v)
		token, _ := f.s.codec.Sign(f.claims[1])
		r := httptest.NewRequest("POST", "/__core/history", bytes.NewReader(b))
		r.Header.Set("Authorization", "Bearer "+token)
		w := httptest.NewRecorder()
		f.s.conversationHistory(w, r)
		return w
	}
	w := call()
	var page struct {
		Messages []storedMessage `json:"messages"`
		HasMore  bool            `json:"hasMore"`
	}
	if w.Code != 200 || json.Unmarshal(w.Body.Bytes(), &page) != nil || len(page.Messages) != 2 || page.Messages[0].Seq != 1 || page.Messages[1].Seq != 2 || !page.HasMore {
		t.Fatal("first gap page failed")
	}
	afterSeq = 2
	w = call()
	if w.Code != 200 || json.Unmarshal(w.Body.Bytes(), &page) != nil || len(page.Messages) != 1 || page.Messages[0].Seq != 3 || page.HasMore {
		t.Fatal("terminal gap page failed")
	}
	f.db.Exec(context.Background(), `UPDATE conversation_members SET left_at=now() WHERE conversation_id=$1 AND user_id=$2`, f.conversation, f.users[1])
	if call().Code != 403 {
		t.Fatal("history leaks to nonmember")
	}
	v.Limit = 0
	if call().Code != 400 {
		t.Fatal("invalid canonical limit accepted")
	}
}

func TestHistoryRequiresPresentIntegerAfterSeq(t *testing.T) {
	f := newMessageFixture(t, 2)
	id, _ := uuid()
	if _, err := f.s.commitMessage(context.Background(), f.claims[0], f.send(id, "history")); err != nil {
		t.Fatal(err)
	}
	request, _ := uuid()
	token, _ := f.s.codec.Sign(f.claims[1])
	for _, tc := range []struct {
		name    string
		value   any
		present bool
		status  int
		count   int
	}{
		{"missing", nil, false, 400, 0}, {"null", nil, true, 400, 0}, {"negative", -1, true, 400, 0}, {"string", "0", true, 400, 0}, {"fraction", 0.5, true, 400, 0}, {"zero", 0, true, 200, 1}, {"positive", 1, true, 200, 0},
	} {
		t.Run(tc.name, func(t *testing.T) {
			body := map[string]any{"syncVersion": "1.0", "type": "sync.conversation.request", "requestId": request, "conversationId": f.conversation, "limit": 2}
			if tc.present {
				body["afterSeq"] = tc.value
			}
			b, err := json.Marshal(body)
			if err != nil {
				t.Fatal(err)
			}
			r := httptest.NewRequest("POST", "/__core/history", bytes.NewReader(b))
			r.Header.Set("Authorization", "Bearer "+token)
			w := httptest.NewRecorder()
			f.s.conversationHistory(w, r)
			if w.Code != tc.status {
				t.Fatalf("HTTP %d, want %d", w.Code, tc.status)
			}
			if tc.status == 400 {
				var v struct {
					Error struct {
						Code string `json:"code"`
					} `json:"error"`
				}
				if json.Unmarshal(w.Body.Bytes(), &v) != nil || v.Error.Code != "VALIDATION_FAILED" {
					t.Fatal("invalid request not rejected canonically")
				}
			} else {
				var v struct {
					Messages []storedMessage `json:"messages"`
				}
				if json.Unmarshal(w.Body.Bytes(), &v) != nil || len(v.Messages) != tc.count {
					t.Fatal("valid cursor history differs")
				}
			}
		})
	}
}
