import shutil
import subprocess
import threading
from dataclasses import dataclass
from typing import List, Optional, Callable

from app.core.errors import (
    CommandNotFoundError,
    CommandFailedError,
    PermissionDeniedError,
    OperationTimeoutError,
    ForensiDriveError
)

@dataclass
class CommandResult:
    stdout: str
    stderr: str
    returncode: int

    @property
    def success(self) -> bool:
        return self.returncode == 0

def find_command(name: str) -> Optional[str]:
    return shutil.which(name)

def require_command(name: str) -> str:
    path = find_command(name)
    if not path:
        raise CommandNotFoundError(name)
    return path

def run_command(
    args: List[str],
    timeout: int = 60,
    capture: bool = True,
    check: bool = True
) -> CommandResult:
    """Safely run a command without shell=True, capturing outputs and translating errors."""
    if not args:
        raise ForensiDriveError("No command specified.")

    cmd_name = args[0]
    if not find_command(cmd_name) and not cmd_name.startswith("/"):
        raise CommandNotFoundError(cmd_name)

    try:
        proc = subprocess.run(
            args,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            text=True,
            timeout=timeout,
            shell=False
        )
        
        result = CommandResult(
            stdout=proc.stdout or "",
            stderr=proc.stderr or "",
            returncode=proc.returncode
        )

        if check and not result.success:
            tech_detail = f"Command: {' '.join(args)}\nExit Code: {result.returncode}\nStderr: {result.stderr}\nStdout: {result.stdout}"
            raise CommandFailedError(
                user_message="We couldn't complete this operation.",
                technical_details=tech_detail
            )

        return result

    except FileNotFoundError:
        raise CommandNotFoundError(cmd_name)
    except subprocess.TimeoutExpired as e:
        raise OperationTimeoutError(
            user_message="The operation took too long and was stopped.",
            technical_details=f"Command '{' '.join(args)}' timed out after {timeout} seconds."
        )
    except PermissionError as e:
        raise PermissionDeniedError(
            user_message="Administrative privileges are required for this action.",
            technical_details=str(e)
        )
    except Exception as e:
        if isinstance(e, ForensiDriveError):
            raise
        raise CommandFailedError(
            user_message="We encountered an unexpected problem while executing the command.",
            technical_details=str(e)
        )

def run_command_async(
    args: List[str],
    on_output: Optional[Callable[[str], None]] = None,
    on_complete: Optional[Callable[[int], None]] = None,
    on_error: Optional[Callable[[Exception], None]] = None
) -> subprocess.Popen:
    """Run command asynchronously, streaming output in a background daemon thread."""
    cmd_name = args[0]
    if not find_command(cmd_name) and not cmd_name.startswith("/"):
        err = CommandNotFoundError(cmd_name)
        if on_error:
            on_error(err)
        raise err

    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        shell=False
    )

    def monitor():
        try:
            for line in iter(proc.stdout.readline, ''):
                if line and on_output:
                    on_output(line)
            proc.stdout.close()
            proc.wait()
            if on_complete:
                on_complete(proc.returncode)
        except Exception as e:
            if on_error:
                on_error(e)

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    return proc
