import 'package:plugworld_local_store/local_store.dart';
export 'package:plugworld_local_store/local_store.dart' show LocalStore;

/// Native mobile account storage; the app supplies its private data directory.
LocalStore openAccountStorage(String privateDirectory, String accountId) =>
    LocalStore.openAccount(privateDirectory, accountId);
