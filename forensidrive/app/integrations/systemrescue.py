import os
from app.core.commands import run_command

class SystemRescueEnvironment:
    @staticmethod
    def is_systemrescue() -> bool:
        if os.path.exists("/etc/system-rescue"):
            return True
        try:
            with open("/etc/os-release", "r") as f:
                content = f.read()
                if "systemrescue" in content.lower():
                    return True
        except FileNotFoundError:
            pass
        return False

    @staticmethod
    def get_version() -> str:
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("VERSION="):
                        return line.split("=")[1].strip().strip('"')
        except FileNotFoundError:
            pass
        return "Unknown"

    @staticmethod
    def get_boot_mode() -> str:
        if os.path.exists("/sys/firmware/efi"):
            return "UEFI"
        return "BIOS"

    @staticmethod
    def get_live_media_device() -> str | None:
        try:
            result = run_command(["findmnt", "-n", "-o", "SOURCE", "/run/archiso/bootmnt"], timeout=5, capture=True)
            if result.success and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
        return None

    @staticmethod
    def is_graphical() -> bool:
        return bool(os.environ.get("DISPLAY"))

    @staticmethod
    def get_autostart_path() -> str:
        return "/etc/skel/.config/autostart"

    @staticmethod
    def get_install_path() -> str:
        return os.environ.get("FORENSIDRIVE_PATH", "/usr/local/forensidrive")
