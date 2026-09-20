# Auth, User, and Friend Domain Input

This document supplies semantic input to `LOOP1-CONTRACT-001`. Names used below identify domain concepts only; they do not define public wire fields, implementation classes, or database tables.

| Rule ID | Domain statement | Source |
| --- | --- | --- |
| AUF-D-001 | A user MUST have exactly three login slots: WEB, DESKTOP, and MOBILE; at most one Session for a given user and client type may be valid at a time. | Architecture Baseline v1.0, chapter 4.1 and appendix B (Session). |
| AUF-D-002 | Sessions for different client types MAY be valid concurrently for the same user. | Architecture Baseline v1.0, chapter 4.1 and appendix B (Session). |
| AUF-D-003 | A new login for the same user and client type MUST revoke the previous Session and advance the session epoch in one transaction. | Architecture Baseline v1.0, chapter 4.1 and appendix B (Session). |
| AUF-D-004 | PostgreSQL MUST remain authoritative for login state; Gateway memory is only an online-connection and routing cache. | Architecture Baseline v1.0, chapters 2 (F-03), 4.1, and 7.3. |
| AUF-D-005 | A friendship MUST be represented by one normalized unordered user pair, so `(A,B)` and `(B,A)` denote the same friendship. | Architecture Baseline v1.0, chapter 4.2 and appendix B (Friend). |
| AUF-D-006 | Adding a friend in Loop 1 MUST immediately establish the bidirectional friendship and create or reuse the pair's single DIRECT Conversation in the same transaction. | Architecture Baseline v1.0, chapter 4.2 and appendix B (Friend). |
| AUF-D-007 | Loop 1 MUST NOT introduce a friend-request approval flow. | Architecture Baseline v1.0, chapter 4.2. |
| AUF-D-008 | A successful explicit logout MUST revoke the Session and Refresh Token and close its WSS connection; it MUST NOT be specified as deletion of local client history. | Architecture Baseline v1.0, chapter 7.1. |
| AUF-D-009 | Production authentication transport MUST use HTTPS/WSS/TLS; tokens MUST NOT be accepted from a URL query or written to logs or traces, and error responses MUST NOT reveal token material. | Architecture Baseline v1.0, chapter 7.4. |
