# kineticos-plus

A modular bootc image based on `ghcr.io/theblack-don/kineticos:default` by default.
Small always-on core, everything else opt-in: enable the modules you want,
comment out the apps you don't.

Built with [dcli-bootc](https://copr.fedorainfracloud.org/coprs/theblackdon/dcli-bootc).
`build_files/build.sh` is generated — edit `modules/*.yaml`, then run
`dcli-bootc gen`.

## Configure

Edit `profile.yaml` to choose the base image and module defaults, and edit
`modules/*.yaml` to choose apps. `removals`, `base`, `rpmfusion`, and `terra`
are enabled by default; app modules are listed but disabled until apps are
selected. The configurator is distributed separately as an RPM; it is not
included in this image or repository checkout.

## Build

```bash
dcli-bootc gen
dcli-bootc build
```

To use it on a machine, rebase/switch to the built image with `bootc`
(follow your current system's rebase procedure; keep a known-good
deployment pinned so you can roll back).

## Modules

`profile.yaml` lists all modules under `enabled_modules:` so the configurator
can offer their app choices. `removals`, `base`, `rpmfusion`, and `terra` are
enabled by default; app modules are commented out and should only be enabled
when an app from that module is selected. `removals` is listed first, followed
by `base`; keep `rpmfusion` or `terra` before any apps that need those
repositories. Because removals run first, selecting one of those apps in
another module (such as Dolphin or Spectacle) installs it afterward.

By default, the image includes no file manager, terminal emulator, or
screenshot tool. The removals module removes Dolphin, Konsole, Alacritty, and
Spectacle; the `file-managers`, `terminals`, and `screenshot-tools` modules are
opt-in, with their package choices commented out until selected.

| Module | Contents | Needs `rpmfusion`? |
|---|---|---|
| `removals` | Removes preinstalled dolphin, spectacle, konsole, and alacritty | no |
| `base` | update timer. Always on. | no |
| `rpmfusion` | RPMFusion free + nonfree repos. Enabled by default; disable if no selected app needs them. | — (it *is* the repos) |
| `terra` | Terra repositories. Enabled by default; needed for `terra-mangohud` and other Terra packages. No apps installed by this module. | no |
| `browsers` | helium, chromium, firefox, brave-browser, brave-origin, vivaldi | Brave and Vivaldi need their vendor repo enabled alongside the app |
| `content` | obs-studio, audacity, kdenlive, gimp, pavucontrol, easyeffects, vlc, mpv, Spotify flatpak | yes (vlc, mpv) |
| `file-managers` | Thunar, Nautilus, PCManFM-Qt, Dolphin (commented out) | no |
| `gaming` | prismlauncher, terra-mangohud, goverlay, ProtonPlus, steam, lutris (all commented out by default) | yes (if steam uncommented) |
| `comms` | telegram, thunderbird, discord (commented) | yes (if discord uncommented) |
| `terminals` | kitty, konsole, alacritty, foot, ghostty (commented out) | no |
| `screenshot-tools` | Flameshot, Shutter, Spectacle (commented out) | no |
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

Some apps need their repo commands enabled alongside the package. In
`modules/browsers.yaml`, Brave Browser and Brave Origin share one repo command;
Vivaldi has a separate command. The browser module's pre script adds the repo
before DNF installs those packages. Until the separate configurator is updated,
when editing YAML manually, uncomment only the repo command for each selected
browser. After any change, re-run `dcli-bootc gen` before building.

## Base image variants

The default is `ghcr.io/theblack-don/kineticos:default` for AMD and Intel GPUs.
Set `profile.yaml` → `base_image:` to choose the variant that matches your GPU:
`:default` for AMD and Intel, `:nvidia` for Turing and newer Nvidia GPUs, or
`:nvidia-legacy` for older Nvidia GPUs. `ghcr.io/theblack-don/kineticos:deck`
is also selectable, but it is very early and not recommended for normal use:

```yaml
base_image: ghcr.io/theblack-don/kineticos:default
```

To try the experimental Deck image, replace that value with
`ghcr.io/theblack-don/kineticos:deck`; expect instability and use it only if
you are willing to troubleshoot early-development issues.

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
