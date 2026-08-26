import tkinter as tk
import threading
from typing import List

from app.ui.navigation import BasePage
from app.ui.theme import ForensiDriveTheme
from app.ui.widgets import DriveCard, SectionHeader
from app.core.storage import detect_drives
from app.models.drive import Drive
from app.ui.dialogs import show_error

class RecoveryPage(BasePage):
    """Step 1 of File Recovery: Select target storage drive."""

    def build(self):
        # If a drive was already passed, navigate to recovery tools directly
        preselected_drive = self.kwargs.get('drive')
        if preselected_drive:
            self.after(50, lambda: self.nav.navigate_to('recovery_tools', drive=preselected_drive))
            return

        self.create_header(
            title="Recover Files",
            subtitle="Choose the drive you want to recover lost or deleted files from",
            show_back=True
        )

        scroll = self.create_scrollable_content()
        self.list_container = scroll.interior

        self._load_drives()

    def _load_drives(self):
        loading = tk.Label(
            self.list_container,
            text="Searching for available drives...",
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
        for widget in self.list_container.winfo_children():
            widget.destroy()

        if not drives:
            empty_lbl = tk.Label(
                self.list_container,
                text="No storage drives detected. Please connect your drive and try again.",
                font=ForensiDriveTheme.FONTS['BODY'],
                bg=self['bg'],
                fg=ForensiDriveTheme.COLORS['TEXT_MUTED']
            )
            empty_lbl.pack(pady=40)
            return

        header = SectionHeader(self.list_container, "Select Source Drive", "Choose the drive containing the files you need to recover")
        header.pack(fill='x', pady=(0, 15))

        for drive in drives:
            card = DriveCard(self.list_container, drive, on_select=self._on_drive_selected)
            card.pack(fill='x', pady=5)

    def _on_drive_selected(self, drive: Drive):
        self.nav.navigate_to('recovery_tools', drive=drive)

    def _handle_error(self, exc: Exception):
        for widget in self.list_container.winfo_children():
            widget.destroy()
        tech = getattr(exc, 'technical_details', str(exc))
        show_error(self, "Drive Detection Error", "We couldn't check your connected storage drives.", tech)
