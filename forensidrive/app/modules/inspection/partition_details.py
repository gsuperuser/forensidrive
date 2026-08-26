import tkinter as tk
from app.ui.navigation import BasePage
from app.ui.theme import ForensiDriveTheme
from app.ui.widgets import InfoRow, SectionHeader
from app.models.partition import Partition

class PartitionDetailsPage(BasePage):
    """Detailed inspection of a specific partition."""

    def build(self):
        partition: Partition = self.kwargs.get('partition')
        if not partition:
            self.create_header(title="Partition Details", subtitle="No partition selected", show_back=True)
            return

        self.create_header(
            title=partition.display_name,
            subtitle=f"Partition device: {partition.path}",
            show_back=True
        )

        scroll = self.create_scrollable_content()
        container = scroll.interior

        sec_overview = SectionHeader(container, "Partition Information", "Technical and filesystem parameters")
        sec_overview.pack(fill='x', pady=(0, 10))

        info_box = tk.Frame(container, bg=ForensiDriveTheme.COLORS['BG_CARD'])
        info_box.pack(fill='x', pady=(0, 20), padx=5, ipady=10, ipadx=15)

        InfoRow(info_box, "Partition Name:", partition.name).pack(fill='x', pady=3)
        InfoRow(info_box, "Device Path:", partition.path, mono=True).pack(fill='x', pady=3)
        InfoRow(info_box, "Capacity:", f"{partition.size_human} ({partition.size:,} bytes)").pack(fill='x', pady=3)
        InfoRow(info_box, "Filesystem Format:", partition.filesystem or "Unknown / Unformatted").pack(fill='x', pady=3)
        InfoRow(info_box, "Volume Label:", partition.label or "None").pack(fill='x', pady=3)
        InfoRow(info_box, "Unique ID (UUID):", partition.uuid or "None", mono=True).pack(fill='x', pady=3)
        
        status_str = f"Yes (Open at: {partition.mountpoint})" if partition.is_mounted else "No (Closed / Safe to access)"
        InfoRow(info_box, "Files Currently Accessible:", status_str).pack(fill='x', pady=3)
        InfoRow(info_box, "Parent Drive:", partition.parent_device or "Unknown").pack(fill='x', pady=3)
