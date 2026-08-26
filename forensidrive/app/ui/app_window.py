import tkinter as tk
from .theme import ForensiDriveTheme
from .navigation import NavigationManager
from .notifications import NotificationManager
from .widgets import StatusBar
from .dialogs import show_confirmation

# Imports for pages and core process manager
from app.modules.dashboard.dashboard import DashboardPage
from app.modules.inspection.inspection import InspectionPage
from app.modules.inspection.drive_details import DriveDetailsPage
from app.modules.inspection.partition_details import PartitionDetailsPage
from app.modules.recovery.recovery import RecoveryPage
from app.modules.recovery.recovery_tools import RecoveryToolsPage
from app.modules.recovery.recovery_scan import RecoveryScanPage
from app.modules.recovery.recovery_results import RecoveryResultsPage
from app.modules.erasure.erasure import ErasurePage
from app.modules.erasure.erase_methods import EraseMethodsPage
from app.modules.erasure.confirmation import EraseConfirmationPage
from app.modules.erasure.erase_progress import EraseProgressPage
from app.core.process import ProcessManager
from app.core.system import get_system_info
from app.ui.dialogs import show_info

class ForensiDriveApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('ForensiDrive')
        
        # Maximize in Linux
        try:
            self.root.attributes('-zoomed', True)
        except Exception:
            # Fallback for Windows
            try:
                self.root.state('zoomed')
            except:
                pass
                
        ForensiDriveTheme.apply_to_root(self.root)
        
        self.process_manager = ProcessManager()
        
        # Top Bar
        self.top_bar = tk.Frame(self.root, bg=ForensiDriveTheme.COLORS['BG_SECONDARY'], height=50)
        self.top_bar.pack(side='top', fill='x')
        self.top_bar.pack_propagate(False)
        
        self.app_title = tk.Label(self.top_bar, text="ForensiDrive", font=ForensiDriveTheme.FONTS['HEADING'], bg=self.top_bar['bg'], fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'])
        self.app_title.pack(side='left', padx=ForensiDriveTheme.SPACING['PAD_LARGE'])
        
        self.sys_info_btn = tk.Button(self.top_bar, text="System Info", command=self.show_system_info)
        ForensiDriveTheme.style_button(self.sys_info_btn, 'secondary')
        self.sys_info_btn.pack(side='right', padx=ForensiDriveTheme.SPACING['PAD_LARGE'])
        
        # Status Bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side='bottom', fill='x')
        
        # Main Content
        self.content_area = tk.Frame(self.root, bg=ForensiDriveTheme.COLORS['BG_PRIMARY'])
        self.content_area.pack(side='top', fill='both', expand=True)
        
        # Managers
        self.nav = NavigationManager(self.content_area)
        self.notifications = NotificationManager(self.root)
        
        # Register pages
        pages = {
            'dashboard': DashboardPage,
            'inspection': InspectionPage,
            'drive_details': DriveDetailsPage,
            'partition_details': PartitionDetailsPage,
            'recovery': RecoveryPage,
            'recovery_tools': RecoveryToolsPage,
            'recovery_scan': RecoveryScanPage,
            'recovery_results': RecoveryResultsPage,
            'erasure': ErasurePage,
            'erase_methods': EraseMethodsPage,
            'erase_confirm': EraseConfirmationPage,
            'erase_progress': EraseProgressPage
        }
        
        for name, cls in pages.items():
            self.nav.register_page(name, cls)
            
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Navigate to dashboard
        self.nav.navigate_to('dashboard')
        
    def show_system_info(self):
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
        show_info(self.root, "System Information", "Current System Environment", details)

    def on_close(self):
        if show_confirmation(self.root, "Exit ForensiDrive", "Are you sure you want to exit? Any active operations may be interrupted."):
            if hasattr(self.process_manager, 'cleanup'):
                self.process_manager.cleanup()
            self.root.destroy()
