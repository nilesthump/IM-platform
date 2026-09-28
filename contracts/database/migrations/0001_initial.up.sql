CREATE TABLE users (
    user_id uuid PRIMARY KEY,
    username text NOT NULL UNIQUE,
    display_name text NOT NULL,
    password_hash text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (length(username) > 0),
    CHECK (length(password_hash) > 0)
);

-- The slot row is replaced atomically on login: session_id rotates and epoch rises.
CREATE TABLE sessions (
    user_id uuid NOT NULL REFERENCES users(user_id),
    client_type text NOT NULL CHECK (client_type IN ('WEB', 'DESKTOP', 'MOBILE')),
    session_id uuid NOT NULL UNIQUE,
    session_epoch bigint NOT NULL CHECK (session_epoch > 0),
    refresh_token_hash text,
    status text NOT NULL CHECK (status IN ('ACTIVE', 'REVOKED')),
    device_id text NOT NULL,
    expires_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, client_type),
    CHECK (status <> 'ACTIVE' OR refresh_token_hash IS NOT NULL)
);

CREATE TABLE conversations (
    conversation_id uuid PRIMARY KEY,
    kind text NOT NULL CHECK (kind IN ('DIRECT', 'GROUP')),
    direct_user_low_id uuid REFERENCES users(user_id),
    direct_user_high_id uuid REFERENCES users(user_id),
    next_seq bigint NOT NULL DEFAULT 1 CHECK (next_seq > 0),
    created_by uuid NOT NULL REFERENCES users(user_id),
    group_create_request_id uuid,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK ((kind = 'DIRECT' AND direct_user_low_id IS NOT NULL AND direct_user_high_id IS NOT NULL
            AND direct_user_low_id < direct_user_high_id AND group_create_request_id IS NULL)
        OR (kind = 'GROUP' AND direct_user_low_id IS NULL AND direct_user_high_id IS NULL)),
    UNIQUE (conversation_id, direct_user_low_id, direct_user_high_id),
    UNIQUE (direct_user_low_id, direct_user_high_id),
    UNIQUE (created_by, group_create_request_id)
);

CREATE TABLE friendships (
    user_low_id uuid NOT NULL REFERENCES users(user_id),
    user_high_id uuid NOT NULL REFERENCES users(user_id),
    direct_conversation_id uuid NOT NULL UNIQUE,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_low_id, user_high_id),
    CHECK (user_low_id < user_high_id),
    FOREIGN KEY (direct_conversation_id, user_low_id, user_high_id)
        REFERENCES conversations(conversation_id, direct_user_low_id, direct_user_high_id)
);

CREATE TABLE conversation_members (
    conversation_id uuid NOT NULL REFERENCES conversations(conversation_id),
    user_id uuid NOT NULL REFERENCES users(user_id),
    role text NOT NULL CHECK (role IN ('OWNER', 'MEMBER')),
    joined_at timestamptz NOT NULL DEFAULT now(),
    left_at timestamptz,
    PRIMARY KEY (conversation_id, user_id)
);

CREATE TABLE plugin_artifacts (
    plugin_id text NOT NULL,
    version text NOT NULL,
    package_hash text NOT NULL,
    backend_hash text NOT NULL,
    renderer_hash text NOT NULL,
    manifest jsonb NOT NULL,
    status text NOT NULL CHECK (status IN ('UPLOADED', 'VALIDATING', 'VERIFIED', 'REJECTED')),
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (plugin_id, version),
    CHECK (length(plugin_id) > 0 AND length(version) > 0),
    CHECK (length(package_hash) > 0 AND length(backend_hash) > 0 AND length(renderer_hash) > 0)
);

CREATE FUNCTION reject_plugin_artifact_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF (OLD.plugin_id, OLD.version, OLD.package_hash, OLD.backend_hash, OLD.renderer_hash, OLD.manifest)
       IS DISTINCT FROM
       (NEW.plugin_id, NEW.version, NEW.package_hash, NEW.backend_hash, NEW.renderer_hash, NEW.manifest) THEN
        RAISE EXCEPTION 'plugin artifact identity and bytes are immutable';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER plugin_artifact_immutable BEFORE UPDATE ON plugin_artifacts
    FOR EACH ROW EXECUTE FUNCTION reject_plugin_artifact_mutation();

CREATE FUNCTION reject_plugin_artifact_delete() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'plugin artifact versions cannot be deleted';
END $$;
CREATE TRIGGER plugin_artifact_no_delete BEFORE DELETE ON plugin_artifacts
    FOR EACH ROW EXECUTE FUNCTION reject_plugin_artifact_delete();

CREATE TABLE plugin_instances (
    conversation_id uuid NOT NULL REFERENCES conversations(conversation_id),
    plugin_id text NOT NULL,
    active_version text,
    desired_version text,
    previous_version text,
    status text NOT NULL CHECK (status IN ('INSTALLING', 'ENABLED', 'DISABLED', 'INSTALL_FAILED', 'AUTO_DISABLED', 'UNINSTALLED', 'RETAINED', 'PURGED')),
    grants jsonb NOT NULL DEFAULT '{}'::jsonb,
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (conversation_id, plugin_id),
    FOREIGN KEY (plugin_id, active_version) REFERENCES plugin_artifacts(plugin_id, version),
    FOREIGN KEY (plugin_id, desired_version) REFERENCES plugin_artifacts(plugin_id, version),
    FOREIGN KEY (plugin_id, previous_version) REFERENCES plugin_artifacts(plugin_id, version)
);

CREATE TABLE plugin_kv (
    conversation_id uuid NOT NULL,
    plugin_id text NOT NULL,
    key text NOT NULL,
    value jsonb NOT NULL,
    schema_version integer NOT NULL CHECK (schema_version > 0),
    PRIMARY KEY (conversation_id, plugin_id, key),
    FOREIGN KEY (conversation_id, plugin_id) REFERENCES plugin_instances(conversation_id, plugin_id)
);

CREATE TABLE messages (
    server_message_id uuid PRIMARY KEY,
    conversation_id uuid NOT NULL REFERENCES conversations(conversation_id),
    sender_id uuid NOT NULL REFERENCES users(user_id),
    request_id uuid NOT NULL,
    seq bigint NOT NULL CHECK (seq > 0),
    kind text NOT NULL CHECK (kind IN ('TEXT', 'PLUGIN')),
    text_body text,
    plugin_id text,
    plugin_version text,
    fallback_text text,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (conversation_id, request_id),
    UNIQUE (sender_id, conversation_id, request_id),
    UNIQUE (conversation_id, seq),
    UNIQUE (server_message_id, conversation_id),
    FOREIGN KEY (plugin_id, plugin_version) REFERENCES plugin_artifacts(plugin_id, version),
    CHECK ((kind = 'TEXT' AND text_body IS NOT NULL AND plugin_id IS NULL AND plugin_version IS NULL)
        OR (kind = 'PLUGIN' AND plugin_id IS NOT NULL AND plugin_version IS NOT NULL AND fallback_text IS NOT NULL))
);

CREATE TABLE outbox_events (
    event_id uuid PRIMARY KEY,
    aggregate_type text NOT NULL,
    aggregate_id uuid NOT NULL,
    event_type text NOT NULL,
    conversation_id uuid REFERENCES conversations(conversation_id),
    message_id uuid,
    payload jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    published_at timestamptz,
    attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    FOREIGN KEY (message_id, conversation_id) REFERENCES messages(server_message_id, conversation_id),
    CHECK ((event_type = 'message.created' AND message_id IS NOT NULL AND conversation_id IS NOT NULL)
        OR (event_type <> 'message.created' AND message_id IS NULL))
);
CREATE UNIQUE INDEX outbox_one_message_created ON outbox_events(message_id) WHERE event_type = 'message.created';
CREATE INDEX outbox_unpublished ON outbox_events(created_at, event_id) WHERE published_at IS NULL;

CREATE TABLE user_sync_events (
    user_id uuid NOT NULL REFERENCES users(user_id),
    cursor_id bigint GENERATED ALWAYS AS IDENTITY,
    event_type text NOT NULL CHECK (event_type IN ('friend.changed', 'conversation.changed', 'membership.changed', 'plugin.changed', 'session.revoked')),
    payload jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, cursor_id)
);
