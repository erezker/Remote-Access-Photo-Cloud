# Security model and publication checklist

## Trust boundaries

- **Tailscale** protects access to devices that belong to the authorized tailnet. Use least-privilege ACL/grants and MFA for the login identity.
- **RDP** still requires valid Windows credentials. Do not port-forward Windows Remote Desktop (RDP) from the public internet.
- **Android SSH relay** accepts a key-authenticated connection and transmits a WoL magic packet on the local LAN. A WoL packet itself has no authentication: secure the **relay** rather than treating WoL as an authenticated remote command.
- **Tailscale Serve** adds HTTPS for Immich inside the tailnet. **Funnel is different:** it exposes a service publicly and is not part of this design.
- **Immich API key** belongs only in the local ImmiBridge settings. Start with limited upload/read/album permissions and add any extra permission only when confirmed necessary.
- **Immich storage:** Photos on external NTFS disk; PostgreSQL on Docker-managed Linux-compatible storage. A working app is not equivalent to a verified backup.

## Special concern: older Android relay

An old phone may not receive security patches. Its device access should be limited, it should not have unnecessary public services, and Tailscale access should be scoped to the devices that actually need it. SSH key-only access is strongly preferred; after confirming keys work, disable password authentication in Termux's `sshd_config` and restart `sshd`. Avoid exposing port 8022 on the router. Verify the phone remains connected after reboot and battery optimization does not disable it.

## Secrets and potentially identifying details

Never commit:

- personal email addresses or usernames (including real Termux account names);
- real machine names, tailnet DNS names, public/private IP addresses, MAC addresses, or router screenshots;
- private SSH keys, host keys, key passphrases, certificates, or Tailscale auth keys;
- Immich API keys, database passwords, Docker `.env`, ImmiBridge local profiles, or exported server settings;
- photos/videos, thumbnails, Apple Photos libraries, and application databases.

**Only the SSH public key** may be distributed to a trusted relay (via a secure transfer); do not commit it here. A public key is not secret, but may include an identifying comment.

The `.gitignore` excludes common local-secret files. **This is not a substitute for reviewing staged changes.** Before publishing:

```bash
python3 tools/check_public_repo.py
git status --short
git diff --cached --check
git diff --cached
```

A secret scanner may miss uncommon encodings or formats. Inspect git history as well: adding `.gitignore` later does not remove secrets already committed. If a secret was committed, rotate it and purge the repository history before publishing.

## HTTPS and domain-name privacy

TLS via Tailscale Serve secures the browser-to-Serve hop as well as the Tailscale encrypted path. HTTPS certificates can disclose a device's tailnet DNS **name** through public certificate-transparency logs. Avoid using personally revealing device names and don't place the actual host name in this public repository.

## Reliability / data protection

1. Keep separate, periodically tested backups of (a) Immich media, (b) PostgreSQL/database state, and (c) the original Apple Photos library while migration is being validated.
2. An external disk can fail; the same disk connected to Windows cannot serve as its own independent backup.
3. Before changing Immich versions or volumes, read the upstream migration/backup instructions.
4. Avoid putting PostgreSQL directly on an NTFS bind mount in Windows. See [Immich requirements](https://docs.immich.app/install/requirements/).
5. Reboot tests should verify Docker Desktop starts, the external drive mounts with the expected drive letter, Tailscale connects, and Immich serves requests.
6. Keep ImmiBridge in Smart incremental mode during pilot; do not use Mirror until deletion behavior is understood.

## Network-hardening option

If all Immich access is through Tailscale Serve, consider binding the Immich Docker published port to **loopback** rather than all Windows interfaces. In the upstream Compose file, replace its public host port binding with `localhost:2283:2283` only after reviewing the current official Compose layout and verifying that Serve still reaches it. Test access through HTTPS and local web UI after restarting the stack. No public router port forwarding is required.

## Source references

- [Tailscale Serve](https://tailscale.com/docs/reference/tailscale-cli/serve)
- [Tailscale Serve security and scope](https://tailscale.com/docs/features/tailscale-serve)
- [Immich requirements](https://docs.immich.app/install/requirements/)
- [Immich backup and restore](https://docs.immich.app/administration/backup-and-restore/)
