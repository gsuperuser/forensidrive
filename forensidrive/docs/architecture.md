# Architecture Documentation

## Layer Diagram
1. **UI Layer (Tkinter)** - Presents the visual control layer to the user (`app/ui/`).
2. **Modules Layer** - Represents functional areas like Inspection, Recovery, Erasure (`app/modules/` or `app/core/`).
3. **Core Layer** - Models for Drives and Partitions, utility functions (`app/models/`).
4. **Integrations Layer** - Subprocess callers and wrappers for external tools (`app/utils/`).
5. **SystemRescue OS Layer** - The base environment providing the underlying utilities (lsblk, shred, ddrescue).

## Module Descriptions
- **Inspection**: Discovers and visualizes connected block devices.
- **Recovery**: Interfaces with tools like `photorec` and `ddrescue` for file carving and imaging.
- **Erasure**: Securely wipes data using `shred` or `wipefs`.

## Data Flow
- User clicks "Refresh" -> Core calls `lsblk -J` via subprocess -> Core parses JSON -> Models instantiated -> UI updates list.

## Safety Mechanisms
- **Boot Device Protection**: Hardcoded checks and sysfs checks to prevent wiping `/dev/sda` or the live USB.
- **Confirmation Dialogs**: Required for destructive operations (erasure, overwrite).
- **Read-Only Defaults**: Drives are mounted read-only for inspection and source recovery.

## Error Handling Strategy
- Python exceptions from subprocess calls are caught.
- Errors are wrapped into user-friendly strings.
- Stack traces/raw output are hidden behind an expandable "Technical details" button in the UI.

## Adding New Tools
1. Define a new Tool Adapter in `app/adapters/`.
2. Implement the `is_available()`, `build_command()`, and `parse_output()` methods.
3. Register the adapter in the respective module registry.
