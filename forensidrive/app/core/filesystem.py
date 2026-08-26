import os
import tempfile
from typing import List, Dict, Any, Optional
from app.core.commands import run_command
from app.core.errors import ForensiDriveError

def mount_partition(partition_path: str, mount_point: Optional[str] = None, read_only: bool = True) -> str:
    """Mount a partition. Defaults to read-only for forensic integrity."""
    target_mp = mount_point or create_temp_mount_point()
    os.makedirs(target_mp, exist_ok=True)
    
    cmd = ["mount"]
    if read_only:
        cmd.extend(["-o", "ro"])
    cmd.extend([partition_path, target_mp])
    
    try:
        run_command(cmd, check=True)
        return target_mp
    except Exception as e:
        raise ForensiDriveError(
            user_message="Could not open the drive files.",
            technical_details=str(e)
        )

def unmount_partition(mount_point: str) -> bool:
    try:
        run_command(["umount", mount_point], check=True)
        return True
    except Exception as e:
        raise ForensiDriveError(
            user_message="Could not safely close the drive.",
            technical_details=str(e)
        )

def create_temp_mount_point(prefix: str = "forensidrive_") -> str:
    return tempfile.mkdtemp(prefix=prefix, dir="/tmp" if os.path.exists("/tmp") else None)

def get_available_space(path: str) -> int:
    try:
        st = os.statvfs(path)
        return st.f_bavail * st.f_frsize
    except Exception:
        return 0

def list_directory(path: str) -> List[Dict[str, Any]]:
    results = []
    try:
        for entry in os.scandir(path):
            results.append({
                "name": entry.name,
                "path": entry.path,
                "is_dir": entry.is_dir(),
                "size": entry.stat().st_size if not entry.is_dir() else 0
            })
    except Exception:
        pass
    return results
