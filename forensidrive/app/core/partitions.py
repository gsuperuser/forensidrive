import json
from typing import List, Optional
from app.models.partition import Partition
from app.core.commands import run_command, find_command
from app.core.errors import CommandNotFoundError, ForensiDriveError

def get_partitions(device_path: str) -> List[Partition]:
    """Retrieve all partitions for a given storage device path."""
    if not find_command("lsblk"):
        return []

    try:
        cmd = [
            "lsblk", "-J", "-b",
            "-o", "NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE,LABEL,UUID,PKNAME",
            device_path
        ]
        res = run_command(cmd, check=True)
        data = json.loads(res.stdout)
        devices = data.get("blockdevices", [])
        
        parts: List[Partition] = []
        for dev in devices:
            if dev.get("type") == "part":
                parts.append(Partition.from_lsblk_dict(dev))
            for child in dev.get("children", []):
                if child.get("type") == "part":
                    parts.append(Partition.from_lsblk_dict(child))
        return parts
    except Exception as e:
        if isinstance(e, ForensiDriveError):
            raise
        raise ForensiDriveError(
            user_message="We couldn't retrieve partition information for this drive.",
            technical_details=str(e)
        )

def get_partition_info(partition_path: str) -> Optional[Partition]:
    parts = get_partitions(partition_path)
    return parts[0] if parts else None

def is_mounted(partition_path: str) -> bool:
    try:
        with open("/proc/mounts", "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and parts[0] == partition_path:
                    return True
    except Exception:
        pass
    return False

def get_filesystem_type(partition_path: str) -> Optional[str]:
    if not find_command("blkid"):
        return None
    try:
        res = run_command(["blkid", "-o", "value", "-s", "TYPE", partition_path], check=False)
        if res.success and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return None
