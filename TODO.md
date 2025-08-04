most important:
- add as much logs as possible
  - journalctl (?)
  - other?

on target machine:
- check packages
- check mesa libs installed
- check modprobe blacklists?

future plans:
- how to deliver?
- check qt context creation
- check qt gl functions loading
- check if executed with sudo (for dmesg)

packages to check:
- xserver-xorg-video-nvidia-*
- nvidia-driver-* / nvidia-dkms-* / nvidia-headless-* / nvidia-kernel-*
- mesa-utils
- libdrm-nouveau2 (?)

other:
- rename to GfxHealth / gfx-health