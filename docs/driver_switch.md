check available drivers
```bash
lspci -k | grep -E -A 5 '(VGA|3D)'
```
example output:
```bash
09:00.0 VGA compatible controller: NVIDIA Corporation Device 2489 (rev a1)
        Subsystem: NVIDIA Corporation Device 153c
        Kernel driver in use: nvidia
        Kernel modules: nvidiafb, nouveau, nvidia_drm, nvidia
```
add not needed drivers to blacklist, remove from blacklist needed one
```bash
sudo nano /etc/modprobe.d/disable_nvidia.conf
```
example /etc/modprobe.d/disable_nvidia.conf:
```bash
blacklist nvidia
blacklist nvidiafb
blacklist nvidia_drm
```
find if needed driver is blacklisted
```bash
sudo grep -i nouveau /etc/modprobe.d/* 2>/dev/null
sudo grep -i nouveau /lib/modprobe.d/* 2>/dev/null
```
example output:
```bash
/etc/modprobe.d/blacklist-nouveau.conf: blacklist nouveau
```
comment this lines out

(optional) remove xserver-xorg-video package related to driver you disable and install one related to desired driver
```bash
sudo apt remove xserver-xorg-video-nvidia-515
sudo apt install xserver-xorg-video-nouveau
```

regenerate initramfs
```bash
sudo update-initramfs -u
```

update Xorg config
```bash
sudo nano /etc/X11/xorg.conf
```
comment old nvidia config and add similar with nouveau as driver
```bash
# Section "Device"
#     Identifier     "Device0"
#     Driver         "nvidia"
#     VendorName     "NVIDIA Corporation"
# EndSection

Section "Device"
    Identifier     "Device0"
    Driver         "nouveau"
EndSection
```

# troubleshooting
```bash
sudo dmesg
sudo systemctl status display-manager
cat /var/log/Xorg.0.log | less
```
