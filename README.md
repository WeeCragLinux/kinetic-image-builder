# kineticos-plus

A modular bootc image based on `ghcr.io/theblack-don/kineticos:stable` by default.
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

It asks for a base image (`kineticos:stable` for AMD, `:nvidia` for Turing and newer
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

LGL System Loadout's kernel-changing feature does not work with this bootc-based
image. Do not use it to switch kernels.

## Kineticos usr-overlay (kinpkg)

Kineticos provides the **usr-overlay** as a package-management layer alongside
the base image; it is a Kineticos feature, not a separate image variant. The
overlay is managed by `kinpkg`, which tracks overlay packages separately from
the base image's packages. During builds and updates, `kinpkg` reconciles the
overlay package set: packages added to the set are installed, and removed
packages are uninstalled. This lets overlay-managed customizations persist
across base-image updates while avoiding file conflicts with packages in the
base image.

## Enable / disable apps

You can choose apps with the GUI configurator (`./kinetic-configurator`), or
edit the module files manually. In each `modules/*.yaml`, lines starting with
`# -` are disabled; uncomment a package line to install it, or comment it out
to remove it:

```yaml
packages:
 - mpv
 # - vlc
```

Some apps need their repo lines toggled alongside the package (brave,
vivaldi) — the comments in each file say which lines belong together.
After any change, re-run `dcli-bootc gen` before building.

## Base image variants (stable / legacy Nvidia)

The default is `ghcr.io/theblack-don/kineticos:stable` for AMD and Intel GPUs.
Run `./kinetic-configurator` to select the variant that matches your GPU:
`:stable` for AMD and Intel, `:nvidia` for Turing and newer Nvidia GPUs, or
`:nvidia-legacy` for older Nvidia GPUs. The configurator saves your selection
to `profile.yaml` → `base_image:`. You can also change it manually:

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
