from dataclasses import dataclass
from typing import Optional

@dataclass
class Partition:
    name: str
    path: str
    size: int
    size_human: str
    filesystem: Optional[str] = None
    label: Optional[str] = None
    mountpoint: Optional[str] = None
    uuid: Optional[str] = None
    partition_type: Optional[str] = "part"
    parent_device: Optional[str] = None
    type: Optional[str] = "part"

    @classmethod
    def from_lsblk_dict(cls, data: dict, parent_device: Optional[str] = None, parent_drive_name: Optional[str] = None) -> "Partition":
        name = data.get("name", "")
        path = f"/dev/{name}" if not name.startswith("/dev/") else name
        
        raw_size = data.get("size", 0)
        if isinstance(raw_size, int):
            size_bytes = raw_size
            units = ["B", "KB", "MB", "GB", "TB", "PB"]
            idx = 0
            val = float(size_bytes)
            while val >= 1024.0 and idx < len(units) - 1:
                val /= 1024.0
                idx += 1
            size_human = f"{val:.1f} {units[idx]}"
            size_val = size_bytes
        else:
            size_bytes = 0
            size_human = str(raw_size)
            size_val = raw_size

        return cls(
            name=name,
            path=path,
            size=size_val,
            size_human=size_human,
            filesystem=data.get("fstype") or data.get("filesystem"),
            label=data.get("label"),
            mountpoint=data.get("mountpoint"),
            uuid=data.get("uuid"),
            partition_type=data.get("type", "part"),
            parent_device=parent_drive_name or parent_device or data.get("pkname"),
            type=data.get("type", "part")
        )

    @property
    def fstype(self) -> Optional[str]:
        return self.filesystem

    @property
    def parent_drive_name(self) -> Optional[str]:
        return self.parent_device

    @property
    def is_mounted(self) -> bool:
        return bool(self.mountpoint and self.mountpoint.strip())

    @property
    def display_name(self) -> str:
        fs_str = f" [{self.filesystem}]" if self.filesystem else ""
        label_str = f" '{self.label}'" if self.label else ""
        return f"{self.name}{label_str} ({self.size_human}){fs_str}"
