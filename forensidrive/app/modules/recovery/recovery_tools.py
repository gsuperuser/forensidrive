import tkinter as tk
import os
from app.ui.navigation import BasePage
from app.ui.theme import ForensiDriveTheme
from app.ui.widgets import InfoRow, SectionHeader
from app.ui.dialogs import choose_directory, show_warning
from app.integrations.recovery_tools import RecoveryToolRegistry, RecoveryToolAdapter
from app.models.drive import Drive
from app.core.filesystem import get_available_space

class RecoveryToolsPage(BasePage):
    """Step 2 of Recovery: Select recovery tool and destination folder."""

    def build(self):
        self.drive: Drive = self.kwargs.get('drive')
        if not self.drive:
            self.create_header(title="Recovery Options", subtitle="No drive selected", show_back=True)
            return

        self.create_header(
            title="Recovery Options",
            subtitle=f"Target: {self.drive.display_name}",
            show_back=True
        )

        scroll = self.create_scrollable_content()
        container = scroll.interior

        # 1. Drive summary
        info_box = tk.Frame(container, bg=ForensiDriveTheme.COLORS['BG_CARD'])
        info_box.pack(fill='x', pady=(0, 20), padx=5, ipady=8, ipadx=12)
        InfoRow(info_box, "Source Drive:", self.drive.display_name).pack(fill='x', pady=2)
        InfoRow(info_box, "Device Location:", self.drive.path, mono=True).pack(fill='x', pady=2)

        # 2. Available Recovery Tools
        registry = RecoveryToolRegistry()
        self.available_tools = registry.get_available_tools()
        self.selected_tool = self.available_tools[0] if self.available_tools else None

        sec_tools = SectionHeader(container, "Choose Recovery Method", "Select which tool to use for scanning and recovering your files")
        sec_tools.pack(fill='x', pady=(0, 10))

        self.tool_cards = []
        if not self.available_tools:
            no_tools = tk.Label(
                container,
                text="No recovery utilities (such as PhotoRec, Foremost, ddrescue) are installed on this system.",
                font=ForensiDriveTheme.FONTS['BODY'],
                bg=self['bg'],
                fg=ForensiDriveTheme.COLORS['ACCENT_ORANGE']
            )
            no_tools.pack(anchor='w', padx=10, pady=10)
        else:
            for tool in self.available_tools:
                card = self._create_tool_card(container, tool)
                card.pack(fill='x', pady=4, padx=5)

        # 3. Choose Destination Folder
        sec_dest = SectionHeader(container, "Choose Where to Save Recovered Files", "Select a safe destination folder (preferably on a different drive)")
        sec_dest.pack(fill='x', pady=(20, 10))

        dest_frame = tk.Frame(container, bg=ForensiDriveTheme.COLORS['BG_CARD'])
        dest_frame.pack(fill='x', pady=(0, 20), padx=5, ipady=12, ipadx=12)

        self.dest_path_var = tk.StringVar(value="")
        
        btn_choose = tk.Button(dest_frame, text="📁 Browse Destination Folder...", command=self._browse_destination)
        ForensiDriveTheme.style_button(btn_choose, 'secondary')
        btn_choose.pack(anchor='w', pady=(0, 10))

        self.dest_lbl = tk.Label(
            dest_frame,
            text="No folder selected yet.",
            font=ForensiDriveTheme.FONTS['BODY'],
            bg=dest_frame['bg'],
            fg=ForensiDriveTheme.COLORS['TEXT_MUTED']
        )
        self.dest_lbl.pack(anchor='w')

        self.space_lbl = tk.Label(
            dest_frame,
            text="",
            font=ForensiDriveTheme.FONTS['BODY_SMALL'],
            bg=dest_frame['bg'],
            fg=ForensiDriveTheme.COLORS['TEXT_SECONDARY']
        )
        self.space_lbl.pack(anchor='w', pady=(3, 0))

        # 4. Start Button
        self.start_btn = tk.Button(
            container,
            text="🚀 Start File Recovery",
            command=self._start_recovery,
            state=tk.DISABLED
        )
        ForensiDriveTheme.style_button(self.start_btn, 'success')
        self.start_btn.pack(anchor='w', padx=5, pady=(10, 30))

    def _create_tool_card(self, parent, tool: RecoveryToolAdapter) -> tk.Frame:
        card = tk.Frame(parent, bg=ForensiDriveTheme.COLORS['BG_CARD'], cursor="hand2")
        is_selected = (tool == self.selected_tool)
        if is_selected:
            card.config(bg=ForensiDriveTheme.COLORS['BG_HOVER'])

        title_frame = tk.Frame(card, bg=card['bg'])
        title_frame.pack(fill='x', padx=10, pady=(8, 2))

        indicator = "◉ " if is_selected else "○ "
        ind_lbl = tk.Label(title_frame, text=indicator, font=ForensiDriveTheme.FONTS['HEADING_SMALL'], bg=card['bg'], fg=ForensiDriveTheme.COLORS['ACCENT_GREEN'] if is_selected else ForensiDriveTheme.COLORS['TEXT_MUTED'])
        ind_lbl.pack(side='left')

        name_lbl = tk.Label(title_frame, text=tool.name, font=ForensiDriveTheme.FONTS['HEADING_SMALL'], bg=card['bg'], fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'])
        name_lbl.pack(side='left', padx=5)

        desc_lbl = tk.Label(card, text=tool.description, font=ForensiDriveTheme.FONTS['BODY_SMALL'], bg=card['bg'], fg=ForensiDriveTheme.COLORS['TEXT_SECONDARY'], wraplength=600, justify='left')
        desc_lbl.pack(anchor='w', padx=10, pady=(0, 8))

        def select():
            self.selected_tool = tool
            self.nav.navigate_to('recovery_tools', drive=self.drive)

        for w in (card, title_frame, ind_lbl, name_lbl, desc_lbl):
            w.bind("<Button-1>", lambda e: select())

        return card

    def _browse_destination(self):
        folder = choose_directory(self, "Choose where to save recovered files", initial_dir="/tmp")
        if folder:
            self.dest_path_var.set(folder)
            self.dest_lbl.config(text=f"Selected: {folder}", fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'])
            
            space_bytes = get_available_space(folder)
            from app.models.drive import Drive
            space_str = Drive.human_size(space_bytes)
            self.space_lbl.config(text=f"Available storage space at destination: {space_str}")

            if self.selected_tool:
                self.start_btn.config(state=tk.NORMAL)

    def _start_recovery(self):
        dest = self.dest_path_var.get()
        if not dest or not os.path.exists(dest):
            show_warning(self, "Destination Required", "Please select a valid folder to save recovered files.")
            return

        if not self.selected_tool:
            show_warning(self, "Tool Required", "Please select a recovery method.")
            return

        self.nav.navigate_to('recovery_scan', drive=self.drive, tool=self.selected_tool, destination=dest)
