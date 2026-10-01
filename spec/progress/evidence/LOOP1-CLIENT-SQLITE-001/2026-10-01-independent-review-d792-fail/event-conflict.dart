import 'dart:io';
import 'dart:convert';
import 'package:plugworld_local_store/local_store.dart';
void main() {
 final fixture=jsonDecode(File('contracts/fixtures/sync-plugin/golden.json').readAsStringSync());
 final c=(fixture['cases'] as List).firstWhere((c)=>c['id']=='user-friend.changed');
 final page=Map<String,Object?>.from(c['steps'][0]['page']);
 final events=page['events'] as List;
 final original=Map<String,Object?>.from(events.first);
 final temp=Directory.systemTemp.createTempSync('independent-event-conflict-');
 final store=LocalStore.open('${temp.path}/a.sqlite','10000000-0000-4000-8000-000000000001');
 try {
 store.applyUserPage(page);
 print('before: ${store.userCursor} ${store.userState}');
 final changed={...original,'revision':(original['revision'] as int)+1};
 try { store.applyUserPage({...page,'events':[changed],'nextCursor':'conflicting-cursor'}); print('ACCEPTED conflicting same eventId: ${store.userCursor} ${store.userState}'); }
 catch(e) {print('REJECTED: $e');}
 } finally {store.close();temp.deleteSync(recursive:true);}
}
