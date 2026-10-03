# Bounded local GUI fixture trust proposal — pending Human approval

This proposal changes test-host trust temporarily. No trust has been installed. Local compilation and unauthenticated UI verification continue. Production client TLS verification and hostname checking remain enabled; no client trust bypass, network library, manifest exception or production APK special trust configuration is proposed.

## Exact owned fixture

- Owner: `/root/gui_product_implementation`; task `LOOP1-CLIENT-GUI-001`.
- Endpoint: `https://localhost:18443`, loopback-only host listener; Android reaches exactly this endpoint through `adb -s emulator-5590 reverse tcp:18443 tcp:18443`.
- Private material: `H:/IM-platform/.git/worktrees/IM-platform3/gui-runtime/tls-v2/`, ACL restricted to current user and SYSTEM. The CA signing key was never persisted; only the runtime server leaf key remains. Private keys remain outside Git, screenshots, command arguments and product evidence. No user credentials are used. Controlled fixture accounts are explicitly labelled; fixture ACKs do not prove server durability. The original unconstrained CA was never installed and its signing key was removed; its earlier public fingerprints remain in original Recorder output and are superseded by this v2 proposal.
- CA subject: `IM GUI owned fixture 20261004`, RSA 2048/SHA256, CA path length zero, critical NameConstraints limited to DNS `localhost` and IP `127.0.0.1/32`. Leaf SAN: `localhost`, `127.0.0.1`; server-auth only. Android CA filename: `132339d5.0`, after verifying no existing hash collision.
- CA SHA256 DER fingerprint: `e61a24364dc95315cbdf10bb6eade27b907ff94adb71bde1c827f93a48ad0de8`.
- Windows SHA1 thumbprint: `7a9b96e977ceed8db1494467cb770121746e481a`.
- Leaf SHA256: `cf3ad5a52e014c2d5e6b8462e425443f08654f82c6b272203a2866997a25eb6e`.
- Expiry: `2026-10-04T19:20:46.586064Z`. Generation only is recorded by the Recorder; no store installation has occurred.

## Windows operation requested

Import only the matching public `ca.der` into `Cert:/CurrentUser/Root`. Before import, verify SHA256, expiry and absence of this exact thumbprint. Record the baseline thumbprint set without exporting certificates or private user files. Do not alter LocalMachine stores. Use the normal installed client and its OS TLS trust; collect positive hostname-valid login/refresh and negative untrusted/hostname-mismatch checks. Remove only this newly imported thumbprint afterwards, compare the Root set to baseline and verify the client rejects the fixture again. Root changes affect other processes under this user while the fixture CA is installed, which is why explicit approval is requested.

## Android operation requested

Only the existing task-owned AVD `IMClientSend34` at `H:/IM-platform/.git/worktrees/IM-platform4/send-runtime/avd-home/IMClientSend34.avd`, serial `emulator-5590`, API34 `userdebug`. The personal Pixel AVD and shared Android SDK system-image files remain untouched. Current image supports `nsenter`/`mount`, `ro.debuggable=1`; both `/apex/com.android.conscrypt/cacerts` and `/system/etc/security/cacerts` exist. Android 14 uses the Conscrypt APEX trust directory, so installing a user CA alone is insufficient.

After approval: capture baseline certificate filenames/hashes and mount records in this AVD; `adb root` only for this serial; copy the original public system CA set into an owned `/data/local/tmp/im-gui-ca` directory and add only the approved public certificate under its OpenSSL old-subject-hash filename. Bind-mount this preserved set read-only over `/apex/com.android.conscrypt/cacerts` in the owned emulator init and zygote mount namespaces using `nsenter`, keeping SELinux enforcing. Force-stop/restart only `im.platform.client` so its fresh process inherits the test system trust view. Verify the exact added hash is visible from its mount namespace and use the unmodified APK's default `HttpsURLConnection` verification. No system partition write, verified-boot disable, persistent property, SELinux disable, APEX replacement or APK TLS exception is authorized by this proposal. If the read-only bind operation is rejected by the image, stop this affected proof and report the exact result rather than broadening security changes.

Rollback: stop the owned app, unmount each recorded overlay, remove the exact task-created temporary certificate directory and reverse mapping, then reboot only this AVD without saving a modified snapshot. Verify baseline CA filenames/hashes restored in the fresh app namespace, default TLS rejects the fixture, `ro.debuggable`/SELinux mode unchanged and `adb unroot`. Preserve existing AVD user data; no wipe. Unexpected rollback failure is a blocker and must be reported.

## Proof limits and recovery

These are controlled GUI integration fixtures, distinct from Go/PostgreSQL/NATS accepted runtime regressions. Screenshots must bind the actual candidate SHA, package/APK hash, API/platform, exact state, theme/font/density and fixture steps. No final Architect approval or unified technical acceptance is claimed. Existing accepted Send/Sync regression mechanisms continue unchanged.

Authority references: [AOSP Conscrypt](https://source.android.com/docs/core/ota/modular-system/conscrypt), [AOSP TrustedCertificateStore source](https://android.googlesource.com/platform/external/conscrypt/+/master/platform/src/main/java/org/conscrypt/TrustedCertificateStore.java). The runtime mount proposal is an explicitly bounded test-host operation, not a product architecture change.
