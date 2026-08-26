import tkinter as tk
from app.ui.navigation import BasePage
from app.ui.theme import ForensiDriveTheme
from app.ui.widgets import InfoRow, SectionHeader
from app.ui.dialogs import show_warning
from app.models.drive import Drive
from app.integrations.erasure_tools import ErasureToolRegistry, ErasureToolAdapter

class EraseMethodsPage(BasePage):
    """Step 2 of Erasure: Select sanitization method."""

    def build(self):
        self.drive: Drive = self.kwargs.get('drive')
        if not self.drive:
            self.create_header(title="Choose Erasure Method", subtitle="No drive selected", show_back=True)
            return

        self.create_header(
            title="Choose Erasure Method",
            subtitle=f"Target: {self.drive.display_name}",
            show_back=True
        )

        scroll = self.create_scrollable_content()
        container = scroll.interior

        # Drive Summary Box
        info_box = tk.Frame(container, bg=ForensiDriveTheme.COLORS['BG_CARD'])
        info_box.pack(fill='x', pady=(0, 20), padx=5, ipady=8, ipadx=12)
        InfoRow(info_box, "Target Drive:", self.drive.display_name).pack(fill='x', pady=2)
        InfoRow(info_box, "Device Location:", self.drive.path, mono=True).pack(fill='x', pady=2)
        InfoRow(info_box, "Capacity:", self.drive.size_human).pack(fill='x', pady=2)

        # Available Methods
        registry = ErasureToolRegistry()
        self.available_tools = registry.get_available_tools()
        self.selected_method = self.available_tools[0] if self.available_tools else None

        sec_methods = SectionHeader(
            container,
            "Available Sanitization Methods",
            "Choose how thoroughly you want to erase the data from this drive"
        )
        sec_methods.pack(fill='x', pady=(0, 10))

        if not self.available_tools:
            no_tools = tk.Label(
                container,
                text="No erasure utilities (shred, wipefs, blkdiscard, dd) are available on this system.",
                font=ForensiDriveTheme.FONTS['BODY'],
                bg=self['bg'],
                fg=ForensiDriveTheme.COLORS['ACCENT_RED']
            )
            no_tools.pack(anchor='w', padx=10, pady=10)
            return

        for tool in self.available_tools:
            card = self._create_method_card(container, tool)
            card.pack(fill='x', pady=5, padx=5)

        # Continue Button
        btn_frame = tk.Frame(container, bg=self['bg'])
        btn_frame.pack(fill='x', pady=(20, 30))

        cont_btn = tk.Button(
            btn_frame,
            text="Continue to Confirmation →",
            command=self._continue_to_confirm
        )
        ForensiDriveTheme.style_button(cont_btn, 'primary')
        cont_btn.pack(side='left', padx=5)

    def _create_method_card(self, parent, tool: ErasureToolAdapter) -> tk.Frame:
        card = tk.Frame(parent, bg=ForensiDriveTheme.COLORS['BG_CARD'], cursor="hand2")
        is_selected = (tool == self.selected_method)
        if is_selected:
            card.config(bg=ForensiDriveTheme.COLORS['BG_HOVER'])

        title_frame = tk.Frame(card, bg=card['bg'])
        title_frame.pack(fill='x', padx=12, pady=(10, 4))

        ind = "◉ " if is_selected else "○ "
        ind_lbl = tk.Label(title_frame, text=ind, font=ForensiDriveTheme.FONTS['HEADING_SMALL'], bg=card['bg'], fg=ForensiDriveTheme.COLORS['ACCENT_BLUE'] if is_selected else ForensiDriveTheme.COLORS['TEXT_MUTED'])
        ind_lbl.pack(side='left')

        name_lbl = tk.Label(title_frame, text=tool.name, font=ForensiDriveTheme.FONTS['HEADING_SMALL'], bg=card['bg'], fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'])
        name_lbl.pack(side='left', padx=5)

        # Risk badge
        risk_color = {
            'low': ForensiDriveTheme.COLORS['ACCENT_GREEN'],
            'medium': ForensiDriveTheme.COLORS['ACCENT_ORANGE'],
            'high': ForensiDriveTheme.COLORS['ACCENT_RED'],
            'extreme': ForensiDriveTheme.COLORS['ACCENT_RED']
        }.get(tool.risk_level, ForensiDriveTheme.COLORS['TEXT_MUTED'])

        badge = tk.Label(title_frame, text=f" Risk Level: {tool.risk_level.upper()} ", font=ForensiDriveTheme.FONTS['BODY_SMALL'], bg=ForensiDriveTheme.COLORS['BG_PRIMARY'], fg=risk_color)
        badge.pack(side='right')

        desc_lbl = tk.Label(card, text=tool.description, font=ForensiDriveTheme.FONTS['BODY'], bg=card['bg'], fg=ForensiDriveTheme.COLORS['TEXT_SECONDARY'], wraplength=620, justify='left')
        desc_lbl.pack(anchor='w', padx=12, pady=(0, 4))

        warn_text = tool.get_warning_message()
        if warn_text:
            w_lbl = tk.Label(card, text=f"• {warn_text}", font=ForensiDriveTheme.FONTS['BODY_SMALL'], bg=card['bg'], fg=ForensiDriveTheme.COLORS['ACCENT_ORANGE'], wraplength=620, justify='left')
            w_lbl.pack(anchor='w', padx=12, pady=(0, 10))

        def select():
            self.selected_method = tool
            self.nav.navigate_to('erase_methods', drive=self.drive)

        for w in (card, title_frame, ind_lbl, name_lbl, desc_lbl):
            w.bind("<Button-1>", lambda e: select())

        return card

    def _continue_to_confirm(self):
        if not self.selected_method:
            show_warning(self, "Method Required", "Please select an erasure method to continue.")
            return

        self.nav.navigate_to('erase_confirm', drive=self.drive, method=self.selected_method)
