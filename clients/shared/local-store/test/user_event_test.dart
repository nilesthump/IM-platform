import 'dart:convert';
import 'dart:io';
import 'package:plugworld_local_store/local_store.dart';
import 'package:sqlite3/sqlite3.dart';
import 'package:test/test.dart';

const account = '10000000-0000-4000-8000-000000000001';
const other = '10000000-0000-4000-8000-000000000002';
const newEventId = '50000000-0000-4000-8000-000000000099';
Map<String, Object?> object(dynamic input) =>
    Map<String, Object?>.from(input as Map);
final fixture =
    jsonDecode(
          File(
            '../../../contracts/fixtures/sync-plugin/golden.json',
          ).readAsStringSync(),
        )
        as Map;
final canonicalCase = (fixture['cases'] as List).firstWhere(
  (c) => c['id'] == 'user-friend.changed',
);
final page = object(canonicalCase['steps'][0]['page']);
final event = object((page['events'] as List).single);
Map<String, Object?> withEvents(List<Map<String, Object?>> events) => {
  ...page,
  'events': events,
  'nextCursor': 'conflicting-cursor',
};

void main() {
  late Directory temp;
  late String path;
  late LocalStore store;
  setUp(() {
    temp = Directory.systemTemp.createTempSync('plugworld-user-events-');
    path = '${temp.path}/account.sqlite';
    store = LocalStore.open(path, account);
  });
  tearDown(() {
    store.close();
    temp.deleteSync(recursive: true);
  });
  void reopen() {
    store.close();
    store = LocalStore.open(path, account);
  }

  void expectCanonical() {
    expect(store.userCursor, page['nextCursor']);
    expect(store.userState, {
      '${event['kind']}/${event['subjectId']}': event['revision'],
    });
  }

  test(
    'identical event replay ignores object key order within page and after reopen',
    () {
      final reordered = {
        for (final entry in event.entries.toList().reversed)
          entry.key: entry.value,
      };
      store.applyUserPage({
        ...page,
        'events': [event, reordered],
      });
      expectCanonical();
      reopen();
      store.applyUserPage({
        ...page,
        'events': [reordered],
      });
      expectCanonical();
      final db = sqlite3.open(path);
      try {
        expect(db.select('SELECT * FROM user_events'), hasLength(1));
      } finally {
        db.close();
      }
    },
  );

  test(
    'canonical same-event revision mutation rolls back state and cursor across pages and reopen',
    () {
      store.applyUserPage(page);
      final changed = withEvents([
        {...event, 'revision': 2},
      ]);
      expect(() => store.applyUserPage(changed), throwsStateError);
      expectCanonical();
      reopen();
      expect(() => store.applyUserPage(changed), throwsStateError);
      expectCanonical();
      store.applyUserPage(page);
      expectCanonical();
    },
  );

  for (final mutation in <String, Object?>{
    'cursor': 'changed-event-cursor',
    'kind': 'membership.changed',
    'subjectId': other,
  }.entries) {
    test(
      'same event identity rejects changed ${mutation.key} after reopen',
      () {
        store.applyUserPage(page);
        reopen();
        expect(
          () => store.applyUserPage(
            withEvents([
              {...event, mutation.key: mutation.value},
            ]),
          ),
          throwsStateError,
        );
        expectCanonical();
      },
    );
  }

  test(
    'conflicting identity within a page rolls back the first event and persists nothing',
    () {
      expect(
        () => store.applyUserPage(
          withEvents([
            event,
            {...event, 'revision': 2},
          ]),
        ),
        throwsStateError,
      );
      reopen();
      expect(store.userState, isEmpty);
      expect(store.userCursor, '0');
      // A changed payload can now commit: the rolled-back first event left no identity.
      store.applyUserPage(
        withEvents([
          {...event, 'revision': 2},
        ]),
      );
      expect(store.userState, {'${event['kind']}/${event['subjectId']}': 2});
    },
  );

  test(
    'later conflict rolls back prior new event identity and materialization in the same page',
    () {
      store.applyUserPage(page);
      final newEvent = {...event, 'eventId': newEventId, 'subjectId': other};
      expect(
        () => store.applyUserPage(
          withEvents([
            newEvent,
            {...event, 'revision': 2},
          ]),
        ),
        throwsStateError,
      );
      reopen();
      expectCanonical();
      store.applyUserPage({
        ...page,
        'events': [
          {...newEvent, 'revision': 3},
        ],
        'nextCursor': 'new-cursor',
      });
      expect(store.userState, {
        '${event['kind']}/${event['subjectId']}': 1,
        '${event['kind']}/$other': 3,
      });
      expect(store.userCursor, 'new-cursor');
    },
  );

  test(
    'fault between materialization and cursor commit also rolls back event identity',
    () {
      final db = sqlite3.open(path);
      try {
        db.execute(
          "CREATE TRIGGER cursor_failure BEFORE UPDATE ON account BEGIN SELECT RAISE(ABORT,'fixture failure'); END",
        );
        expect(
          () => store.applyUserPage(page),
          throwsA(isA<SqliteException>()),
        );
        expect(store.userState, isEmpty);
        expect(store.userCursor, '0');
        expect(db.select('SELECT * FROM user_events'), isEmpty);
        db.execute('DROP TRIGGER cursor_failure');
      } finally {
        db.close();
      }
      reopen();
      store.applyUserPage(
        withEvents([
          {...event, 'revision': 2},
        ]),
      );
      reopen();
      expect(store.userState, {'${event['kind']}/${event['subjectId']}': 2});
      expect(store.userCursor, 'conflicting-cursor');
      expect(() => store.applyUserPage(page), throwsStateError);
    },
  );

  test(
    'two already-open connections observe committed event identity before applying their pages',
    () {
      final second = LocalStore.open(path, account);
      try {
        store.applyUserPage(page);
        expect(
          () => second.applyUserPage(
            withEvents([
              {...event, 'revision': 2},
            ]),
          ),
          throwsStateError,
        );
        expect(second.userCursor, page['nextCursor']);
        expect(second.userState, store.userState);
        second.applyUserPage(page);
        expectCanonical();
      } finally {
        second.close();
      }
    },
  );
}
