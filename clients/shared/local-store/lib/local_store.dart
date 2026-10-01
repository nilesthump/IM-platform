import 'dart:io';
import 'package:sqlite3/sqlite3.dart';

/// Private native materialized view. It never stores authentication credentials.
class LocalStore {
  final Database _db;
  final String accountId;
  LocalStore._(this._db, this.accountId);

  static LocalStore openAccount(String directory, String accountId) {
    _id(accountId);
    Directory(directory).createSync(recursive: true);
    return open('${directory}/${accountId}.sqlite', accountId);
  }

  static LocalStore open(String path, String accountId) {
    _id(accountId);
    final db = sqlite3.open(path);
    final store = LocalStore._(db, accountId);
    try {
      store._transaction(() {
        final version = db.select('PRAGMA user_version').single['user_version'];
        if (version != 0 && version != 1) {
          throw StateError('Unsupported local schema version');
        }
        if (version == 0) {
          db.execute('''
CREATE TABLE account (singleton INTEGER PRIMARY KEY CHECK(singleton=1),
 account_id TEXT NOT NULL, user_cursor TEXT NOT NULL);
CREATE TABLE messages (
 conversation_id TEXT NOT NULL, request_id TEXT NOT NULL,
 sender_id TEXT, content TEXT, state TEXT NOT NULL
 CHECK(state IN ('SENDING','SENT','FAILED')),
 server_message_id TEXT, server_seq INTEGER CHECK(server_seq > 0),
 server_time TEXT,
 UNIQUE(conversation_id, request_id),
 CHECK((state='SENT' AND server_message_id IS NOT NULL AND server_seq IS NOT NULL
 AND server_time IS NOT NULL AND sender_id IS NOT NULL AND content IS NOT NULL)
 OR (state!='SENT' AND server_message_id IS NULL AND server_seq IS NULL AND server_time IS NULL)));
CREATE UNIQUE INDEX message_server_identity ON messages(server_message_id)
 WHERE server_message_id IS NOT NULL;
CREATE UNIQUE INDEX message_conversation_sequence ON messages(conversation_id, server_seq)
 WHERE server_seq IS NOT NULL;
CREATE TABLE conversation_cursors (
 conversation_id TEXT PRIMARY KEY, contiguous_seq INTEGER NOT NULL CHECK(contiguous_seq >= 0));
CREATE TABLE user_events (
 event_id TEXT PRIMARY KEY, cursor TEXT NOT NULL, kind TEXT NOT NULL,
 subject_id TEXT NOT NULL, revision INTEGER NOT NULL CHECK(revision > 0));
CREATE TABLE user_state (
 kind TEXT NOT NULL, subject_id TEXT NOT NULL, revision INTEGER NOT NULL CHECK(revision > 0),
 PRIMARY KEY(kind, subject_id));
''');
          db.execute('INSERT INTO account VALUES (1, ?, ?)', [accountId, '0']);
          db.execute('PRAGMA user_version=1');
        }
        if (db
                .select('SELECT account_id FROM account WHERE singleton=1')
                .single['account_id'] !=
            accountId) {
          throw StateError('Account does not match this store');
        }
      });
      return store;
    } catch (_) {
      db.close();
      rethrow;
    }
  }

  void close() => _db.close();

  T _transaction<T>(T Function() body) {
    _db.execute('BEGIN IMMEDIATE');
    try {
      final result = body();
      _db.execute('COMMIT');
      return result;
    } catch (_) {
      _db.execute('ROLLBACK');
      rethrow;
    }
  }

  static String _id(Object? value) {
    if (value is! String ||
        !RegExp(
          r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$',
        ).hasMatch(value)) {
      throw FormatException('Invalid identity');
    }
    return value;
  }

  static String _text(Object? value) {
    if (value is! String || value.isEmpty || value.length > 4096) {
      throw FormatException('Invalid message text');
    }
    return value;
  }

  static Map<String, Object?> _map(Object? value) {
    if (value is! Map) throw FormatException('Expected object');
    return Map<String, Object?>.from(value);
  }

  Map<String, Object?>? item(String conversationId, String requestId) {
    final rows = _db.select(
      'SELECT * FROM messages WHERE conversation_id=? AND request_id=?',
      [conversationId, requestId],
    );
    return rows.isEmpty ? null : Map<String, Object?>.from(rows.single);
  }

  List<Map<String, Object?>> messages(String conversationId) => _db
      .select(
        'SELECT * FROM messages WHERE conversation_id=? ORDER BY server_seq, request_id',
        [conversationId],
      )
      .map((r) => Map<String, Object?>.from(r))
      .toList();

  String get userCursor =>
      _db
              .select('SELECT user_cursor FROM account WHERE singleton=1')
              .single['user_cursor']
          as String;

  int contiguous(String conversationId) {
    final rows = _db.select(
      'SELECT contiguous_seq FROM conversation_cursors WHERE conversation_id=?',
      [conversationId],
    );
    return rows.isEmpty ? 0 : rows.single['contiguous_seq'] as int;
  }

  Map<String, int> get userState => {
    for (final row in _db.select('SELECT * FROM user_state'))
      '${row['kind']}/${row['subject_id']}': row['revision'] as int,
  };

  void localSend(
    String conversationId,
    String requestId,
    String senderId,
    String text,
  ) {
    _local(
      conversationId,
      requestId,
      'SENDING',
      senderId: _id(senderId),
      content: _text(text),
    );
  }

  void localFailed(String conversationId, String requestId) =>
      _local(conversationId, requestId, 'FAILED');

  void _local(
    String conversationId,
    String requestId,
    String state, {
    String? senderId,
    String? content,
  }) {
    _id(conversationId);
    _id(requestId);
    _transaction(() {
      final old = item(conversationId, requestId);
      if (old != null) {
        if ((senderId != null &&
                old['sender_id'] != null &&
                old['sender_id'] != senderId) ||
            (content != null &&
                old['content'] != null &&
                old['content'] != content)) {
          throw StateError('Local request identity conflict');
        }
      }
      _db.execute(
        '''
INSERT INTO messages(conversation_id,request_id,sender_id,content,state) VALUES(?,?,?,?,?)
ON CONFLICT(conversation_id,request_id) DO UPDATE SET
 sender_id=COALESCE(messages.sender_id,excluded.sender_id),
 content=COALESCE(messages.content,excluded.content),
 state=CASE WHEN messages.state='SENT' THEN 'SENT' ELSE excluded.state END
''',
        [conversationId, requestId, senderId, content, state],
      );
    });
  }

  void applyAck(Map<String, Object?> envelope) {
    if (envelope['type'] != 'message.ack' ||
        envelope['protocolVersion'] != '1.0') {
      throw FormatException('Expected committed message ACK');
    }
    final payload = _map(envelope['payload']);
    if (payload['status'] != 'committed')
      throw FormatException('ACK is not committed');
    final conversation = _id(payload['conversationId']);
    final request = _id(envelope['requestId']);
    _transaction(() {
      final old = item(conversation, request);
      if (old == null || old['sender_id'] == null || old['content'] == null) {
        throw StateError('ACK has no matching local send');
      }
      _merge({
        ...payload,
        'requestId': request,
        'senderId': old['sender_id'],
        'content': {'kind': 'TEXT', 'text': old['content']},
      });
    });
  }

  void applyRealtime(Map<String, Object?> envelope) {
    if (envelope['type'] != 'message.created' ||
        envelope['protocolVersion'] != '1.0') {
      throw FormatException('Expected realtime message');
    }
    applyMessages([
      {..._map(envelope['payload']), 'requestId': envelope['requestId']},
    ]);
  }

  void applyMessages(List<Map<String, Object?>> messages) => _transaction(() {
    for (final message in messages) {
      _merge(message);
    }
  });

  void _merge(Map<String, Object?> message) {
    final conversation = _id(message['conversationId']);
    final request = _id(message['requestId']);
    final server = _id(message['messageId']);
    final sender = _id(message['senderId']);
    final seq = message['seq'];
    if (seq is! int || seq < 1) throw FormatException('Invalid sequence');
    final time = message['createdAt'];
    if (time is! String || DateTime.tryParse(time) == null)
      throw FormatException('Invalid server time');
    final content = _map(message['content']);
    if (content['kind'] != 'TEXT')
      throw FormatException('Invalid content kind');
    final text = _text(content['text']);
    final old = item(conversation, request);
    if (old != null) {
      for (final pair in {
        'server_message_id': server,
        'server_seq': seq,
        'server_time': time,
        'sender_id': sender,
        'content': text,
      }.entries) {
        if (old[pair.key] != null && old[pair.key] != pair.value) {
          throw StateError('Immutable message identity or content conflict');
        }
      }
    }
    _db.execute(
      '''
INSERT INTO messages(conversation_id,request_id,sender_id,content,state,server_message_id,server_seq,server_time)
 VALUES(?,?,?,?,'SENT',?,?,?)
ON CONFLICT(conversation_id,request_id) DO UPDATE SET
 sender_id=excluded.sender_id,content=excluded.content,state='SENT',
 server_message_id=excluded.server_message_id,server_seq=excluded.server_seq,server_time=excluded.server_time
''',
      [conversation, request, sender, text, server, seq, time],
    );
    _db.execute(
      'INSERT INTO conversation_cursors VALUES (?,0) ON CONFLICT DO NOTHING',
      [conversation],
    );
    var prefix = contiguous(conversation);
    while (_db.select(
      'SELECT 1 FROM messages WHERE conversation_id=? AND server_seq=?',
      [conversation, prefix + 1],
    ).isNotEmpty) {
      prefix++;
    }
    _db.execute(
      'UPDATE conversation_cursors SET contiguous_seq=? WHERE conversation_id=?',
      [prefix, conversation],
    );
  }

  /// Cursor is opaque. A caller can bind a fetched page to its starting cursor.
  void applyUserPage(Map<String, Object?> page, {String? expectedCursor}) {
    if (page['type'] != 'sync.user.page' ||
        page['syncVersion'] != '1.0' ||
        page['events'] is! List ||
        page['hasMore'] is! bool) {
      throw FormatException('Invalid user Sync page');
    }
    _id(page['requestId']);
    final cursor = page['nextCursor'];
    if (cursor is! String || cursor.isEmpty || cursor.length > 256)
      throw FormatException('Invalid cursor');
    _transaction(() {
      if (expectedCursor != null && userCursor != expectedCursor) {
        throw StateError('Stale user Sync page');
      }
      for (final input in page['events'] as List) {
        final event = _map(input);
        final kind = event['kind'];
        if (![
          'friend.changed',
          'conversation.changed',
          'membership.changed',
          'plugin.changed',
        ].contains(kind)) {
          throw FormatException('Unsupported user event');
        }
        final eventId = _id(event['eventId']);
        final subject = _id(event['subjectId']);
        final revision = event['revision'];
        if (revision is! int || revision < 1)
          throw FormatException('Invalid revision');
        final eventCursor = event['cursor'];
        if (eventCursor is! String ||
            eventCursor.isEmpty ||
            eventCursor.length > 256)
          throw FormatException('Invalid event cursor');
        final previous = _db.select(
          'SELECT * FROM user_events WHERE event_id=?',
          [eventId],
        );
        if (previous.isNotEmpty) {
          final old = previous.single;
          if (old['cursor'] != eventCursor ||
              old['kind'] != kind ||
              old['subject_id'] != subject ||
              old['revision'] != revision) {
            throw StateError('Conflicting user event');
          }
        } else {
          _db.execute('INSERT INTO user_events VALUES (?,?,?,?,?)', [
            eventId,
            eventCursor,
            kind,
            subject,
            revision,
          ]);
        }
        _db.execute(
          '''
INSERT INTO user_state VALUES (?,?,?)
ON CONFLICT(kind,subject_id) DO UPDATE SET revision=MAX(user_state.revision,excluded.revision)
''',
          [kind, subject, revision],
        );
      }
      _db.execute('UPDATE account SET user_cursor=? WHERE singleton=1', [
        cursor,
      ]);
    });
  }
}
