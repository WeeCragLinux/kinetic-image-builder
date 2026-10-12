# kineticos-plus

A modular bootc image based on `ghcr.io/theblack-don/kineticos:nvidia`.
Small always-on core, everything else opt-in: enable the modules you want,
comment out the apps you don't.

Built with [dcli-bootc](https://copr.fedorainfracloud.org/coprs/theblackdon/dcli-bootc).
`build_files/build.sh` is generated — edit `modules/*.yaml`, then run
`dcli-bootc gen`.

## Configure (GUI)

Instead of editing the YAML by hand, run the configurator from the project folder:

```bash
./kinetic-configurator
```

It asks for a base image (`kineticos:default` for AMD, `:nvidia` for Turing and newer
NVIDIA cards, `:nvidia-legacy` for older NVIDIA cards), then walks through each module
in `profile.yaml` order and lets you pick its apps. `base`, `rpmfusion` and `terra` are
on by default. Selecting an app turns its module on. When it finishes, it writes
`profile.yaml` and `modules/*.yaml` and runs `dcli-bootc gen`.

Requires PySide6 (`python3 -c "import PySide6"` should work).

## Build

```bash
dcli-bootc gen
dcli-bootc build
```

To use it on a machine, rebase/switch to the built image with `bootc`
(follow your current system's rebase procedure; keep a known-good
deployment pinned so you can roll back).

## Modules

Toggle in `profile.yaml` under `enabled_modules:` (comment a line out to
disable that whole module). Order matters: `base` first, `rpmfusion`
before anything needing it.

| Module | Contents | Needs `rpmfusion`? |
|---|---|---|
| `base` | tmux, dcli-bootc, Spotify flatpak, update timer. Always on. | no |
| `rpmfusion` | RPMFusion free + nonfree repos. Leave on unless minimal. | — (it *is* the repos) |
| `browsers` | helium, chromium, firefox, brave-browser, brave-origin, vivaldi | brave/vivaldi need their own repo setup (in-module); discord-style n/a |
| `content` | obs-studio, audacity, kdenlive, gimp, pavucontrol, easyeffects, vlc, mpv | yes (vlc, mpv) |
| `gaming` | prismlauncher, mangohud, goverlay; steam, lutris commented out | yes (if steam uncommented) |
| `comms` | telegram, thunderbird, discord (commented) | yes (if discord uncommented) |
| `terminals` | kitty, konsole | no |
| `dev` | zed, opencode (via install script) | no |
| `lgl-tools` | LGL System Loadout, Colour Picker, DNF Helper, Emoji Picker, Keychron Helper, Papercutter, Scheduler Manager | no (Scheduler Manager also needs `scx-tools` and `scx-scheds` from `bieszczaders/kernel-cachyos-addons`) |

## The usr-overlay (kinpkg) — not used here, but good to know

`dcli-bootc` has a second install mechanism besides modules: the
**usr-overlay**, managed by `kinpkg`. Overlay packages live in a
`modules/overlay-packages.yaml` list (wired via `overlay_module:` /
`overlay_backend:` in `profile.yaml`) and are populated with
`dcli-bootc overlay import` from the base image's own overlay.
Removing one from the list runs `kinpkg remove` on next build/update.
Its purpose is tracking packages the *base image* ships (this repo used
to carry `chromium` and `easyeffects` that way) so your customizations
survive base updates without whiteout conflicts — `build.sh` snapshots
the base package set for exactly this safety.

This repo deliberately doesn't use it: every app comes through regular
dnf modules (one mechanism, `chromium` via `browsers.yaml`,
`easyeffects` via `content.yaml`). If you ever want it back, recreate
`modules/overlay-packages.yaml`, restore the two `overlay_*` keys in
`profile.yaml`, and run `dcli-bootc overlay import` + `dcli-bootc gen`.

## Enable / disable apps

Inside each `modules/*.yaml`, lines starting with `# -` are disabled.
Uncomment the package line to install it; comment it to drop it:

```yaml
packages:
 - mpv
 # - vlc
```

Some apps need their repo lines toggled alongside the package (brave,
vivaldi) — the comments in each file say which lines belong together.
After any change, re-run `dcli-bootc gen` before building.

## Base image variants (stable / legacy Nvidia)

Default is the `:nvidia` tag (`profile.yaml` → `base_image:`). For a
different Kineticos stream, change that one line:

```yaml
base_image: ghcr.io/theblack-don/kineticos:stable
```

`profile.yaml` also has an `nvidia_base_image:` key (currently `null`).
Its exact semantics depend on your dcli-bootc version — check
`dcli-bootc gen --help` on your build host before relying on it; the
one-line `base_image:` edit above always works regardless.

## Extras

- **fastfetch config (opt-in):** `files/fastfetch-config.jsonc` is *not*
  baked into the image. After booting, run from a repo checkout:
  ```bash
  bash scripts/apply-fastfetch-config.sh        # your ~/.config only
  bash scripts/apply-fastfetch-config.sh --system  # also /etc default (needs sudo)
  ```
  The script also offers bash auto-run in new terminals.
- **Flatpaks:** listed under `flatpaks:` per module (see Spotify in `base`).
