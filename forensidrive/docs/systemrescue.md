# SystemRescue Integration

## Overview
ForensiDrive is designed to be the primary graphical interface for a custom-built SystemRescue ISO. It replaces or overlays the default Xfce desktop to give users immediate access to forensic tools without using the command line.

## Installation
The recommended path for installation on the live file system is:
`/usr/local/forensidrive/`

## Autostart Configuration
To start the application automatically:
Place the `forensidrive.desktop` file into the autostart directory (e.g. `~/.config/autostart/` for the live user, or `/etc/xdg/autostart/`).

## Dependencies
SystemRescue naturally provides many required tools. The minimum dependencies include:
- `python3`
- `python3-tk` (Tkinter)
- `lsblk`, `mount`, `umount` (util-linux)
- `shred`, `dd` (coreutils)
- `photorec`, `testdisk`
- `ddrescue`

## Boot Sequence
1. Power On (BIOS/UEFI)
2. SystemRescue boots (Live USB)
3. Xorg/Wayland Graphical Session initializes
4. Autostart triggers `python3 /usr/local/forensidrive/app/main.py`
5. ForensiDrive UI appears fullscreen.

## Limitations
- Must be run as root (or with appropriate polkit/sudo permissions) for block device access.
- Offline by design; cannot download missing packages at runtime.

## TODO Items
- [ ] Automate the creation of a custom ISO with ForensiDrive embedded.
- [ ] Determine exact xdg autostart paths for the target SystemRescue version.
