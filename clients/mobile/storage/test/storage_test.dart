import 'dart:io';
import 'package:plugworld_mobile_storage/storage.dart';
import 'package:test/test.dart';

void main() {
  test('mobile uses persistent isolated native account storage', () {
    final directory = Directory.systemTemp.createTempSync('plugworld-mobile-');
    const account = '10000000-0000-4000-8000-000000000001';
    const other = '10000000-0000-4000-8000-000000000002';
    const conversation = '30000000-0000-4000-8000-000000000001';
    const request = '40000000-0000-4000-8000-000000000001';
    var a = openAccountStorage(directory.path, account);
    final b = openAccountStorage(directory.path, other);
    try {
      a.localSend(conversation, request, account, 'persist');
      a.close();
      a = openAccountStorage(directory.path, account);
      expect(a.item(conversation, request)!['state'], 'SENDING');
      expect(b.item(conversation, request), isNull);
    } finally {
      a.close();
      b.close();
      directory.deleteSync(recursive: true);
    }
  });
}
