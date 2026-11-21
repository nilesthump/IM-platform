import assert from 'node:assert/strict';
import {join} from 'node:path';
import {setTimeout as delay} from 'node:timers/promises';
import {pathToFileURL} from 'node:url';

const [artifact, origin] = process.argv.slice(2);
const {WebClient} = await import(pathToFileURL(join(artifact, 'web/src/application/client.js')));
const clients = [];
function openClient() {
  const client = new WebClient(origin);
  clients.push(client);
  return client;
}

// The Web UI has no registration action. Bootstrap two disposable accounts with
// the canonical registration input; WebClient owns all subsequent protocol I/O.
async function register() {
  const username = 'parity' + crypto.randomUUID().replaceAll('-', '');
  const password = crypto.randomUUID();
  const response = await fetch(origin + '/v1/auth/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password, displayName: username})
  });
  assert.equal(response.status, 201);
  return {username, password, id: (await response.json()).user.userId};
}

async function until(label, predicate) {
  const deadline = Date.now() + 15000;
  while (!predicate()) {
    assert.ok(Date.now() < deadline, 'Timed out waiting for ' + label);
    await delay(50);
  }
}

async function exchange(alice, bob, conversation, text, senderId) {
  alice.open(conversation);
  bob.open(conversation);
  assert.equal(bob.view().selected, conversation);
  const request = alice.send(text);
  assert.ok(request);
  const rows = client => client.repository.snapshot(conversation).filter(row => row.requestId === request);
  await until('sender commit and receiver delivery', () =>
    [alice, bob].every(client => rows(client).some(row => row.state === 'SENT')));
  const [sent] = rows(alice);
  assert.equal(rows(alice).length, 1);
  assert.equal(rows(bob).length, 1);
  assert.deepEqual(rows(bob)[0], sent);
  assert.equal(sent.senderId, senderId);
  assert.equal(sent.content.text, text);
  assert.equal(sent.seq, 1n);
  await until('conversation Sync', () => bob.view().sync === '本页在线消息已同步 · 不补历史');
}

const failures = [];
try {
  const alice = openClient();
  const bob = openClient();
  const a = await register();
  const b = await register();
  await alice.login(a.username, a.password);
  await bob.login(b.username, b.password);
  await until('authenticated WSS and profile', () =>
    alice.view().user?.userId === a.id && bob.view().user?.userId === b.id &&
    [alice, bob].every(client => client.view().connection === 'ready'));
  await alice.search(b.username);
  assert.equal(alice.view().searchResults[0]?.userId, b.id);
  await alice.addFriend(b.id);
  const direct = alice.view().friends.find(friend => friend.user.userId === b.id)?.directConversationId;
  assert.ok(direct);
  await until('friend metadata Sync', () => bob.view().friends.some(friend =>
    friend.user.userId === a.id && friend.directConversationId === direct));
  await exchange(alice, bob, direct, 'direct parity', a.id);
  await alice.createGroup([b.id]);
  assert.equal(alice.view().groupStatus, 'success');
  const group = alice.view().selected;
  assert.ok(group && group !== direct);
  await until('group membership Sync', () => bob.view().groups.some(row =>
    row.kind === 'GROUP' && row.conversationId === group && row.member.user.userId === b.id));
  await exchange(alice, bob, group, 'group parity', a.id);
  await alice.logout();
  await bob.logout();
  for (const client of [alice, bob]) {
    assert.equal(client.view().session, false);
    assert.equal(client.view().notice, '已退出登录。');
  }
} catch (error) {
  failures.push(error);
}
for (const client of clients) {
  try {
    client.dispose();
  } catch (error) {
    failures.push(error);
  }
}
if (failures.length === 1) throw failures[0];
if (failures.length > 1) throw new AggregateError(failures, 'Web parity and client cleanup failures');
console.log('PASS unchanged WebClient login, friend, DIRECT, group, delivery, Sync and logout');
