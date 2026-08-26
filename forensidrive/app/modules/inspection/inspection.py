import tkinter as tk
import threading
from typing import List

from app.ui.navigation import BasePage
from app.ui.theme import ForensiDriveTheme
from app.ui.widgets import DriveCard, SectionHeader
from app.core.storage import detect_drives
from app.models.drive import Drive
from app.ui.dialogs import show_error

class InspectionPage(BasePage):
    """Storage drive inspection listing page."""

    def build(self):
        self.create_header(
            title="Your Storage Drives",
            subtitle="These are the storage drives connected to this computer",
            show_back=True
        )

        controls_frame = tk.Frame(self, bg=self['bg'])
        controls_frame.pack(fill='x', padx=ForensiDriveTheme.SPACING['PAD_LARGE'], pady=(0, 10))

        refresh_btn = tk.Button(controls_frame, text="🔄 Refresh Drive List", command=self._refresh_drives)
        ForensiDriveTheme.style_button(refresh_btn, 'secondary')
        refresh_btn.pack(side='left')

        self.scroll = self.create_scrollable_content()
        self.list_container = self.scroll.interior

        self._refresh_drives()

    def _refresh_drives(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        loading_lbl = tk.Label(
            self.list_container,
            text="Checking connected storage drives...",
            font=ForensiDriveTheme.FONTS['BODY'],
            bg=self['bg'],
            fg=ForensiDriveTheme.COLORS['TEXT_SECONDARY']
        )
        loading_lbl.pack(pady=30)

        def worker():
            try:
                drives = detect_drives()
                self.after(0, lambda: self._display_drives(drives))
            except Exception as e:
                self.after(0, lambda: self._handle_error(e))

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _display_drives(self, drives: List[Drive]):
        for widget in self.list_container.winfo_children():
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

        header = SectionHeader(self.list_container, f"Detected Drives ({len(drives)})", "Click on any drive to inspect partitions and technical details.")
        header.pack(fill='x', pady=(0, 15))

        for drive in drives:
            card = DriveCard(self.list_container, drive, on_select=self._on_drive_selected)
            card.pack(fill='x', pady=5)

    def _on_drive_selected(self, drive: Drive):
        self.nav.navigate_to('drive_details', drive=drive)

    def _handle_error(self, exc: Exception):
        for widget in self.list_container.winfo_children():
            widget.destroy()
        tech = getattr(exc, 'technical_details', str(exc))
        show_error(self, "Drive Inspection Failed", "We couldn't inspect your storage drives.", tech)
