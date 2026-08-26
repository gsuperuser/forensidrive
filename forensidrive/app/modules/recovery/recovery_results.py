import tkinter as tk
import os
from app.ui.navigation import BasePage
from app.ui.theme import ForensiDriveTheme
from app.ui.widgets import TechnicalDetails, SectionHeader
from app.models.operation import Operation

class RecoveryResultsPage(BasePage):
    """Step 4 of Recovery: Summary of recovered files and status."""

    def build(self):
        operation: Operation = self.kwargs.get('operation')
        destination: str = self.kwargs.get('destination', '')

        is_success = operation and operation.status == 'completed'
        is_cancelled = operation and operation.status == 'cancelled'

        title = "Recovery Complete" if is_success else ("Recovery Stopped" if is_cancelled else "Recovery Notice")
        subtitle = "Here is the summary of your file recovery session"
        
        self.create_header(title=title, subtitle=subtitle, show_back=False)

        scroll = self.create_scrollable_content()
        container = scroll.interior

        # Status Card
        status_card = tk.Frame(container, bg=ForensiDriveTheme.COLORS['BG_CARD'])
        status_card.pack(fill='x', pady=(0, 20), padx=5, ipady=15, ipadx=15)

        if is_success:
            icon_text = "✅"
            msg_text = "The operation completed successfully."
            sub_msg = f"Recovered files have been saved to:\n{destination}"
            msg_color = ForensiDriveTheme.COLORS['ACCENT_GREEN']
        elif is_cancelled:
            icon_text = "⏹️"
            msg_text = "The recovery process was stopped."
            sub_msg = f"Any files saved before stopping are available at:\n{destination}"
            msg_color = ForensiDriveTheme.COLORS['ACCENT_ORANGE']
        else:
            icon_text = "⚠️"
            msg_text = operation.message if operation else "We couldn't complete this operation."
            sub_msg = "Please check the technical log below for details."
            msg_color = ForensiDriveTheme.COLORS['ACCENT_RED']

        lbl_icon = tk.Label(status_card, text=icon_text, font=("Helvetica", 36), bg=status_card['bg'])
        lbl_icon.pack(anchor='w', pady=(0, 5))

        lbl_main = tk.Label(status_card, text=msg_text, font=ForensiDriveTheme.FONTS['HEADING'], bg=status_card['bg'], fg=msg_color)
        lbl_main.pack(anchor='w')

        lbl_sub = tk.Label(status_card, text=sub_msg, font=ForensiDriveTheme.FONTS['BODY'], bg=status_card['bg'], fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'], justify='left')
        lbl_sub.pack(anchor='w', pady=(8, 0))

        # Files Count Summary if destination exists
        if destination and os.path.exists(destination):
            try:
                entries = os.listdir(destination)
                sec_files = SectionHeader(container, "Saved Content", f"{len(entries)} items saved in the recovery directory")
                sec_files.pack(fill='x', pady=(10, 5))
            except Exception:
                pass

        # Technical log
        if operation and operation.technical_details:
            tech = TechnicalDetails(container, label="Show Technical Session Details")
            tech.pack(fill='x', padx=5, pady=(10, 20))
            tech.set_content(operation.technical_details)

        # Action Buttons
        btn_frame = tk.Frame(container, bg=self['bg'])
        btn_frame.pack(fill='x', pady=(15, 30))

        dash_btn = tk.Button(
            btn_frame,
            text="🏠 Return to Dashboard",
            command=lambda: self.nav.navigate_to('dashboard')
        )
        ForensiDriveTheme.style_button(dash_btn, 'primary')
        dash_btn.pack(side='left', padx=(0, 15))

        another_btn = tk.Button(
            btn_frame,
            text="🔄 Recover More Files",
            command=lambda: self.nav.navigate_to('recovery')
        )
        ForensiDriveTheme.style_button(another_btn, 'secondary')
        another_btn.pack(side='left')
