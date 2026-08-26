import re
from app.core.commands import find_command, run_command

class ErasureToolAdapter:
    name: str = ""
    command: str = ""
    description: str = ""
    risk_level: str = "medium"
    
    def is_available(self) -> bool:
        return find_command(self.command) is not None
        
    def get_version(self) -> str:
        if not self.is_available():
            return "Not installed"
        try:
            res = run_command([self.command, "--version"], timeout=2, capture=True)
            if res.success:
                return res.stdout.strip().split("\n")[0]
        except Exception:
            pass
        return "Unknown version"

    def build_command(self, target_device: str, options: dict) -> list[str]:
        raise NotImplementedError

    def parse_output(self, line: str) -> dict:
        return {"progress": 0.0, "message": "Erasing...", "technical": line}

    def get_estimated_duration(self, device_size_bytes: int) -> str:
        return "Unknown"

    def get_supported_options(self) -> list[dict]:
        return []

    def get_warning_message(self) -> str:
        return f"Warning: Running {self.name} will result in permanent data loss."


class ShredAdapter(ErasureToolAdapter):
    name = "Shred"
    command = "shred"
    description = "Overwrite with random data, multiple passes."
    risk_level = "extreme"

    def build_command(self, target_device: str, options: dict) -> list[str]:
        passes = options.get("passes", 3)
        cmd = [self.command, "-v", "-n", str(passes)]
        if options.get("zero_fill_final", False):
            cmd.append("-z")
        cmd.append(target_device)
        return cmd
        
    def parse_output(self, line: str) -> dict:
        match = re.search(r"pass (\d+)/(\d+)", line)
        if match:
            current = int(match.group(1))
            total = int(match.group(2))
            progress = (current / total) * 100
            return {"progress": progress, "message": f"Pass {current} of {total}", "technical": line}
        return {"progress": 0.0, "message": "Overwriting...", "technical": line}

    def get_supported_options(self) -> list[dict]:
        return [
            {"name": "passes", "label": "Number of passes", "description": "Number of times to overwrite", "type": "integer", "default": 3},
            {"name": "zero_fill_final", "label": "Zero-fill final pass", "description": "Add a final overwrite with zeros to hide shredding", "type": "boolean", "default": False}
        ]


class WipefsAdapter(ErasureToolAdapter):
    name = "Wipefs"
    command = "wipefs"
    description = "Remove filesystem signatures only (fast, less destructive)."
    risk_level = "medium"
    
    def build_command(self, target_device: str, options: dict) -> list[str]:
        return [self.command, "-a", target_device]
        
    def get_warning_message(self) -> str:
        return "Warning: wipefs only removes filesystem signatures. Underlying data may still be recoverable."


class BlkdiscardAdapter(ErasureToolAdapter):
    name = "Block Discard"
    command = "blkdiscard"
    description = "TRIM/discard blocks on SSDs."
    risk_level = "high"
    
    def build_command(self, target_device: str, options: dict) -> list[str]:
        return [self.command, target_device]

    def get_warning_message(self) -> str:
        return "Warning: blkdiscard issues TRIM commands to the SSD. Effectiveness depends on SSD firmware."


class DDZeroAdapter(ErasureToolAdapter):
    name = "DD Zero Fill"
    command = "dd"
    description = "Write zeros using dd."
    risk_level = "extreme"
    
    def build_command(self, target_device: str, options: dict) -> list[str]:
        return [self.command, "if=/dev/zero", f"of={target_device}", "bs=4M", "status=progress"]
        
    def parse_output(self, line: str) -> dict:
        match = re.search(r"(\d+) bytes", line)
        if match:
            bytes_written = int(match.group(1))
            return {"progress": -1.0, "message": f"Written: {bytes_written} bytes", "technical": line}
        return {"progress": 0.0, "message": "Zeroing drive...", "technical": line}


class ErasureToolRegistry:
    def __init__(self):
        self.tools = [
            ShredAdapter(),
            WipefsAdapter(),
            BlkdiscardAdapter(),
            DDZeroAdapter()
        ]
        
    def get_available_tools(self) -> list[ErasureToolAdapter]:
        return [t for t in self.tools if t.is_available()]
        
    def get_tool(self, name: str) -> ErasureToolAdapter | None:
        for t in self.tools:
            if t.command == name or t.name == name:
                return t
        return None
        
    def get_tools_by_risk(self, max_risk: str) -> list[ErasureToolAdapter]:
        levels = {"low": 1, "medium": 2, "high": 3, "extreme": 4}
        max_val = levels.get(max_risk, 4)
        return [t for t in self.get_available_tools() if levels.get(t.risk_level, 4) <= max_val]
