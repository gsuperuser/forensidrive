import json
import os
from typing import List, Optional
from app.models.drive import Drive
from app.core.commands import run_command, find_command
from app.core.errors import CommandNotFoundError, ForensiDriveError

def detect_drives() -> List[Drive]:
    """Detect storage drives using lsblk -J."""
    if not find_command("lsblk"):
        # If running on non-Linux or test system without lsblk
        return []

    try:
        cmd = [
            "lsblk", "-J", "-b",
            "-o", "NAME,SIZE,TYPE,MODEL,VENDOR,SERIAL,RM,RO,TRAN,MOUNTPOINT,FSTYPE,LABEL,UUID,PKNAME"
        ]
        res = run_command(cmd, check=True)
        if not res.stdout.strip():
            return []

        data = json.loads(res.stdout)
        devices = data.get("blockdevices", [])
        
        drives = []
        for dev in devices:
            # Only root disk devices
            if dev.get("type") in ["disk", "loop"]:
                drive = Drive.from_lsblk_dict(dev)
                # Check boot device heuristic
                if drive.is_boot_device or is_boot_device(drive.name):
                    drive.is_boot_device = True
                drives.append(drive)

        return drives
    except Exception as e:
        if isinstance(e, ForensiDriveError):
            raise
        raise ForensiDriveError(
            user_message="We couldn't inspect your storage drives.",
            technical_details=str(e)
        )

def get_drive(device_path: str) -> Optional[Drive]:
    drives = detect_drives()
    for d in drives:
        if d.path == device_path or d.name == device_path or f"/dev/{d.name}" == device_path:
            return d
    return None

def refresh_drive(drive: Drive) -> Drive:
    updated = get_drive(drive.path)
    return updated if updated else drive

def is_boot_device(device_name: str) -> bool:
    """Check if device is part of live/root boot filesystem."""
    try:
        with open("/proc/mounts", "r") as f:
            mounts = f.read()
            # If device appears in root mount or archiso mount
            clean_name = os.path.basename(device_name)
            for line in mounts.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    dev, mnt = parts[0], parts[1]
                    if clean_name in dev and mnt in ["/", "/boot", "/run/archiso/bootmnt", "/run/archiso/cowspace"]:
                        return True
    except Exception:
        pass
    return False

def get_mount_points(device_path: str) -> List[str]:
    mounts = []
    try:
        with open("/proc/mounts", "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and device_path in parts[0]:
                    mounts.append(parts[1])
    except Exception:
        pass
    return mounts
