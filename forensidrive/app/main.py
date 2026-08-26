import sys
import os
import tkinter as tk

# Ensure app package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Also handle running from project root
if os.path.basename(os.getcwd()) == 'ForensiDrive':
    sys.path.insert(0, os.getcwd())

from app.ui.app_window import ForensiDriveApp

def main():
    root = tk.Tk()
    app = ForensiDriveApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
