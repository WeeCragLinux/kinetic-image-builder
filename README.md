# kineticos-plus

A modular bootc image based on `ghcr.io/theblack-don/kineticos:default` by default.
Small always-on core, everything else opt-in: enable the modules you want,
comment out the apps you don't.

Built with [dcli-bootc](https://copr.fedorainfracloud.org/coprs/theblackdon/dcli-bootc).
`build_files/build.sh` is generated — edit `modules/*.yaml`, then run
`dcli-bootc gen`.

## Configure

Edit `profile.yaml` to enable or disable modules, and edit `modules/*.yaml` to
choose apps. `base`, `rpmfusion`, and the Terra repositories are enabled by
default; gaming apps are commented out. The configurator is distributed
separately as an RPM; it is not included in this image or repository checkout.

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
| `base` | update timer. Always on. | no |
| `rpmfusion` | RPMFusion free + nonfree repos. Leave on unless minimal. | — (it *is* the repos) |
| `terra` | Terra repositories. Enabled by default; no apps installed by this module. | no |
| `browsers` | helium, chromium, firefox, brave-browser, brave-origin, vivaldi | brave/vivaldi need their own repo setup (in-module) |
| `content` | obs-studio, audacity, kdenlive, gimp, pavucontrol, easyeffects, vlc, mpv, Spotify flatpak | yes (vlc, mpv) |
| `gaming` | prismlauncher, terra-mangohud, goverlay, steam, lutris (all commented out by default) | yes (if steam uncommented) |
| `comms` | telegram, thunderbird, discord (commented) | yes (if discord uncommented) |
| `terminals` | kitty, konsole | no |
| `dev` | Zed Flatpak (commented out) | no |
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

Edit the module files to choose apps. In each `modules/*.yaml`, commented-out
entries are disabled; uncomment an entry to enable it, or comment it out to
remove it:

```yaml
packages:
 - mpv
 # - vlc
```

Some apps need their repo lines toggled alongside the package (brave,
vivaldi) — the comments in each file say which lines belong together.
After any change, re-run `dcli-bootc gen` before building.

## Base image variants

The default is `ghcr.io/theblack-don/kineticos:default` for AMD and Intel GPUs.
Set `profile.yaml` → `base_image:` to choose the variant that matches your GPU:
`:default` for AMD and Intel, `:nvidia` for Turing and newer Nvidia GPUs, or
`:nvidia-legacy` for older Nvidia GPUs:

```yaml
base_image: ghcr.io/theblack-don/kineticos:default
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
- **Flatpaks:** listed under `flatpaks:` per module (see Spotify in `content`).

## License

This project is licensed under the [MIT License](LICENSE). It covers this
repository's original content; Kineticos, dcli-bootc, and third-party packages
and repositories remain under their own terms.
