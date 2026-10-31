# Operations, onboarding, and troubleshooting

All values such as `WINDOWS_DEVICE`, `YOUR_TAILNET`, `TERMUX_USER`, `EXTERNAL_DRIVE`, and `ETHERNET_MAC` are **placeholders**. Never replace them in the public repository. Replace them only in local files explicitly ignored by Git.

## Windows: start, test, and stop Immich

Open PowerShell on the Windows desktop:

```powershell
# Use the local installation directory established by the operator.
Set-Location C:\Immich
docker compose config -q
docker compose up -d
docker compose ps
```

Or use the supplied helper scripts after reviewing their paths:

```powershell
.\scripts\windows\Start-Immich.ps1 -ImmichDir 'C:\Immich'
.\scripts\windows\Check-Immich.ps1 -ImmichDir 'C:\Immich'
```

To stop safely:

```powershell
Set-Location C:\Immich
docker compose stop
```

**Do not use `docker compose down -v`**: the `-v` option removes named volumes, which can include the Immich database.

To check Tailscale HTTPS from Windows:

```powershell
tailscale serve status
```

To enable the private HTTPS proxy if not yet enabled:

```powershell
tailscale serve --bg 2283
```

Only use `serve`, not `funnel`. This remains private to the authorized tailnet.

### External disk sanity check

- Ensure the Windows media disk is connected and retains its expected drive letter.
- Check the local `UPLOAD_LOCATION` in the private Immich `.env`.
- Upload **one expendable** photo through Immich and verify the file was written under the intended media folder.
- Do not directly move or rename Immich-managed files in that folder.

## Mac → Android SSH relay → Wake-on-LAN

### On the Android / Termux device

```sh
pkg update
pkg install openssh python
mkdir -p "$HOME/.config/remote-photo-cloud" "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
touch "$HOME/.ssh/authorized_keys"
chmod 600 "$HOME/.ssh/authorized_keys"
sshd
```

Place the **Mac's SSH public key**, not its private key, into `~/.ssh/authorized_keys` using a trusted method. After key login works, set `PasswordAuthentication no` and `KbdInteractiveAuthentication no` in Termux SSH daemon configuration and restart `sshd`. Termux's SSH daemon commonly listens on port **8022**.

From the **Mac** repository directory, copy the program files to Termux (the alias must be configured first):

```bash
scp scripts/termux/wake_pc.py scripts/termux/wake_pc.sh config/wol.env.example android-wol:~/
```

On the **phone**, create its private environment file from the template (copy the template onto the phone using SCP or edit it locally):

```sh
cp "$HOME/wol.env.example" "$HOME/.config/remote-photo-cloud/wol.env"
chmod 600 "$HOME/.config/remote-photo-cloud/wol.env"
chmod 700 "$HOME/wake_pc.sh"
```

Edit `wol.env` **only on the phone** and enter the real Ethernet interface MAC and suitable broadcast destination. A broadcast across different routed networks will normally not work; the Android relay must be on the same LAN as the sleeping desktop.

### On the Mac

Add the following example alias to `~/.ssh/config` **after filling the values locally**:

```sshconfig
Host android-wol
    HostName PHONE_TAILSCALE_DNS_NAME
    User TERMUX_USER
    Port 8022
    IdentityFile ~/.ssh/android_wol
    IdentitiesOnly yes
    AddKeysToAgent yes
    UseKeychain yes
```

Then test the private SSH connection:

```bash
ssh android-wol 'true'
```

And trigger WoL:

```bash
bash scripts/mac/wake-windows.sh
```

For a file you can double-click in Finder, you can create a local `.command` shortcut that invokes this script; don't commit shortcuts containing personal paths or hostnames.

**Phone reboot caveat:** Termux `sshd` may not restart automatically. Configure `Termux:Boot` if desired, and confirm battery/boot permissions and Tailscale connectivity after restarting Android.

## Mac: local placeholders and connectivity checks

```bash
cp config/mac.env.example config/mac.env.local
# Edit the ignored config/mac.env.local with YOUR OWN values.
bash scripts/mac/check-connections.sh
bash scripts/mac/check-photo-source.sh
```

The first script checks whether the HTTPS site and RDP port can be reached. The second checks that the **configured Apple Photos package exists**. Neither script uploads any photos or changes server settings.

## ImmiBridge setup and first import (not yet done)

1. Mount the Mac external drive holding the actual Photos library.
2. Open Apple Photos and verify the active library in **Settings → General → Library Location**. Make sure originals load.
3. In ImmiBridge choose Photos as the source and Immich as the destination. Use the HTTPS Tailscale Serve URL in local app settings and a locally generated least-privilege Immich API key.
4. Choose **Smart** incremental, **All** media, and **Originals**; consider **Both** if separately rendered edits are needed. Decide whether albums and hidden photos should be included.
5. Leave scheduled backup disabled for now. Run **Dry Run**, then test with a small selected album. Check originals, videos, Live Photos and timestamps in Immich.
6. After verifying output and backups, enable a recurring schedule while the Mac is awake and the Photos volume mounted. The Windows Docker services and Tailscale must also be online.

Mac's Apple Photos library stays authoritative during validation; Immich does **not** provide a native iCloud Photos replacement inside Apple's built-in Photos apps.

## Troubleshooting matrix

| Symptom | First checks |
|---|---|
| Mac cannot reach Windows RDP | Both devices online in Tailscale; Windows awake; RDP enabled; account password accepted; no public port forwarding needed |
| Remote wake fails | Termux SSH reachable; phone on Windows LAN; wake launcher executable; MAC and broadcast set locally; wired NIC/BIOS WoL enabled; phone battery optimization |
| Immich UI unavailable | Windows awake; Docker engine running; `docker compose ps`; correct external disk connected; `tailscale serve status` |
| Browser says connection is insecure | Use the HTTPS address issued by Tailscale Serve instead of a raw HTTP URL |
| ImmiBridge sees wrong library | Attach the Mac photo drive; verify library in Apple Photos; refresh the library source; don't launch automatic backup yet |
| Some photos missing | Verify source volume mounted, library permissions, original file availability, filters and Dry Run output |
| Windows reboot but Immich unavailable | Docker Desktop may not start automatically on its own; confirm Docker engine and containers after sign-in |

## Backup/restore planning

Photos on an external drive and PostgreSQL metadata are **two separate backup targets**. Back up the photo/media directory and a consistent database backup to **another independent storage destination**. Follow the [official Immich backup/restore guide](https://docs.immich.app/administration/backup-and-restore/) instead of inventing ad-hoc database file copies.
