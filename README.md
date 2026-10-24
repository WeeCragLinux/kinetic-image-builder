# kineticos-plus

A modular bootc image based on `ghcr.io/theblack-don/kineticos:default` by default.
Small always-on core, everything else opt-in: enable the modules you want,
comment out the apps you don't.

Built with [dcli-bootc](https://copr.fedorainfracloud.org/coprs/theblackdon/dcli-bootc).
`build_files/build.sh` is generated — edit `modules/*.yaml`, then run
`dcli-bootc gen`.

## Configure

Edit `profile.yaml` to choose the base image and module defaults, and edit
`modules/*.yaml` to choose apps and optional removals. `base` and `rpmfusion`
are enabled by default. Removals and app modules are listed but disabled
until the user selects choices; no packages are removed by default. The
configurator is distributed separately as an RPM; it is not included in this
image or repository checkout.

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
can offer their app or removal choices. `base` and `rpmfusion` are
enabled by default; removals and app modules are commented out and should only
be enabled when the user selects choices from them. The `removals` module is
listed first so selected removals run before `base` and app modules. Keep
`rpmfusion` before any apps that need those repositories. If a
package is selected for both removal and installation, the later app module
installs it afterward.

No packages are removed by default, so preinstalled apps from the base image
remain unless selected for removal. Steam is preinstalled, and Alacritty
remains installed as a fallback terminal. The optional removals module offers
Dolphin, Spectacle, Konsole, KWrite, Kate, and several KDE extras, plus
`terra-mangohud` if you want Fedora's `mangohud`; each removal choice is
commented out until selected. The `browsers`, `content`, `gaming`, `comms`,
`terminals`, `lgl-tools`, and `flatpak` modules are also opt-in.

| Module | Contents | Needs `rpmfusion`? |
|---|---|---|
| `removals` | Optional removal of preinstalled Dolphin, Spectacle, Konsole, KWrite, Kate, and KDE extras (`kdebugsettings`, `kfind`, `krdc`, `krfb`, `kwalletmanager5`), plus `terra-mangohud`; none by default | no |
| `base` | tmux, dcli-bootc, the dcli-bootc COPR, and the update timer. Always on. | no |
| `rpmfusion` | RPMFusion free + nonfree repos. Enabled by default; disable if no selected app needs them. | — (it *is* the repos) |
| `browsers` | helium-bin (needs the `imput/helium` COPR), chromium, firefox, brave-browser, brave-origin, vivaldi-stable | Brave and Vivaldi need their vendor repo enabled alongside the app |
| `content` | audacity, kdenlive, gimp, pavucontrol, vlc, mpv | yes (vlc, mpv) |
| `gaming` | Steam is preinstalled in the base image; optional mangohud, goverlay, lutris; ProtonPlus and PrismLauncher Flatpaks. Enables the `linuxgamerlife/lgl-essentials` COPR for mangohud and goverlay | no |
| `comms` | telegram-desktop, thunderbird, discord (commented) | only discord (nonfree) |
| `terminals` | kitty, foot, ghostty (commented out); Alacritty remains installed as a fallback | no |
| `lgl-tools` | LGL System Loadout, Colour Picker, DNF Helper, Emoji Picker, Papercutter, Scheduler Manager (from the `linuxgamerlife/lgl-toolkit` COPR) | no (Scheduler Manager also needs `scx-tools` and `scx-scheds` from `bieszczaders/kernel-cachyos-addons`) |
| `flatpak` | opt-in Flatpaks: Spotify, EasyEffects, ProtonPlus, PrismLauncher, Zed, OBS Studio, Discord | no |

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
- **Flatpaks:** most are listed in `modules/flatpak.yaml`; `gaming` also has
  its own ProtonPlus and PrismLauncher entries.
  `dcli-bootc` installs them with `flatpak --user` into the invoking user's
  home; they are deliberately not baked into the image, because `/var/lib/flatpak`
  is machine-local state under bootc. Run `dcli-bootc build` as your normal
  user, not with `sudo`, or the Flatpaks will be installed for root instead.
  If they need to be applied separately, run
  `dcli-bootc flatpak sync -p <project>`.

## License

This project is licensed under the [MIT License](LICENSE). It covers this
repository's original content; Kineticos, dcli-bootc, and third-party packages
and repositories remain under their own terms.
