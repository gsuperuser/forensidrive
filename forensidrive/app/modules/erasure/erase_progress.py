import tkinter as tk
from app.ui.navigation import BasePage
from app.ui.theme import ForensiDriveTheme
from app.ui.widgets import ProgressPanel, TechnicalDetails, InfoRow, SectionHeader
from app.ui.dialogs import show_confirmation
from app.models.drive import Drive
from app.models.operation import Operation
from app.integrations.erasure_tools import ErasureToolAdapter
from app.core.commands import run_command_async

class EraseProgressPage(BasePage):
    """Step 4 of Erasure: Active drive sanitization in progress."""

    def build(self):
        self.drive: Drive = self.kwargs.get('drive')
        self.method: ErasureToolAdapter = self.kwargs.get('method')

        self.create_header(
            title="Erasing Storage Drive",
            subtitle="Please do not disconnect the drive or power off the system",
            show_back=False
        )

        scroll = self.create_scrollable_content()
        container = scroll.interior

        # Summary box
        summary = tk.Frame(container, bg=ForensiDriveTheme.COLORS['BG_CARD'])
        summary.pack(fill='x', pady=(0, 20), padx=5, ipady=8, ipadx=12)
        InfoRow(summary, "Target Drive:", self.drive.display_name).pack(fill='x', pady=2)
        InfoRow(summary, "Device Location:", self.drive.path, mono=True).pack(fill='x', pady=2)
        InfoRow(summary, "Sanitization Method:", self.method.name).pack(fill='x', pady=2)

        # Progress Panel
        self.progress_panel = ProgressPanel(container)
        self.progress_panel.pack(fill='x', pady=(0, 20), padx=5)
        self.progress_panel.set_cancel_callback(self._on_cancel_requested)

        # Warning text
        warn_lbl = tk.Label(
            container,
            text="⚠️ CAUTION: Overwrite operation in progress. Interrupting this process may leave the drive unreadable or in an inconsistent state.",
            font=ForensiDriveTheme.FONTS['BODY_SMALL'],
            bg=self['bg'],
            fg=ForensiDriveTheme.COLORS['ACCENT_ORANGE'],
            wraplength=650,
            justify='left'
        )
        warn_lbl.pack(anchor='w', padx=5, pady=(0, 15))

        # Technical Output Details
        self.tech_details = TechnicalDetails(container, label="Show Live Overwrite Log")
        self.tech_details.pack(fill='both', expand=True, padx=5, pady=(0, 20))

        # Results area (initially hidden)
        self.result_container = tk.Frame(container, bg=self['bg'])
        self.result_container.pack(fill='x', pady=(10, 30))

        self.operation = Operation(
            operation_type="erasure",
            target_device=self.drive.path
        )
        self.operation.start("Preparing drive sanitization...")
        self.progress_panel.start("Starting erasure...")

        self.log_lines = []
        self.proc = None
        self._start_process()

    def _start_process(self):
        try:
            cmd = self.method.build_command(self.drive.path, {})
            self._append_log(f"Executing: {' '.join(cmd)}\n")

            self.proc = run_command_async(
                cmd,
                on_output=self._on_output,
                on_complete=self._on_complete,
                on_error=self._on_error
            )
        except Exception as e:
            self._on_error(e)

    def _on_output(self, line: str):
        self.after(0, lambda: self._process_output_line(line))

    def _process_output_line(self, line: str):
        self._append_log(line)
        parsed = self.method.parse_output(line)
        msg = parsed.get("message", "Overwriting data...")
        prog = parsed.get("progress", 0.0)
        if prog >= 0:
            self.progress_panel.update(prog, msg)
        else:
            self.progress_panel.update(50.0, msg)

    def _append_log(self, text: str):
        self.log_lines.append(text)
        if len(self.log_lines) > 500:
            self.log_lines.pop(0)
        self.tech_details.set_content("".join(self.log_lines))

    def _on_complete(self, returncode: int):
        self.after(0, lambda: self._handle_completion(returncode))

    def _handle_completion(self, returncode: int):
        if returncode == 0:
            self.operation.complete("The drive has been successfully erased.")
            self.progress_panel.complete("Erasure complete.")
            self._show_final_ui(success=True)
        else:
            self.operation.fail(
                "The erasure could not be completed.",
                "".join(self.log_lines[-20:])
            )
            self.progress_panel.fail("Erasure encountered errors.")
            self._show_final_ui(success=False)

    def _on_error(self, exc: Exception):
        self.after(0, lambda: self._handle_error_ui(exc))

    def _handle_error_ui(self, exc: Exception):
        tech = getattr(exc, 'technical_details', str(exc))
        self.operation.fail("We couldn't complete the erasure operation.", tech)
        self.progress_panel.fail("Operation failed.")
        self._show_final_ui(success=False)

    def _on_cancel_requested(self):
        if show_confirmation(self, "Interrupt Erasure?", "Are you sure you want to stop the erasure? The drive will be left partially wiped and unusable until reformatted."):
            if self.proc:
                try:
                    self.proc.terminate()
                except Exception:
                    pass
            self.operation.cancel("Erasure was interrupted by user.")
            self.progress_panel.fail("Interrupted.")
            self._show_final_ui(success=False, interrupted=True)

    def _show_final_ui(self, success: bool, interrupted: bool = False):
        for w in self.result_container.winfo_children():
            w.destroy()

        if success:
            res_card = tk.Frame(self.result_container, bg=ForensiDriveTheme.COLORS['BG_CARD'])
            res_card.pack(fill='x', pady=(10, 20), ipady=12, ipadx=12)
            lbl = tk.Label(
                res_card,
                text="✅ The storage drive has been erased successfully.",
                font=ForensiDriveTheme.FONTS['HEADING_SMALL'],
                bg=res_card['bg'],
                fg=ForensiDriveTheme.COLORS['ACCENT_GREEN']
            )
            lbl.pack(anchor='w')
        elif interrupted:
            res_card = tk.Frame(self.result_container, bg=ForensiDriveTheme.COLORS['BG_CARD'])
            res_card.pack(fill='x', pady=(10, 20), ipady=12, ipadx=12)
            lbl = tk.Label(
                res_card,
                text="⏹️ Erasure was interrupted. The drive is in an incomplete state.",
                font=ForensiDriveTheme.FONTS['HEADING_SMALL'],
                bg=res_card['bg'],
                fg=ForensiDriveTheme.COLORS['ACCENT_ORANGE']
            )
            lbl.pack(anchor='w')
        else:
            res_card = tk.Frame(self.result_container, bg=ForensiDriveTheme.COLORS['BG_CARD'])
            res_card.pack(fill='x', pady=(10, 20), ipady=12, ipadx=12)
            lbl = tk.Label(
                res_card,
                text="❌ We couldn't complete the erasure operation.",
                font=ForensiDriveTheme.FONTS['HEADING_SMALL'],
                bg=res_card['bg'],
                fg=ForensiDriveTheme.COLORS['ACCENT_RED']
            )
            lbl.pack(anchor='w')

        btn_row = tk.Frame(self.result_container, bg=self['bg'])
        btn_row.pack(fill='x')

        dash_btn = tk.Button(
            btn_row,
            text="🏠 Return to Dashboard",
            command=lambda: self.nav.navigate_to('dashboard')
        )
        ForensiDriveTheme.style_button(dash_btn, 'primary')
        dash_btn.pack(side='left', padx=(0, 15))

        another_btn = tk.Button(
            btn_row,
            text="🗑️ Erase Another Drive",
            command=lambda: self.nav.navigate_to('erasure')
        )
        ForensiDriveTheme.style_button(another_btn, 'secondary')
        another_btn.pack(side='left')
