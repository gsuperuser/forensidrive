import tkinter as tk
from app.ui.navigation import BasePage
from app.ui.theme import ForensiDriveTheme
from app.ui.widgets import InfoRow, SectionHeader
from app.models.drive import Drive
from app.models.partition import Partition

class DriveDetailsPage(BasePage):
    """Detailed inspection of a specific storage drive and its partitions."""

    def build(self):
        drive: Drive = self.kwargs.get('drive')
        if not drive:
            self.create_header(title="Drive Details", subtitle="No drive selected", show_back=True)
            return

        self.create_header(
            title=drive.display_name,
            subtitle=f"Drive path: {drive.path}",
            show_back=True
        )

        scroll = self.create_scrollable_content()
        container = scroll.interior

        # Warning banner if boot device
        if drive.is_boot_device:
            warn_frame = tk.Frame(container, bg=ForensiDriveTheme.COLORS['BG_CARD'], bd=1, relief=tk.SOLID)
            warn_frame.pack(fill='x', pady=(0, 15), ipady=8, ipadx=10)
            warn_lbl = tk.Label(
                warn_frame,
                text="⚠️ Note: This drive contains the active SystemRescue live environment or boot system.",
                font=ForensiDriveTheme.FONTS['BODY'],
                bg=warn_frame['bg'],
                fg=ForensiDriveTheme.COLORS['ACCENT_ORANGE']
            )
            warn_lbl.pack(anchor='w')

        # 1. Drive Overview
        sec_overview = SectionHeader(container, "Drive Information", "Physical drive specifications and connectivity")
        sec_overview.pack(fill='x', pady=(0, 10))

        info_box = tk.Frame(container, bg=ForensiDriveTheme.COLORS['BG_CARD'])
        info_box.pack(fill='x', pady=(0, 20), padx=5, ipady=10, ipadx=15)

        InfoRow(info_box, "Manufacturer / Vendor:", drive.vendor or "Unknown").pack(fill='x', pady=3)
        InfoRow(info_box, "Model:", drive.model or "Unknown").pack(fill='x', pady=3)
        InfoRow(info_box, "Capacity:", f"{drive.size_human} ({drive.size:,} bytes)").pack(fill='x', pady=3)
        InfoRow(info_box, "Device Path:", drive.path, mono=True).pack(fill='x', pady=3)
        InfoRow(info_box, "Serial Number:", drive.serial or "Not available", mono=True).pack(fill='x', pady=3)
        InfoRow(info_box, "Connection Type:", (drive.transport or "Internal/Standard").upper()).pack(fill='x', pady=3)
        InfoRow(info_box, "Removable Media:", "Yes (e.g. USB drive)" if drive.removable else "No (Internal Drive)").pack(fill='x', pady=3)
        InfoRow(info_box, "Read-Only Hardware:", "Yes (Write-Protected)" if drive.read_only else "No (Read/Write)").pack(fill='x', pady=3)

        # 2. Partitions Section
        sec_parts = SectionHeader(container, f"Partitions ({len(drive.partitions)})", "Accessible sections on this drive")
        sec_parts.pack(fill='x', pady=(10, 10))

        if not drive.partitions:
            no_parts = tk.Label(
                container,
                text="No partitions found on this drive. It may be unformatted or raw storage.",
                font=ForensiDriveTheme.FONTS['BODY'],
                bg=self['bg'],
                fg=ForensiDriveTheme.COLORS['TEXT_MUTED']
            )
            no_parts.pack(anchor='w', padx=10, pady=10)
        else:
            for part in drive.partitions:
                self._render_partition_card(container, part)

        # 3. Actions
        sec_actions = SectionHeader(container, "Actions", "Choose what you want to do with this drive")
        sec_actions.pack(fill='x', pady=(20, 10))

        act_frame = tk.Frame(container, bg=self['bg'])
        act_frame.pack(fill='x', pady=(0, 20))

        recover_btn = tk.Button(
            act_frame,
            text="🔄 Recover Files from this Drive",
            command=lambda: self.nav.navigate_to('recovery_tools', drive=drive)
        )
        ForensiDriveTheme.style_button(recover_btn, 'success')
        recover_btn.pack(side='left', padx=(0, 15))

        erase_btn = tk.Button(
            act_frame,
            text="🗑️ Erase this Drive",
            command=lambda: self.nav.navigate_to('erase_methods', drive=drive)
        )
        ForensiDriveTheme.style_button(erase_btn, 'danger')
        erase_btn.pack(side='left')

    def _render_partition_card(self, parent, partition: Partition):
        card = tk.Frame(parent, bg=ForensiDriveTheme.COLORS['BG_CARD'], cursor="hand2")
        card.pack(fill='x', pady=4, padx=5, ipady=8, ipadx=10)

        title = f"{partition.name} - {partition.size_human}"
        if partition.label:
            title += f" [Label: {partition.label}]"
        
        lbl_title = tk.Label(card, text=title, font=ForensiDriveTheme.FONTS['HEADING_SMALL'], bg=card['bg'], fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'])
        lbl_title.pack(anchor='w')

        fs_text = f"Filesystem: {partition.filesystem or 'Unknown / Unformatted'}"
        if partition.mountpoint:
            fs_text += f" • Files accessible at: {partition.mountpoint}"
        else:
            fs_text += " • Not currently open"

        lbl_sub = tk.Label(card, text=fs_text, font=ForensiDriveTheme.FONTS['BODY_SMALL'], bg=card['bg'], fg=ForensiDriveTheme.COLORS['TEXT_SECONDARY'])
        lbl_sub.pack(anchor='w', pady=(3, 0))

        for w in (card, lbl_title, lbl_sub):
            w.bind("<Button-1>", lambda e: self.nav.navigate_to('partition_details', partition=partition))
            w.bind("<Enter>", lambda e, c=card: c.config(bg=ForensiDriveTheme.COLORS['BG_HOVER']))
            w.bind("<Leave>", lambda e, c=card: c.config(bg=ForensiDriveTheme.COLORS['BG_CARD']))
