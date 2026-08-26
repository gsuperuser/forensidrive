import subprocess
import threading
import uuid
import time
from typing import Dict, Optional, Callable, Any

class ProcessManager:
    """Manages background child processes, streaming logs and handling cancellations."""
    def __init__(self):
        self._processes: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def start_process(
        self,
        args: list,
        on_output: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[int], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ) -> str:
        proc_id = str(uuid.uuid4())
        
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            shell=False
        )

        with self._lock:
            self._processes[proc_id] = {
                "process": proc,
                "args": args,
                "started_at": time.time(),
                "running": True,
                "returncode": None
            }

        def worker():
            try:
                for line in iter(proc.stdout.readline, ''):
                    if line and on_output:
                        on_output(line)
                proc.stdout.close()
                rc = proc.wait()
                with self._lock:
                    if proc_id in self._processes:
                        self._processes[proc_id]["running"] = False
                        self._processes[proc_id]["returncode"] = rc
                if on_complete:
                    on_complete(rc)
            except Exception as e:
                with self._lock:
                    if proc_id in self._processes:
                        self._processes[proc_id]["running"] = False
                if on_error:
                    on_error(e)

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        return proc_id

    def cancel_process(self, proc_id: str) -> bool:
        with self._lock:
            info = self._processes.get(proc_id)
            if not info or not info["running"]:
                return False
            proc: subprocess.Popen = info["process"]

        try:
            proc.terminate()
            time.sleep(0.5)
            if proc.poll() is None:
                proc.kill()
            with self._lock:
                if proc_id in self._processes:
                    self._processes[proc_id]["running"] = False
                    self._processes[proc_id]["returncode"] = -1
            return True
        except Exception:
            return False

    def is_running(self, proc_id: str) -> bool:
        with self._lock:
            info = self._processes.get(proc_id)
            return bool(info and info["running"])

    def get_process(self, proc_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._processes.get(proc_id)

    def cleanup(self):
        with self._lock:
            for proc_id, info in list(self._processes.items()):
                if info["running"]:
                    try:
                        info["process"].terminate()
                    except Exception:
                        pass
