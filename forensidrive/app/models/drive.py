from dataclasses import dataclass, field
from typing import List, Optional
from app.models.partition import Partition

@dataclass
class Drive:
    name: str
    path: str
    size: int
    size_human: str
    model: Optional[str] = None
    vendor: Optional[str] = None
    serial: Optional[str] = None
    removable: bool = False
    read_only: bool = False
    transport: Optional[str] = None
    partitions: List[Partition] = field(default_factory=list)
    is_boot_device: bool = False
    type: str = "disk"

    @classmethod
    def from_lsblk_dict(cls, data: dict) -> "Drive":
        name = data.get("name", "")
        path = f"/dev/{name}" if not name.startswith("/dev/") else name
        
        raw_size = data.get("size", 0)
        if isinstance(raw_size, int):
            size_bytes = raw_size
            size_human = cls.human_size(size_bytes)
            size_val = size_bytes
        elif isinstance(raw_size, str) and raw_size.isdigit():
            size_bytes = int(raw_size)
            size_human = cls.human_size(size_bytes)
            size_val = size_bytes
        else:
            size_bytes = 0
            size_human = str(raw_size) if raw_size else "0 B"
            size_val = raw_size
        
        drive = cls(
            name=name,
            path=path,
            size=size_val,
            size_human=size_human,
            model=data.get("model"),
            vendor=data.get("vendor"),
            serial=data.get("serial"),
            removable=bool(data.get("rm", False) or data.get("rm") == "1"),
            read_only=bool(data.get("ro", False) or data.get("ro") == "1"),
            transport=data.get("tran"),
            is_boot_device=False,
            type=data.get("type", "disk")
        )

        children = data.get("children", [])
        for child in children:
            if child.get("type") == "part":
                part = Partition.from_lsblk_dict(child, parent_device=name)
                drive.partitions.append(part)
                if part.mountpoint in ["/", "/boot", "/run/archiso/bootmnt", "/run/archiso/cowspace"]:
                    drive.is_boot_device = True

        return drive

    @property
    def display_name(self) -> str:
        ident = []
        if self.vendor and self.vendor.strip():
            ident.append(self.vendor.strip())
        if self.model and self.model.strip():
            ident.append(self.model.strip())
        name_str = " ".join(ident) if ident else self.name or "Storage Drive"
        part_info = f" ({len(self.partitions)} partitions)" if self.partitions else ""
        return f"{name_str} - {self.size_human}{part_info}"

    @staticmethod
    def human_size(size_bytes: int) -> str:
        if size_bytes <= 0:
            return "0 B"
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        idx = 0
        val = float(size_bytes)
        while val >= 1024.0 and idx < len(units) - 1:
            val /= 1024.0
            idx += 1
        return f"{val:.1f} {units[idx]}"
