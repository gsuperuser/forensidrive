import tkinter as tk
from .theme import ForensiDriveTheme

class NotificationManager:
    def __init__(self, parent: tk.Tk):
        self.parent = parent
        self.notifications = {}
        self._next_id = 1

    def _get_color(self, level):
        colors = {
            'info': ForensiDriveTheme.COLORS['ACCENT_BLUE'],
            'success': ForensiDriveTheme.COLORS['ACCENT_GREEN'],
            'warning': ForensiDriveTheme.COLORS['ACCENT_ORANGE'],
            'error': ForensiDriveTheme.COLORS['ACCENT_RED']
        }
        return colors.get(level, ForensiDriveTheme.COLORS['ACCENT_BLUE'])

    def show_toast(self, message, level='info', duration=3000):
        win = tk.Toplevel(self.parent)
        win.overrideredirect(True)
        win.attributes('-topmost', True)
        
        bg_color = self._get_color(level)
        frame = tk.Frame(win, bg=bg_color, bd=1, relief=tk.RAISED)
        frame.pack(fill='both', expand=True)
        
        lbl = tk.Label(frame, text=message, font=ForensiDriveTheme.FONTS['BODY'], bg=bg_color, fg='#ffffff', padx=20, pady=10)
        lbl.pack()
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (win.winfo_width() // 2)
        y = 50
        win.geometry(f"+{x}+{y}")
        
        self.parent.after(duration, win.destroy)

    def show_persistent(self, message, level='info', dismiss_text='OK'):
        notif_id = self._next_id
        self._next_id += 1
        
        win = tk.Toplevel(self.parent)
        win.overrideredirect(True)
        win.attributes('-topmost', True)
        
        bg_color = self._get_color(level)
        frame = tk.Frame(win, bg=bg_color, bd=1, relief=tk.RAISED)
        frame.pack(fill='both', expand=True)
        
        lbl = tk.Label(frame, text=message, font=ForensiDriveTheme.FONTS['BODY'], bg=bg_color, fg='#ffffff', padx=20, pady=10)
        lbl.pack(side='left')
        
        btn = tk.Button(frame, text=dismiss_text, command=lambda: self.dismiss(notif_id), bg=bg_color, fg='#ffffff', relief=tk.FLAT, bd=0, activebackground=bg_color)
        btn.pack(side='right', padx=10)
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (win.winfo_width() // 2)
        y = 50 + (len(self.notifications) * 50)
        win.geometry(f"+{x}+{y}")
        
        self.notifications[notif_id] = win
        return notif_id

    def dismiss(self, notification_id):
        if notification_id in self.notifications:
            self.notifications[notification_id].destroy()
            del self.notifications[notification_id]

    def clear_all(self):
        for win in self.notifications.values():
            win.destroy()
        self.notifications.clear()
