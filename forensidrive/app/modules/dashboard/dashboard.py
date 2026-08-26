import tkinter as tk
from app.ui.navigation import BasePage
from app.ui.theme import ForensiDriveTheme
from app.ui.widgets import ActionCard
from app.core.system import get_system_info
from app.ui.dialogs import show_info

class DashboardPage(BasePage):
    """Main landing dashboard offering core forensic and recovery actions."""
    
    def build(self):
        self.create_header(
            title="ForensiDrive",
            subtitle="Choose what you want to do with your connected drives",
            show_back=False
        )

        content = tk.Frame(self, bg=self['bg'])
        content.pack(fill='both', expand=True, padx=ForensiDriveTheme.SPACING['PAD_LARGE'], pady=ForensiDriveTheme.SPACING['PAD_LARGE'])

        # 2x2 grid layout
        content.grid_columnconfigure(0, weight=1, uniform="dash_cols")
        content.grid_columnconfigure(1, weight=1, uniform="dash_cols")
        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        # 1. Recover Files
        card_recover = ActionCard(
            content,
            title="Recover Files",
            description="Find and recover deleted or lost files from a storage drive",
            icon="🔄",
            command=lambda: self.nav.navigate_to('recovery'),
            color=ForensiDriveTheme.COLORS['ACCENT_GREEN']
        )
        card_recover.grid(row=0, column=0, padx=ForensiDriveTheme.SPACING['PAD_MEDIUM'], pady=ForensiDriveTheme.SPACING['PAD_MEDIUM'], sticky="nsew")

        # 2. Erase Data
        card_erase = ActionCard(
            content,
            title="Erase Data",
            description="Permanently and safely remove all data from a storage drive",
            icon="🗑️",
            command=lambda: self.nav.navigate_to('erasure'),
            color=ForensiDriveTheme.COLORS['ACCENT_RED']
        )
        card_erase.grid(row=0, column=1, padx=ForensiDriveTheme.SPACING['PAD_MEDIUM'], pady=ForensiDriveTheme.SPACING['PAD_MEDIUM'], sticky="nsew")

        # 3. Inspect Drive
        card_inspect = ActionCard(
            content,
            title="Inspect Drive",
            description="View detailed information about connected drives and their health",
            icon="🔍",
            command=lambda: self.nav.navigate_to('inspection'),
            color=ForensiDriveTheme.COLORS['ACCENT_BLUE']
        )
        card_inspect.grid(row=1, column=0, padx=ForensiDriveTheme.SPACING['PAD_MEDIUM'], pady=ForensiDriveTheme.SPACING['PAD_MEDIUM'], sticky="nsew")

        # 4. System Information
        card_sysinfo = ActionCard(
            content,
            title="System Information",
            description="View information about this system rescue environment and tools",
            icon="ℹ️",
            command=self._show_sys_info,
            color=ForensiDriveTheme.COLORS['ACCENT_PURPLE']
        )
        card_sysinfo.grid(row=1, column=1, padx=ForensiDriveTheme.SPACING['PAD_MEDIUM'], pady=ForensiDriveTheme.SPACING['PAD_MEDIUM'], sticky="nsew")

    def _show_sys_info(self):
        info = get_system_info()
        details = (
            f"SystemRescue: {info.get('systemrescue_version')}\n"
            f"Linux Kernel: {info.get('kernel_version')}\n"
            f"Architecture: {info.get('cpu_arch')}\n"
            f"Total RAM: {info.get('total_ram')}\n"
            f"Available RAM: {info.get('available_ram')}\n"
            f"Boot Mode: {info.get('boot_mode')}\n"
            f"ForensiDrive: {info.get('app_version')}"
        )
        show_info(self, "System Information", "Current System Environment", details)
