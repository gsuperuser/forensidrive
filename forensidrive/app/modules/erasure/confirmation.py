import tkinter as tk
from app.ui.navigation import BasePage
from app.ui.theme import ForensiDriveTheme
from app.ui.widgets import InfoRow, SectionHeader
from app.models.drive import Drive
from app.integrations.erasure_tools import ErasureToolAdapter

class EraseConfirmationPage(BasePage):
    """Step 3 of Erasure: Strict multi-step verification and typing confirmation."""

    def build(self):
        self.drive: Drive = self.kwargs.get('drive')
        self.method: ErasureToolAdapter = self.kwargs.get('method')

        if not self.drive or not self.method:
            self.create_header(title="Confirm Erasure", subtitle="Missing parameters", show_back=True)
            return

        self.create_header(
            title="⚠️ Final Confirmation Before Erasure",
            subtitle="Please carefully verify the target drive and confirm your intent",
            show_back=True
        )

        scroll = self.create_scrollable_content()
        container = scroll.interior

        # Danger Banner
        danger_box = tk.Frame(container, bg=ForensiDriveTheme.COLORS['BG_CARD'], bd=2, relief=tk.SOLID)
        danger_box.pack(fill='x', pady=(0, 20), ipady=12, ipadx=15)

        d_title = tk.Label(
            danger_box,
            text="🚨 IRREVERSIBLE OPERATION",
            font=ForensiDriveTheme.FONTS['HEADING_SMALL'],
            bg=danger_box['bg'],
            fg=ForensiDriveTheme.COLORS['ACCENT_RED']
        )
        d_title.pack(anchor='w')

        d_desc = tk.Label(
            danger_box,
            text="You are about to permanently erase all data, filesystems, and partitions on this storage drive. "
                 "Nobody will be able to recover data from this drive after this procedure finishes.",
            font=ForensiDriveTheme.FONTS['BODY'],
            bg=danger_box['bg'],
            fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'],
            wraplength=650,
            justify='left'
        )
        d_desc.pack(anchor='w', pady=(5, 0))

        # Target Drive Identity Verification
        sec_id = SectionHeader(container, "1. Verify Storage Drive Identity", "Confirm this is indeed the drive you wish to sanitize")
        sec_id.pack(fill='x', pady=(0, 10))

        info_box = tk.Frame(container, bg=ForensiDriveTheme.COLORS['BG_CARD'])
        info_box.pack(fill='x', pady=(0, 20), padx=5, ipady=8, ipadx=12)
        InfoRow(info_box, "Drive Model:", self.drive.model or "Unknown").pack(fill='x', pady=2)
        InfoRow(info_box, "Manufacturer / Vendor:", self.drive.vendor or "Unknown").pack(fill='x', pady=2)
        InfoRow(info_box, "Capacity:", self.drive.size_human).pack(fill='x', pady=2)
        InfoRow(info_box, "Device Location:", self.drive.path, mono=True).pack(fill='x', pady=2)
        InfoRow(info_box, "Selected Method:", f"{self.method.name} ({self.method.risk_level.upper()} Risk)").pack(fill='x', pady=2)

        # Safety Checklists
        sec_check = SectionHeader(container, "2. Acknowledge Risks", "Check each box to confirm you understand the consequences")
        sec_check.pack(fill='x', pady=(0, 10))

        check_box = tk.Frame(container, bg=ForensiDriveTheme.COLORS['BG_CARD'])
        check_box.pack(fill='x', pady=(0, 20), padx=5, ipady=12, ipadx=12)

        self.cb1_var = tk.BooleanVar(value=False)
        self.cb2_var = tk.BooleanVar(value=False)
        self.cb3_var = tk.BooleanVar(value=False)

        cb1 = tk.Checkbutton(
            check_box,
            text="I understand that ALL existing files and partitions on this drive will be destroyed.",
            variable=self.cb1_var,
            command=self._validate_confirmation,
            font=ForensiDriveTheme.FONTS['BODY'],
            bg=check_box['bg'],
            fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'],
            selectcolor=ForensiDriveTheme.COLORS['BG_PRIMARY'],
            activebackground=check_box['bg'],
            activeforeground=ForensiDriveTheme.COLORS['TEXT_PRIMARY']
        )
        cb1.pack(anchor='w', pady=4)

        cb2 = tk.Checkbutton(
            check_box,
            text=f"I have verified that the device path is {self.drive.path} and not another drive.",
            variable=self.cb2_var,
            command=self._validate_confirmation,
            font=ForensiDriveTheme.FONTS['BODY'],
            bg=check_box['bg'],
            fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'],
            selectcolor=ForensiDriveTheme.COLORS['BG_PRIMARY'],
            activebackground=check_box['bg'],
            activeforeground=ForensiDriveTheme.COLORS['TEXT_PRIMARY']
        )
        cb2.pack(anchor='w', pady=4)

        cb3 = tk.Checkbutton(
            check_box,
            text="I understand that this action is permanent and cannot be cancelled once writing starts.",
            variable=self.cb3_var,
            command=self._validate_confirmation,
            font=ForensiDriveTheme.FONTS['BODY'],
            bg=check_box['bg'],
            fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'],
            selectcolor=ForensiDriveTheme.COLORS['BG_PRIMARY'],
            activebackground=check_box['bg'],
            activeforeground=ForensiDriveTheme.COLORS['TEXT_PRIMARY']
        )
        cb3.pack(anchor='w', pady=4)

        # Type Confirmation
        sec_type = SectionHeader(container, "3. Type Drive Name to Confirm", f"Type exactly '{self.drive.name}' in the box below to unlock the erase button")
        sec_type.pack(fill='x', pady=(0, 10))

        type_box = tk.Frame(container, bg=ForensiDriveTheme.COLORS['BG_CARD'])
        type_box.pack(fill='x', pady=(0, 20), padx=5, ipady=12, ipadx=12)

        self.type_entry_var = tk.StringVar()
        self.type_entry_var.trace_add("write", lambda *args: self._validate_confirmation())

        self.entry = tk.Entry(
            type_box,
            textvariable=self.type_entry_var,
            font=ForensiDriveTheme.FONTS['HEADING_SMALL'],
            bg=ForensiDriveTheme.COLORS['BG_PRIMARY'],
            fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'],
            insertbackground=ForensiDriveTheme.COLORS['TEXT_PRIMARY'],
            width=20
        )
        self.entry.pack(anchor='w', pady=5)

        # Erase Action Button
        btn_box = tk.Frame(container, bg=self['bg'])
        btn_box.pack(fill='x', pady=(10, 30))

        self.erase_btn = tk.Button(
            btn_box,
            text=f"🗑️ Permanently Erase {self.drive.path}",
            command=self._execute_erase,
            state=tk.DISABLED
        )
        ForensiDriveTheme.style_button(self.erase_btn, 'danger')
        self.erase_btn.pack(side='left', padx=5)

    def _validate_confirmation(self):
        c1 = self.cb1_var.get()
        c2 = self.cb2_var.get()
        c3 = self.cb3_var.get()
        typed = self.type_entry_var.get().strip()
        expected = self.drive.name.strip()

        if c1 and c2 and c3 and typed == expected:
            self.erase_btn.config(state=tk.NORMAL)
        else:
            self.erase_btn.config(state=tk.DISABLED)

    def _execute_erase(self):
        self.nav.navigate_to('erase_progress', drive=self.drive, method=self.method)
