import 'package:sqlite3/sqlite3.dart';
import 'package:test/test.dart';

void main() {
  test('loads the real native SQLite library', () {
    final db = sqlite3.openInMemory();
    try {
      expect(
        db.select('SELECT sqlite_version() AS version').single['version'],
        isNotEmpty,
      );
      db.execute('CREATE TABLE probe (value TEXT NOT NULL)');
      db.execute('INSERT INTO probe VALUES (?)', ['native']);
      expect(db.select('SELECT value FROM probe').single['value'], 'native');
    } finally {
      db.close();
    }
  });
}
