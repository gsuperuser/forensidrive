import tkinter as tk
import threading
from typing import List

from app.ui.navigation import BasePage
from app.ui.theme import ForensiDriveTheme
from app.ui.widgets import DriveCard, SectionHeader
from app.core.storage import detect_drives
from app.models.drive import Drive
from app.ui.dialogs import show_error, show_warning

class ErasurePage(BasePage):
    """Step 1 of Data Erasure: Select drive to erase."""

    def build(self):
        preselected_drive = self.kwargs.get('drive')
        if preselected_drive:
            self.after(50, lambda: self._on_drive_selected(preselected_drive))
            return

        self.create_header(
            title="Erase Data",
            subtitle="Choose the storage drive you want to permanently erase",
            show_back=True
        )

        scroll = self.create_scrollable_content()
        self.list_container = scroll.interior

        # Prominent Safety Warning Banner
        warn_frame = tk.Frame(self.list_container, bg=ForensiDriveTheme.COLORS['BG_CARD'], bd=2, relief=tk.SOLID)
        warn_frame.pack(fill='x', pady=(0, 20), ipady=12, ipadx=15)

        warn_title = tk.Label(
            warn_frame,
            text="⚠️ CAUTION: PERMANENT DATA DESTRUCTION",
            font=ForensiDriveTheme.FONTS['HEADING_SMALL'],
            bg=warn_frame['bg'],
            fg=ForensiDriveTheme.COLORS['ACCENT_RED']
        )
        warn_title.pack(anchor='w')

        warn_desc = tk.Label(
            warn_frame,
            text="Erasing a drive permanently removes all files, partitions, and operating systems on it. "
                 "Once completed, this action CANNOT be undone. Please ensure you select the correct drive.",
            font=ForensiDriveTheme.FONTS['BODY'],
            bg=warn_frame['bg'],
            fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'],
            wraplength=650,
            justify='left'
        )
        warn_desc.pack(anchor='w', pady=(5, 0))

        self._load_drives()

    def _load_drives(self):
        loading = tk.Label(
            self.list_container,
            text="Scanning for connected drives...",
            font=ForensiDriveTheme.FONTS['BODY'],
            bg=self['bg'],
            fg=ForensiDriveTheme.COLORS['TEXT_SECONDARY']
        )
        loading.pack(pady=30)

        def worker():
            try:
                drives = detect_drives()
                self.after(0, lambda: self._display_drives(drives))
            except Exception as e:
                self.after(0, lambda: self._handle_error(e))

        threading.Thread(target=worker, daemon=True).start()

    def _display_drives(self, drives: List[Drive]):
        for widget in self.list_container.winfo_children()[1:]: # Keep warning banner
            widget.destroy()

        if not drives:
            empty_lbl = tk.Label(
                self.list_container,
                text="No storage drives detected.",
                font=ForensiDriveTheme.FONTS['BODY'],
                bg=self['bg'],
                fg=ForensiDriveTheme.COLORS['TEXT_MUTED']
            )
            empty_lbl.pack(pady=40)
            return

        header = SectionHeader(self.list_container, "Select Target Drive to Erase", "Click on the drive you wish to sanitize")
        header.pack(fill='x', pady=(0, 15))

        for drive in drives:
            card = DriveCard(self.list_container, drive, on_select=self._on_drive_selected)
            card.pack(fill='x', pady=5)

    def _on_drive_selected(self, drive: Drive):
        if drive.is_boot_device:
            show_warning(
                self,
                "Protected System Drive",
                f"The drive '{drive.name}' ({drive.path}) contains the active SystemRescue live environment or boot filesystem.\n\n"
                "To prevent system crash, erasing the active live boot drive is prohibited."
            )
            return

        if drive.read_only:
            show_warning(
                self,
                "Read-Only Storage",
                f"The drive '{drive.name}' is marked as hardware read-only and cannot be modified or erased."
            )
            return

        self.nav.navigate_to('erase_methods', drive=drive)

    def _handle_error(self, exc: Exception):
        for widget in self.list_container.winfo_children()[1:]:
            widget.destroy()
        tech = getattr(exc, 'technical_details', str(exc))
        show_error(self, "Drive Detection Error", "We couldn't inspect connected drives.", tech)
