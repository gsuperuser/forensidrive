import re
from app.core.commands import find_command, run_command

class RecoveryToolAdapter:
    name: str = ""
    command: str = ""
    description: str = ""
    
    def is_available(self) -> bool:
        return find_command(self.command) is not None
        
    def get_version(self) -> str:
        if not self.is_available():
            return "Not installed"
        try:
            res = run_command([self.command, "--version"], timeout=2, capture=True)
            if res.success:
                return res.stdout.strip().split("\n")[0]
            res = run_command([self.command, "-v"], timeout=2, capture=True)
            if res.success:
                return res.stdout.strip().split("\n")[0]
        except Exception:
            pass
        return "Unknown version"

    def build_command(self, source_device: str, destination: str, options: dict) -> list[str]:
        raise NotImplementedError

    def parse_output(self, line: str) -> dict:
        return {"progress": 0.0, "message": line, "technical": line}
        
    def get_supported_options(self) -> list[dict]:
        return []


class PhotoRecAdapter(RecoveryToolAdapter):
    name = "PhotoRec"
    command = "photorec"
    description = "File recovery by file type from damaged/formatted drives."

    def build_command(self, source_device: str, destination: str, options: dict) -> list[str]:
        cmd = [self.command, "/d", destination, "/cmd", source_device]
        if "options" in options:
            cmd.extend(options["options"].split())
        else:
            cmd.extend(["partition_none", "search"])
        return cmd
        
    def parse_output(self, line: str) -> dict:
        match = re.search(r"sector\s+(\d+)/(\d+)", line)
        if match:
            current, total = int(match.group(1)), int(match.group(2))
            progress = (current / total) * 100 if total > 0 else 0
            return {"progress": progress, "message": f"Recovering... {progress:.1f}%", "technical": line}
        return {"progress": 0.0, "message": "Recovering...", "technical": line}
        
    def get_supported_options(self) -> list[dict]:
        return [{"name": "options", "label": "Command Options", "description": "Custom options for photorec", "type": "string", "default": "partition_none search"}]


class TestDiskAdapter(RecoveryToolAdapter):
    name = "TestDisk"
    command = "testdisk"
    description = "Partition recovery and repair. Note: This is an interactive tool."

    def build_command(self, source_device: str, destination: str, options: dict) -> list[str]:
        return [self.command, source_device]


class DDRescueAdapter(RecoveryToolAdapter):
    name = "GNU ddrescue"
    command = "ddrescue"
    description = "Disk/partition imaging/cloning for damaged media."

    def build_command(self, source_device: str, destination: str, options: dict) -> list[str]:
        logfile = options.get("logfile", f"{destination}.log")
        return [self.command, "-f", source_device, destination, logfile]
        
    def parse_output(self, line: str) -> dict:
        match = re.search(r"rescued:\s+(\d+\s+\w+)", line)
        if match:
            return {"progress": -1.0, "message": f"Rescued: {match.group(1)}", "technical": line}
        return {"progress": 0.0, "message": "Copying...", "technical": line}

    def get_supported_options(self) -> list[dict]:
        return [{"name": "logfile", "label": "Log File", "description": "Path to the mapfile/logfile", "type": "string", "default": ""}]


class ForemostAdapter(RecoveryToolAdapter):
    name = "Foremost"
    command = "foremost"
    description = "File carving from disk images."

    def build_command(self, source_device: str, destination: str, options: dict) -> list[str]:
        return [self.command, "-i", source_device, "-o", destination]
        
    def parse_output(self, line: str) -> dict:
        return {"progress": 0.0, "message": "Carving files...", "technical": line}


class ScalpelAdapter(RecoveryToolAdapter):
    name = "Scalpel"
    command = "scalpel"
    description = "File carving similar to foremost."

    def build_command(self, source_device: str, destination: str, options: dict) -> list[str]:
        return [self.command, "-o", destination, source_device]


class RecoveryToolRegistry:
    def __init__(self):
        self.tools = [
            PhotoRecAdapter(),
            TestDiskAdapter(),
            DDRescueAdapter(),
            ForemostAdapter(),
            ScalpelAdapter()
        ]
        
    def get_available_tools(self) -> list[RecoveryToolAdapter]:
        return [t for t in self.tools if t.is_available()]
        
    def get_tool(self, name: str) -> RecoveryToolAdapter | None:
        for t in self.tools:
            if t.command == name or t.name == name:
                return t
        return None
        
    def get_recommended_tool(self, scenario: str) -> RecoveryToolAdapter | None:
        if scenario == 'deleted_files':
            return self.get_tool('photorec')
        elif scenario == 'damaged_drive':
            return self.get_tool('ddrescue')
        elif scenario == 'partition_recovery':
            return self.get_tool('testdisk')
        elif scenario == 'formatted_drive':
            return self.get_tool('photorec')
        return None
