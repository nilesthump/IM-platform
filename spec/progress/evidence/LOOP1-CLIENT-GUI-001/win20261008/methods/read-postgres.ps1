param([ValidateSet('before-retry','after-retry','reconnected')][string]$Phase='before-retry')
$ErrorActionPreference='Stop'
$docker='C:/Program Files/Docker/Docker/resources/bin/docker.exe';$project='im-gui-product-20261004-18484';$root='H:/.codex/worktrees/g/IM-platform';$work='H:/.codex/gui-handoffs/20261004-4f866046/gui-runtime/go-18484'
$taskIds=@(& $docker ps -q --filter "label=com.docker.compose.project=$project" --filter 'label=com.docker.compose.service=postgres');if($LASTEXITCODE -ne 0 -or $taskIds.Count -ne 1){throw 'Owned Postgres absent/nonunique'}
$taskDb=(& $docker inspect $taskIds[0] | ConvertFrom-Json)[0];if($LASTEXITCODE -ne 0 -or $taskDb.Config.Labels.'com.docker.compose.project' -ne $project){throw 'Owned Postgres labels mismatch'}
$env:IM_HTTPS_PORT='8443';$env:IM_GO_CONFIG_DIR="$work/config";$env:COMPOSE_PROGRESS='quiet'
$taskQuery=@"
SELECT COALESCE(json_agg(x),'[]'::json) FROM (SELECT m.server_message_id,m.request_id,m.seq,m.sender_id,m.conversation_id,m.text_body,m.created_at,(SELECT count(*) FROM outbox_events o WHERE o.message_id=m.server_message_id AND o.event_type='message.created') AS outbox_count FROM messages m WHERE m.conversation_id='3511b34b-4d5d-46e9-a32e-e936eca78fce' AND m.sender_id='4dada728-e56b-48a0-a84c-d8ae88507adc' AND m.text_body IN ('Windows native SEND 20261008-1220-owned-79ec62c','Windows native RETRY 20261008-1222-owned-79ec62c') ORDER BY m.seq) x;
"@
$taskRows= & $docker compose -f "$root/deploy/compose.yaml" -f "$work/override.yaml" -p $project --profile go exec -T postgres psql -U im -d im -v ON_ERROR_STOP=1 -Atc $taskQuery
if($LASTEXITCODE -ne 0){throw 'Owned read-only message query failed'}
@{time=(Get-Date).ToString('o');phase=$Phase;project=$project;only_controlled_messages=$true;read_only_query=$true;rows=@($taskRows|ConvertFrom-Json)}|ConvertTo-Json -Depth 6|Set-Content ("H:/.codex/gui-handoffs/20261008-ca-desktop/postgres-$Phase.json") -Encoding UTF8
'Owned actual Postgres message and outbox rows saved'
