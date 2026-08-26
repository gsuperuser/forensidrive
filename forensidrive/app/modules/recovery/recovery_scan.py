import tkinter as tk
import os
from app.ui.navigation import BasePage
from app.ui.theme import ForensiDriveTheme
from app.ui.widgets import ProgressPanel, TechnicalDetails, InfoRow
from app.ui.dialogs import show_confirmation
from app.models.drive import Drive
from app.models.operation import Operation
from app.integrations.recovery_tools import RecoveryToolAdapter
from app.core.commands import run_command_async

class RecoveryScanPage(BasePage):
    """Step 3 of Recovery: Active scan and file recovery in progress."""

    def build(self):
        self.drive: Drive = self.kwargs.get('drive')
        self.tool: RecoveryToolAdapter = self.kwargs.get('tool')
        self.destination: str = self.kwargs.get('destination')

        self.create_header(
            title="File Recovery in Progress",
            subtitle="Please wait while we scan and extract your files",
            show_back=False
        )

        scroll = self.create_scrollable_content()
        container = scroll.interior

        # Summary box
        summary = tk.Frame(container, bg=ForensiDriveTheme.COLORS['BG_CARD'])
        summary.pack(fill='x', pady=(0, 20), padx=5, ipady=8, ipadx=12)
        InfoRow(summary, "Source Drive:", self.drive.display_name).pack(fill='x', pady=2)
        InfoRow(summary, "Recovery Method:", self.tool.name).pack(fill='x', pady=2)
        InfoRow(summary, "Destination:", self.destination).pack(fill='x', pady=2)

        # Progress Panel
        self.progress_panel = ProgressPanel(container)
        self.progress_panel.pack(fill='x', pady=(0, 20), padx=5)
        self.progress_panel.set_cancel_callback(self._on_cancel_requested)

        # Technical Output Details
        self.tech_details = TechnicalDetails(container, label="Show Live Tool Log")
        self.tech_details.pack(fill='both', expand=True, padx=5, pady=(0, 20))

        self.operation = Operation(
            operation_type="recovery",
            target_device=self.drive.path
        )
        self.operation.start("Initializing scan...")
        self.progress_panel.start("Starting recovery...")

        self.log_lines = []
        self.proc = None
        self._start_process()

    def _start_process(self):
        try:
            cmd = self.tool.build_command(self.drive.path, self.destination, {})
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
        parsed = self.tool.parse_output(line)
        msg = parsed.get("message", "Recovering files...")
        prog = parsed.get("progress", 0.0)
        if prog >= 0:
            self.progress_panel.update(prog, msg)
        else:
            self.progress_panel.update(50.0, msg)

    def _append_log(self, text: str):
        self.log_lines.append(text)
        if len(self.log_lines) > 500:
            self.log_lines.pop(0)
        full_text = "".join(self.log_lines)
        self.tech_details.set_content(full_text)

    def _on_complete(self, returncode: int):
        self.after(0, lambda: self._handle_completion(returncode))

    def _handle_completion(self, returncode: int):
        if returncode == 0:
            self.operation.complete("Recovery completed successfully.")
        else:
            self.operation.fail(
                "Recovery ended with warnings or partial results.",
                "".join(self.log_lines[-20:])
            )
        self.nav.navigate_to('recovery_results', operation=self.operation, destination=self.destination)

    def _on_error(self, exc: Exception):
        self.after(0, lambda: self._handle_error_ui(exc))

    def _handle_error_ui(self, exc: Exception):
        tech = getattr(exc, 'technical_details', str(exc))
        self.operation.fail("We couldn't complete the file recovery.", tech)
        self.nav.navigate_to('recovery_results', operation=self.operation, destination=self.destination)

    def _on_cancel_requested(self):
        if show_confirmation(self, "Stop Recovery?", "Are you sure you want to stop the recovery process? Any files recovered so far will remain."):
            if self.proc:
                try:
                    self.proc.terminate()
                except Exception:
                    pass
            self.operation.cancel("Recovery was stopped by the user.")
            self.nav.navigate_to('recovery_results', operation=self.operation, destination=self.destination)
