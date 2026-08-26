# ForensiDrive

**ForensiDrive** is a specialized graphical control and orchestration layer designed to run directly on top of [SystemRescue Linux](https://www.system-rescue.org/) when booted from a live USB or ISO.

It serves as the primary user-facing interface for non-technical operators, abstracting complex Linux block device mechanics, mount operations, forensic file carving, and storage sanitization into a clean, safe, full-screen workflow.

---

## 📁 Complete Directory Tree

```
ForensiDrive/
│
├── app/
│   ├── main.py
│   ├── __init__.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── app_window.py
│   │   ├── navigation.py
│   │   ├── dialogs.py
│   │   ├── notifications.py
│   │   ├── widgets.py
│   │   └── theme.py
│   │
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── dashboard/
│   │   │   ├── __init__.py
│   │   │   └── dashboard.py
│   │   │
│   │   ├── inspection/
│   │   │   ├── __init__.py
│   │   │   ├── inspection.py
│   │   │   ├── drive_details.py
│   │   │   └── partition_details.py
│   │   │
│   │   ├── recovery/
│   │   │   ├── __init__.py
│   │   │   ├── recovery.py
│   │   │   ├── recovery_tools.py
│   │   │   ├── recovery_scan.py
│   │   │   └── recovery_results.py
│   │   │
│   │   └── erasure/
│   │       ├── __init__.py
│   │       ├── erasure.py
│   │       ├── erase_methods.py
│   │       ├── confirmation.py
│   │       └── erase_progress.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── storage.py
│   │   ├── partitions.py
│   │   ├── filesystem.py
│   │   ├── commands.py
│   │   ├── process.py
│   │   ├── system.py
│   │   └── errors.py
│   │
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── systemrescue.py
│   │   ├── recovery_tools.py
│   │   ├── erasure_tools.py
│   │   └── filesystem_tools.py
│   │
│   └── models/
│       ├── __init__.py
│       ├── drive.py
│       ├── partition.py
│       └── operation.py
│
├── systemrescue/
│   ├── config/
│   │   └── forensidrive.yaml
│   │
│   └── autostart/
│       └── forensidrive.desktop
│
├── customization/
│   ├── recipe/
│   ├── build/
│   └── scripts/
│
├── tests/
│   ├── test_storage.py
│   ├── test_inspection.py
│   ├── test_recovery.py
│   └── test_erasure.py
│
├── docs/
│   ├── architecture.md
│   ├── systemrescue.md
│   └── tools.md
│
└── README.md
```

---

## 🚀 How to Run Inside SystemRescue

ForensiDrive requires **Python 3** and **Tkinter**, using solely standard library modules (no pip or internet access needed).

### 1. Manual Launch from Terminal / Graphical Desktop
Open a terminal in XFCE and run:
```bash
cd /usr/local/forensidrive
python3 app/main.py
```
Or from your development checkout:
```bash
cd /path/to/ForensiDrive
python3 app/main.py
```

### 2. Live USB Autostart
When integrated into SystemRescue:
- Copy `systemrescue/autostart/forensidrive.desktop` to `/etc/xdg/autostart/forensidrive.desktop` or `~/.config/autostart/forensidrive.desktop`.
- On boot, XFCE initializes and immediately opens ForensiDrive in maximized mode.

---

## 🧪 Testing and Verification

Run the test suite offline with standard `unittest`:
```bash
python3 -m unittest discover tests
```

### 1. How to Test Inspection
- Launch ForensiDrive and click **[ Inspect Drive ]**.
- ForensiDrive executes `lsblk -J -b -o ...` to detect physical devices.
- It displays model, capacity, partition layout, mount status, and flags the live boot device with a warning badge.

### 2. How to Test Recovery Without Destroying Data
- **Preparation**:
  Create a temporary virtual image or plug in a test USB drive containing sample files.
  ```bash
  # Optional: Create a test filesystem with sample files
  dd if=/dev/zero of=/tmp/testdrive.img bs=1M count=64
  mkfs.ext4 /tmp/testdrive.img
  ```
- **Execution**:
  1. Click **[ Recover Files ]** on the dashboard.
  2. Select the target drive or loop device.
  3. Choose a recovery tool (e.g. `PhotoRec` or `Foremost`).
  4. Select a safe destination folder (e.g. `/tmp/recovered/`).
  5. Click **Start File Recovery**.
  6. Recovery runs in read-only mode, extracting carved files without modifying the source device.

### 3. How to Test Erasure Safely Using a Disposable Test Device
- **Safety Gate**: The live boot media is automatically detected and blocked from erasure.
- **Preparation**:
  Create a disposable loop block device:
  ```bash
  dd if=/dev/zero of=/tmp/disposable.img bs=1M count=100
  sudo losetup -fP /tmp/disposable.img
  ```
- **Execution**:
  1. Click **[ Erase Data ]**.
  2. Select the disposable loop device (e.g., `loop0`).
  3. Select an erasure method (`Shred`, `Wipefs`, `DD Zero Fill`, or `Block Discard`).
  4. Walk through the 3 safety checkboxes acknowledging permanent destruction.
  5. Type the exact short name of the device (e.g. `loop0`) to unlock the **Erase Drive** button.
  6. Monitor the real-time progress and verify data sanitization safely.

---

## 📦 Eventual ISO Integration Status

### Ready for Eventual ISO Integration
- **Clean Architecture**: Complete separation of UI, Models, Core Subprocess wrappers, and Tool Integrations.
- **Zero External Dependencies**: Standard library Python 3 + Tkinter only; offline-first design.
- **Path Portability**: Dynamic path resolution (`/usr/local/forensidrive/` or local directory).
- **SystemRescue Autostart**: Pre-configured `.desktop` XDG autostart file and YAML configuration file.
- **Safety Barriers**: Explicit boot device detection and multi-stage confirmation gates.

### Intentionally Deferred
- Audit logging database and cryptographic verification
- Password protection and user account tiers
- Encrypted audit and forensic evidence partitions
- Persistent credential management
