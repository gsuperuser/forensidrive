class ForensiDriveError(Exception):
    """Base error class for ForensiDrive with user-friendly and technical messages."""
    def __init__(self, user_message: str = "An unexpected issue occurred.", technical_details: str = ""):
        super().__init__(user_message)
        self.user_message = user_message
        self.technical_details = technical_details

class CommandNotFoundError(ForensiDriveError):
    def __init__(self, command: str, technical_details: str = ""):
        user_message = f"The required system tool '{command}' is not available on this system."
        super().__init__(user_message, technical_details or f"Command '{command}' not found in PATH.")

class CommandFailedError(ForensiDriveError):
    def __init__(self, user_message: str = "We couldn't complete this operation.", technical_details: str = ""):
        super().__init__(user_message, technical_details)

class DeviceNotFoundError(ForensiDriveError):
    def __init__(self, device_path: str, technical_details: str = ""):
        user_message = f"The storage drive ({device_path}) is no longer accessible. It may have been disconnected."
        super().__init__(user_message, technical_details or f"Device path '{device_path}' does not exist.")

class PermissionDeniedError(ForensiDriveError):
    def __init__(self, user_message: str = "Administrative privileges are required for this action.", technical_details: str = ""):
        super().__init__(user_message, technical_details)

class DeviceBusyError(ForensiDriveError):
    def __init__(self, device_path: str, technical_details: str = ""):
        user_message = f"The storage drive ({device_path}) is currently in use. Please close any files or folders on it."
        super().__init__(user_message, technical_details or f"Device '{device_path}' is busy or has mounted partitions.")

class OperationCancelledError(ForensiDriveError):
    def __init__(self, user_message: str = "The operation was cancelled by the user.", technical_details: str = ""):
        super().__init__(user_message, technical_details)

class OperationTimeoutError(ForensiDriveError):
    def __init__(self, user_message: str = "The operation took too long and was stopped.", technical_details: str = ""):
        super().__init__(user_message, technical_details)
