from dataclasses import dataclass, field
import uuid
from datetime import datetime
from typing import Optional

@dataclass
class Operation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operation_type: str = "recovery"  # 'recovery', 'erasure', 'inspection'
    status: str = "pending"          # 'pending', 'running', 'completed', 'failed', 'cancelled'
    target_device: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    message: str = "Ready"
    technical_details: str = ""
    result_summary: str = ""

    def start(self, initial_message: str = "Starting operation..."):
        self.status = "running"
        self.started_at = datetime.now()
        self.progress = 0.0
        self.message = initial_message

    def complete(self, message: str = "The operation completed successfully.", summary: str = ""):
        self.status = "completed"
        self.completed_at = datetime.now()
        self.progress = 1.0
        self.message = message
        self.result_summary = summary or message

    def fail(self, user_message: str = "We couldn't complete this operation.", technical: str = ""):
        self.status = "failed"
        self.completed_at = datetime.now()
        self.message = user_message
        if technical:
            self.technical_details = f"{self.technical_details}\n{technical}".strip()

    def cancel(self, message: str = "Operation was cancelled."):
        self.status = "cancelled"
        self.completed_at = datetime.now()
        self.message = message

    def update_progress(self, progress: float, message: Optional[str] = None):
        self.progress = max(0.0, min(1.0, progress))
        if message:
            self.message = message
