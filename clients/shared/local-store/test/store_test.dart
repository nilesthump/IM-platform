import 'dart:convert';
import 'dart:io';
import 'package:sqlite3/sqlite3.dart';
import 'package:test/test.dart';
import 'package:plugworld_local_store/local_store.dart';

const account = '10000000-0000-4000-8000-000000000001';
const other = '10000000-0000-4000-8000-000000000002';
final root = Directory('../../../').absolute.path;
Map<String, dynamic> fixture(String path) =>
    jsonDecode(File('$root/$path').readAsStringSync()) as Map<String, dynamic>;
Map<String, Object?> object(dynamic input) =>
    Map<String, Object?>.from(input as Map);
final cases =
    (fixture('contracts/fixtures/sync-plugin/golden.json')['cases'] as List)
        .where(
          (c) => (c['steps'] as List).every(
            (s) =>
                ['sync.message', 'sync.user', 'local.failed'].contains(s['op']),
          ),
        )
        .toList();
final scenario =
    (fixture('contracts/fixtures/websocket/golden.json')['scenarios'] as List)
        .firstWhere((s) => s['id'] == 'durable-send-and-created');
final step = (scenario['steps'] as List).firstWhere(
  (s) => s['in']['type'] == 'message.send',
);
final send = object(step['in']);
final outputs = step['out'] as List;
final ack = object(outputs.firstWhere((s) => s['type'] == 'message.ack'));
final realtime = object(
  outputs.firstWhere((s) => s['type'] == 'message.created'),
);
final server = <String, Object?>{
  ...object(realtime['payload']),
  'requestId': realtime['requestId'],
};
final conversation = server['conversationId'] as String;
final request = server['requestId'] as String;

void main() {
  late Directory temp;
  late String path;
  late LocalStore store;
  setUp(() {
    temp = Directory.systemTemp.createTempSync('plugworld-store-');
    path = '${temp.path}/account.sqlite';
    store = LocalStore.open(path, account);
  });
  tearDown(() {
    store.close();
    temp.deleteSync(recursive: true);
  });

  test(
    'canonical storage case selection is complete',
    () => expect(cases.length, 13),
  );
  for (final c in cases) {
    test('canonical SQLite ${c['id']}', () {
      final steps = c['steps'] as List;
      final timelines =
          (c['expect']?['timeline'] ?? c['expect']?['localTimeline']) as List?;
      var last = '';
      var rejected = false;
      final ids = <String>{};
      for (var index = 0; index < steps.length; index++) {
        final s = steps[index];
        final op = s['op'];
        final conv = s['message']?['conversationId'] ?? s['conversationId'];
        if (conv != null) ids.add(conv as String);
        Database? probe;
        if (s['fault'] == 'before_commit') {
          probe = sqlite3.open(path);
          final table = op == 'sync.user' ? 'account' : 'conversation_cursors';
          probe.execute(
            "CREATE TRIGGER fixture_failure BEFORE UPDATE ON $table BEGIN SELECT RAISE(ABORT,'fixture failure'); END",
          );
        }
        try {
          if (op == 'sync.message') {
            store.applyMessages([object(s['message'])]);
            last = 'APPLIED';
          } else if (op == 'sync.user') {
            store.applyUserPage(object(s['page']));
            last = 'APPLIED';
          } else {
            store.localFailed(
              s['conversationId'] as String,
              s['requestId'] as String,
            );
            last =
                store.item(
                      s['conversationId'] as String,
                      s['requestId'] as String,
                    )!['state']
                    as String;
          }
        } catch (_) {
          if (s['fault'] == 'before_commit') {
            last = 'ROLLED_BACK';
          } else {
            rejected = true;
          }
        } finally {
          if (probe != null) {
            probe.execute('DROP TRIGGER fixture_failure');
            probe.close();
          }
        }
        if (timelines != null) {
          assertExpected(store, object(timelines[index]), ids, last);
        }
        if (rejected) break;
      }
      expect(rejected, c['expectError'] == true);
      if (!rejected) assertExpected(store, object(c['expect']), ids, last);
    });
  }

  test('all four entrances interleave and persist one canonical message', () {
    store.localSend(
      conversation,
      request,
      account,
      object(server['content'])['text'] as String,
    );
    store.localSend(
      conversation,
      request,
      account,
      object(server['content'])['text'] as String,
    );
    store.applyRealtime(realtime);
    store.applyAck(ack);
    store.applyMessages([server, server]);
    store.localFailed(conversation, request);
    store.close();
    store = LocalStore.open(path, account);
    expect(store.messages(conversation), hasLength(1));
    final row = store.item(conversation, request)!;
    expect(row['state'], 'SENT');
    expect(row['server_message_id'], server['messageId']);
    expect(row['server_seq'], server['seq']);
    expect(row['server_time'], server['createdAt']);
    expect(store.contiguous(conversation), server['seq']);
  });

  test(
    'ACK merges local data and rejects uncommitted or missing confirmation',
    () {
      expect(() => store.applyAck(ack), throwsStateError);
      store.localSend(
        conversation,
        request,
        account,
        object(server['content'])['text'] as String,
      );
      store.localFailed(conversation, request);
      final invalid = {
        ...ack,
        'payload': {...object(ack['payload']), 'status': 'rejected'},
      };
      expect(() => store.applyAck(invalid), throwsFormatException);
      expect(store.item(conversation, request)!['state'], 'FAILED');
      store.applyAck(ack);
      expect(store.item(conversation, request)!['state'], 'SENT');
    },
  );

  test(
    'identity conflicts roll back whole page and preserve committed row',
    () {
      store.applyMessages([server]);
      final initial = store.messages(conversation);
      final conflicting = {...server, 'seq': (server['seq'] as int) + 1};
      expect(() => store.applyMessages([conflicting]), throwsStateError);
      final another = {
        ...server,
        'requestId': '40000000-0000-4000-8000-000000000099',
      };
      expect(
        () => store.applyMessages([another]),
        throwsA(isA<SqliteException>()),
      );
      expect(store.messages(conversation), initial);
      expect(store.contiguous(conversation), server['seq']);
      final cross = {
        ...another,
        'conversationId': '30000000-0000-4000-8000-000000000099',
      };
      expect(
        () => store.applyMessages([cross]),
        throwsA(isA<SqliteException>()),
      );
      expect(store.messages(cross['conversationId'] as String), isEmpty);
    },
  );

  test('account binding and separate native stores survive reopen', () {
    store.applyMessages([server]);
    expect(() => LocalStore.open(path, other), throwsStateError);
    final a = LocalStore.openAccount('${temp.path}/accounts', account);
    final b = LocalStore.openAccount('${temp.path}/accounts', other);
    try {
      a.applyMessages([server]);
      expect(b.messages(conversation), isEmpty);
      expect(a.messages(conversation), hasLength(1));
    } finally {
      a.close();
      b.close();
    }
  });

  test(
    'migration from an empty version0 database is transactional and idempotent',
    () {
      final migrationPath = '${temp.path}/initial.sqlite';
      var probe = sqlite3.open(migrationPath);
      expect(probe.select('PRAGMA user_version').single['user_version'], 0);
      probe.close();
      var migrated = LocalStore.open(migrationPath, account);
      migrated.applyMessages([server]);
      migrated.close();
      migrated = LocalStore.open(migrationPath, account);
      expect(migrated.messages(conversation), hasLength(1));
      migrated.close();
      probe = sqlite3.open(migrationPath);
      expect(probe.select('PRAGMA user_version').single['user_version'], 1);
      probe.close();
    },
  );

  test('failed initial migration rolls back all newly created objects', () {
    final migrationPath = '${temp.path}/broken.sqlite';
    final probe = sqlite3.open(migrationPath);
    probe.execute('CREATE TABLE messages (preserved TEXT)');
    probe.execute("INSERT INTO messages VALUES ('original')");
    expect(
      () => LocalStore.open(migrationPath, account),
      throwsA(isA<SqliteException>()),
    );
    expect(probe.select('PRAGMA user_version').single['user_version'], 0);
    expect(
      probe.select("SELECT name FROM sqlite_master WHERE name='account'"),
      isEmpty,
    );
    expect(
      probe.select('SELECT preserved FROM messages').single['preserved'],
      'original',
    );
    probe.close();
  });

  test('future schema is rejected without destructive downgrade', () {
    final probe = sqlite3.open(path);
    probe.execute('PRAGMA user_version=2');
    expect(() => LocalStore.open(path, account), throwsStateError);
    expect(probe.select('PRAGMA user_version').single['user_version'], 2);
    probe.close();
  });

  test(
    'batch conflict rolls back earlier materialization and prefix updates',
    () {
      final second = {
        ...server,
        'requestId': '40000000-0000-4000-8000-000000000099',
      };
      expect(
        () => store.applyMessages([server, second]),
        throwsA(isA<SqliteException>()),
      );
      expect(store.messages(conversation), isEmpty);
      expect(store.contiguous(conversation), 0);
    },
  );

  test(
    'opaque user cursor compare protects a page fetched before concurrent change',
    () {
      final c = cases.firstWhere((c) => c['id'] == 'user-friend.changed');
      final page = object(c['steps'][0]['page']);
      store.applyUserPage(page, expectedCursor: '0');
      final before = store.userState;
      expect(
        () => store.applyUserPage({
          ...page,
          'nextCursor': 'opaque',
        }, expectedCursor: '0'),
        throwsStateError,
      );
      expect(store.userCursor, page['nextCursor']);
      expect(store.userState, before);
    },
  );
}

void assertExpected(
  LocalStore store,
  Map<String, Object?> expected,
  Set<String> ids,
  String last,
) {
  final conv = ids.isEmpty ? conversation : ids.first;
  final rows = store.messages(conv);
  final normalized = {
    for (final row in rows.where((r) => r['server_seq'] != null))
      '${row['server_seq']}': row['server_message_id'],
  };
  if (expected.containsKey('cursor'))
    expect(store.userCursor, expected['cursor']);
  if (expected.containsKey('contiguous'))
    expect(store.contiguous(conv), expected['contiguous']);
  if (expected.containsKey('messages'))
    expect(normalized, expected['messages']);
  if (expected.containsKey('userState'))
    expect(store.userState, expected['userState']);
  if (expected.containsKey('last')) expect(last, expected['last']);
  if (expected.containsKey('local')) {
    final local = object(expected['local']);
    for (final entry in local.entries) {
      final parts = entry.key.split('/');
      expect(store.item(parts[0], parts[1])!['state'], entry.value);
    }
  }
  if (expected.containsKey('itemCount'))
    expect(rows.length, expected['itemCount']);
  if (expected.containsKey('conversations')) {
    for (final entry in object(expected['conversations']).entries) {
      assertExpected(store, object(entry.value), {entry.key}, last);
    }
  }
}
