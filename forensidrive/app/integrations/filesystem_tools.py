from app.core.commands import run_command
from app.core.errors import CommandFailedError

def detect_filesystem(device_path: str) -> str | None:
    res = run_command(["blkid", "-s", "TYPE", "-o", "value", device_path], timeout=5, capture=True)
    if res.success and res.stdout.strip():
        return res.stdout.strip()
    return None

def mount_device(device_path: str, mount_point: str, read_only: bool = True, filesystem_type: str = None) -> bool:
    cmd = ["mount"]
    if read_only:
        cmd.extend(["-o", "ro"])
    if filesystem_type:
        cmd.extend(["-t", filesystem_type])
    cmd.extend([device_path, mount_point])
    
    res = run_command(cmd, timeout=10, capture=True)
    if not res.success:
        raise CommandFailedError(f"Failed to mount {device_path} at {mount_point}: {res.stderr}")
    return True

def unmount_device(mount_point: str, force: bool = False) -> bool:
    cmd = ["umount"]
    if force:
        cmd.append("-f")
    cmd.append(mount_point)
    
    res = run_command(cmd, timeout=10, capture=True)
    if not res.success:
        raise CommandFailedError(f"Failed to unmount {mount_point}: {res.stderr}")
    return True

def check_filesystem(device_path: str) -> dict:
    fs_type = detect_filesystem(device_path)
    
    # Run check in non-interactive mode
    check_res = run_command(["fsck", "-n", device_path], timeout=60, capture=True)
    status = "healthy" if check_res.success else "errors_found"
    
    return {
        "status": status,
        "errors": check_res.stderr if not check_res.success else "",
        "filesystem_type": fs_type or "unknown"
    }

def get_block_device_info(device_path: str) -> dict:
    res = run_command(["blkid", "-o", "export", device_path], timeout=5, capture=True)
    info = {}
    if res.success:
        for line in res.stdout.splitlines():
            if "=" in line:
                key, val = line.split("=", 1)
                info[key] = val
    return info
