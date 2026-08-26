import os
import platform
from typing import Dict
from app import APP_VERSION
from app.core.commands import find_command

def get_system_info() -> Dict[str, str]:
    """Get system and environment details for non-technical display."""
    sys_rescue_ver = "Unknown"
    for path in ["/etc/system-rescue-version", "/etc/system-rescue", "/etc/os-release"]:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    for line in f:
                        if "VERSION=" in line or "PRETTY_NAME=" in line:
                            sys_rescue_ver = line.split("=")[1].strip().strip('"')
                            break
                    if sys_rescue_ver == "Unknown":
                        f.seek(0)
                        sys_rescue_ver = f.readline().strip()
                break
            except Exception:
                pass

    total_ram = "Unknown"
    avail_ram = "Unknown"
    if os.path.exists("/proc/meminfo"):
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        total_ram = f"{kb / (1024 * 1024):.1f} GB"
                    elif line.startswith("MemAvailable:"):
                        kb = int(line.split()[1])
                        avail_ram = f"{kb / (1024 * 1024):.1f} GB"
        except Exception:
            pass

    boot_mode = "UEFI" if os.path.exists("/sys/firmware/efi") else "BIOS / Legacy"

    return {
        "app_version": APP_VERSION,
        "systemrescue_version": sys_rescue_ver,
        "kernel_version": platform.release(),
        "cpu_arch": platform.machine(),
        "total_ram": total_ram,
        "available_ram": avail_ram,
        "boot_mode": boot_mode,
        "hostname": platform.node()
    }

def get_available_tools() -> Dict[str, bool]:
    """Check presence of common forensic and system tools."""
    tools = [
        "photorec", "testdisk", "ddrescue", "foremost", "scalpel",
        "shred", "wipefs", "blkdiscard", "dd",
        "lsblk", "blkid", "mount", "umount", "fsck"
    ]
    return {tool: bool(find_command(tool)) for tool in tools}
