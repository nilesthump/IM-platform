import 'dart:io';
import 'dart:convert';
import 'package:plugworld_local_store/local_store.dart';
import 'package:sqlite3/sqlite3.dart';
void require(bool condition, String label) { if (!condition) throw StateError(label); }
void main() {
 final fixture=jsonDecode(File('contracts/fixtures/sync-plugin/golden.json').readAsStringSync());
 final c=(fixture['cases'] as List).firstWhere((c)=>c['id']=='user-friend.changed');
 final page=Map<String,Object?>.from(c['steps'][0]['page']);
 final original=Map<String,Object?>.from((page['events'] as List).first);
 final temp=Directory.systemTemp.createTempSync('independent-fixed-event-conflict-');
 final path='${temp.path}/a.sqlite';
 var store=LocalStore.open(path,'10000000-0000-4000-8000-000000000001');
 try {
  store.applyUserPage(page);
  final priorCursor=store.userCursor;
  final priorState=jsonEncode(store.userState);
  final changed={...original,'revision':(original['revision'] as int)+1};
  bool rejected=false;
  try { store.applyUserPage({...page,'events':[changed],'nextCursor':'conflicting-cursor'}); }
  on StateError catch(e) { rejected=true; print('Exact prior mutation REJECTED: $e'); }
  require(rejected,'Prior canonical mutation must reject');
  require(store.userCursor==priorCursor && jsonEncode(store.userState)==priorState,'Prior state/cursor changed');
  store.close();
  store=LocalStore.open(path,'10000000-0000-4000-8000-000000000001');
  require(store.userCursor==priorCursor && jsonEncode(store.userState)==priorState,'Reopen state/cursor changed');
  final db=sqlite3.open(path);
  try {
   final priorIds=jsonEncode(db.select('SELECT * FROM user_events').map((r)=>Map<String,Object?>.from(r)).toList());
   db.execute("CREATE TRIGGER identity_failure BEFORE INSERT ON user_events WHEN NEW.event_id='50000000-0000-4000-8000-000000000098' BEGIN SELECT RAISE(ABORT,'independent identity insert failure'); END");
   final first={...original,'eventId':'50000000-0000-4000-8000-000000000097','subjectId':'10000000-0000-4000-8000-000000000002'};
   final fault={...original,'eventId':'50000000-0000-4000-8000-000000000098','subjectId':'10000000-0000-4000-8000-000000000003'};
   bool rolledBack=false;
   try {store.applyUserPage({...page,'events':[first,fault],'nextCursor':'insert-failure-cursor'});}
   on SqliteException catch(e) {rolledBack=true; print('Actual SQLite identity INSERT fault REJECTED: $e');}
   require(rolledBack,'Fault injection did not execute');
   require(store.userCursor==priorCursor && jsonEncode(store.userState)==priorState,'Earlier page effects survived identity fault');
   require(jsonEncode(db.select('SELECT * FROM user_events').map((r)=>Map<String,Object?>.from(r)).toList())==priorIds,'Earlier identity survived rollback');
   db.execute('DROP TRIGGER identity_failure');
   store.applyUserPage({...page,'events':[{...first,'revision':3}],'nextCursor':'retry-after-rollback'});
   require(store.userState['${first['kind']}/${first['subjectId']}']==3,'Rolled-back identity prevents retry');
   print('PASS prior mutation/reopen unchanged; identity insert failure rolls back earlier event identity/state/cursor; changed retry commits');
  } finally {db.close();}
 } finally {store.close();temp.deleteSync(recursive:true);}
}
