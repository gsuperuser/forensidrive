import tkinter as tk
from tkinter import ttk
from .theme import ForensiDriveTheme
import time

class ActionCard(tk.Frame):
    def __init__(self, parent, title, description, icon, command, color=None):
        if color is None:
            color = ForensiDriveTheme.COLORS['ACCENT_BLUE']
        super().__init__(parent, bg=ForensiDriveTheme.COLORS['BG_CARD'], cursor="hand2")
        self.command = command
        self.color = color
        
        self.grid_columnconfigure(1, weight=1)
        self.config(height=120)
        self.grid_propagate(False)
        
        self.icon_lbl = tk.Label(self, text=icon, font=("Helvetica", 32), bg=self['bg'], fg=self.color)
        self.icon_lbl.grid(row=0, column=0, rowspan=2, padx=ForensiDriveTheme.SPACING['PAD_LARGE'], pady=ForensiDriveTheme.SPACING['PAD_LARGE'], sticky='w')
        
        self.title_lbl = tk.Label(self, text=title, font=ForensiDriveTheme.FONTS['HEADING_SMALL'], bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'], anchor='w', justify='left')
        self.title_lbl.grid(row=0, column=1, sticky='sw', padx=(0, ForensiDriveTheme.SPACING['PAD_LARGE']), pady=(ForensiDriveTheme.SPACING['PAD_LARGE'], 0))
        
        self.desc_lbl = tk.Label(self, text=description, font=ForensiDriveTheme.FONTS['BODY_SMALL'], bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_SECONDARY'], anchor='nw', justify='left', wraplength=400)
        self.desc_lbl.grid(row=1, column=1, sticky='nw', padx=(0, ForensiDriveTheme.SPACING['PAD_LARGE']), pady=(5, ForensiDriveTheme.SPACING['PAD_LARGE']))
        
        for w in (self, self.icon_lbl, self.title_lbl, self.desc_lbl):
            w.bind("<Enter>", self.on_enter)
            w.bind("<Leave>", self.on_leave)
            w.bind("<Button-1>", self.on_click)
            
    def on_enter(self, event):
        self.config(bg=ForensiDriveTheme.COLORS['BG_HOVER'])
        self.icon_lbl.config(bg=ForensiDriveTheme.COLORS['BG_HOVER'])
        self.title_lbl.config(bg=ForensiDriveTheme.COLORS['BG_HOVER'])
        self.desc_lbl.config(bg=ForensiDriveTheme.COLORS['BG_HOVER'])

    def on_leave(self, event):
        self.config(bg=ForensiDriveTheme.COLORS['BG_CARD'])
        self.icon_lbl.config(bg=ForensiDriveTheme.COLORS['BG_CARD'])
        self.title_lbl.config(bg=ForensiDriveTheme.COLORS['BG_CARD'])
        self.desc_lbl.config(bg=ForensiDriveTheme.COLORS['BG_CARD'])
        
    def on_click(self, event):
        if self.command:
            self.command()

class DriveCard(tk.Frame):
    def __init__(self, parent, drive, on_select=None):
        super().__init__(parent, bg=ForensiDriveTheme.COLORS['BG_CARD'], cursor="hand2")
        self.drive = drive
        self.on_select = on_select
        
        self.grid_columnconfigure(1, weight=1)
        
        def _get_val(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        is_removable = bool(_get_val(drive, 'removable', False))
        icon = '💾' if is_removable else '🖴'
        
        self.icon_lbl = tk.Label(self, text=icon, font=("Helvetica", 24), bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'])
        self.icon_lbl.grid(row=0, column=0, rowspan=3, padx=ForensiDriveTheme.SPACING['PAD_MEDIUM'], pady=ForensiDriveTheme.SPACING['PAD_MEDIUM'], sticky='n')
        
        model = _get_val(drive, 'model', 'Unknown Device') or 'Unknown Device'
        vendor = _get_val(drive, 'vendor', '') or ''
        name_text = f"{vendor} {model}".strip() if vendor else model
        
        self.name_lbl = tk.Label(self, text=name_text, font=ForensiDriveTheme.FONTS['HEADING_SMALL'], bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'])
        self.name_lbl.grid(row=0, column=1, sticky='w', padx=ForensiDriveTheme.SPACING['PAD_SMALL'], pady=(ForensiDriveTheme.SPACING['PAD_SMALL'], 0))
        
        size_str = _get_val(drive, 'size_human', None) or str(_get_val(drive, 'size', 'Unknown'))
        path_str = _get_val(drive, 'path', 'Unknown')
        info_text = f"{size_str} - {path_str}"
        if is_removable:
            info_text += " (Removable)"
        if _get_val(drive, 'is_boot_device', False):
            info_text += " [System Live Media]"
        
        self.info_lbl = tk.Label(self, text=info_text, font=ForensiDriveTheme.FONTS['BODY_SMALL'], bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_SECONDARY'])
        self.info_lbl.grid(row=1, column=1, sticky='w', padx=ForensiDriveTheme.SPACING['PAD_SMALL'])
        
        partitions = _get_val(drive, 'partitions', []) or []
        parts_text = f"{len(partitions)} partition(s)"
        self.parts_lbl = tk.Label(self, text=parts_text, font=ForensiDriveTheme.FONTS['BODY_SMALL'], bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_MUTED'])
        self.parts_lbl.grid(row=2, column=1, sticky='w', padx=ForensiDriveTheme.SPACING['PAD_SMALL'], pady=(0, ForensiDriveTheme.SPACING['PAD_SMALL']))
        
        for w in (self, self.icon_lbl, self.name_lbl, self.info_lbl, self.parts_lbl):
            w.bind("<Enter>", self.on_enter)
            w.bind("<Leave>", self.on_leave)
            w.bind("<Button-1>", self.on_click)
            
    def on_enter(self, event):
        self.config(bg=ForensiDriveTheme.COLORS['BG_HOVER'])
        self.icon_lbl.config(bg=ForensiDriveTheme.COLORS['BG_HOVER'])
        self.name_lbl.config(bg=ForensiDriveTheme.COLORS['BG_HOVER'])
        self.info_lbl.config(bg=ForensiDriveTheme.COLORS['BG_HOVER'])
        self.parts_lbl.config(bg=ForensiDriveTheme.COLORS['BG_HOVER'])

    def on_leave(self, event):
        self.config(bg=ForensiDriveTheme.COLORS['BG_CARD'])
        self.icon_lbl.config(bg=ForensiDriveTheme.COLORS['BG_CARD'])
        self.name_lbl.config(bg=ForensiDriveTheme.COLORS['BG_CARD'])
        self.info_lbl.config(bg=ForensiDriveTheme.COLORS['BG_CARD'])
        self.parts_lbl.config(bg=ForensiDriveTheme.COLORS['BG_CARD'])
        
    def on_click(self, event):
        if self.on_select:
            self.on_select(self.drive)

class StatusBar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=ForensiDriveTheme.COLORS['BG_SECONDARY'], height=30)
        self.pack_propagate(False)
        self.status_label = tk.Label(self, text="Ready", font=ForensiDriveTheme.FONTS['BODY_SMALL'], bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'])
        self.status_label.pack(side='left', padx=ForensiDriveTheme.SPACING['PAD_MEDIUM'], pady=2)
        
    def set_status(self, message, level='info'):
        colors = {
            'info': ForensiDriveTheme.COLORS['ACCENT_BLUE'],
            'success': ForensiDriveTheme.COLORS['ACCENT_GREEN'],
            'warning': ForensiDriveTheme.COLORS['ACCENT_ORANGE'],
            'error': ForensiDriveTheme.COLORS['ACCENT_RED']
        }
        self.status_label.config(text=message, fg=colors.get(level, ForensiDriveTheme.COLORS['TEXT_PRIMARY']))

    def clear(self):
        self.set_status("Ready", 'info')

class ProgressPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=ForensiDriveTheme.COLORS['BG_CARD'])
        self.grid_columnconfigure(0, weight=1)
        
        self.message_lbl = tk.Label(self, text="Waiting...", font=ForensiDriveTheme.FONTS['BODY'], bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'])
        self.message_lbl.grid(row=0, column=0, sticky='w', padx=ForensiDriveTheme.SPACING['PAD_MEDIUM'], pady=(ForensiDriveTheme.SPACING['PAD_MEDIUM'], 5))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky='ew', padx=ForensiDriveTheme.SPACING['PAD_MEDIUM'], pady=5)
        
        self.stats_frame = tk.Frame(self, bg=self['bg'])
        self.stats_frame.grid(row=2, column=0, sticky='ew', padx=ForensiDriveTheme.SPACING['PAD_MEDIUM'], pady=(0, ForensiDriveTheme.SPACING['PAD_MEDIUM']))
        self.stats_frame.grid_columnconfigure(1, weight=1)
        
        self.pct_lbl = tk.Label(self.stats_frame, text="0%", font=ForensiDriveTheme.FONTS['BODY_SMALL'], bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_SECONDARY'])
        self.pct_lbl.grid(row=0, column=0, sticky='w')
        
        self.time_lbl = tk.Label(self.stats_frame, text="00:00:00", font=ForensiDriveTheme.FONTS['BODY_SMALL'], bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_SECONDARY'])
        self.time_lbl.grid(row=0, column=2, sticky='e')
        
        self.cancel_btn = tk.Button(self, text="Cancel", command=self.on_cancel)
        ForensiDriveTheme.style_button(self.cancel_btn, 'secondary')
        self.cancel_btn.grid(row=1, column=1, rowspan=2, padx=ForensiDriveTheme.SPACING['PAD_MEDIUM'])
        
        self.start_time = None
        self.cancel_cb = None

    def set_cancel_callback(self, cb):
        self.cancel_cb = cb
        
    def on_cancel(self):
        if self.cancel_cb:
            self.cancel_cb()

    def start(self, message):
        self.start_time = time.time()
        self.message_lbl.config(text=message, fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'])
        self.progress_var.set(0)
        self.pct_lbl.config(text="0%")
        self.time_lbl.config(text="00:00:00")
        
    def update(self, progress, message):
        self.progress_var.set(progress)
        self.message_lbl.config(text=message)
        self.pct_lbl.config(text=f"{int(progress)}%")
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            mins, secs = divmod(elapsed, 60)
            hours, mins = divmod(mins, 60)
            self.time_lbl.config(text=f"{hours:02d}:{mins:02d}:{secs:02d}")
            
    def complete(self, message):
        self.message_lbl.config(text=message, fg=ForensiDriveTheme.COLORS['ACCENT_GREEN'])
        self.progress_var.set(100)
        self.pct_lbl.config(text="100%")
        
    def fail(self, message):
        self.message_lbl.config(text=message, fg=ForensiDriveTheme.COLORS['ACCENT_RED'])
        
    def reset(self):
        self.start_time = None
        self.message_lbl.config(text="Waiting...", fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'])
        self.progress_var.set(0)
        self.pct_lbl.config(text="0%")
        self.time_lbl.config(text="00:00:00")

class TechnicalDetails(tk.Frame):
    def __init__(self, parent, label='Technical details'):
        super().__init__(parent, bg=ForensiDriveTheme.COLORS['BG_PRIMARY'])
        self.expanded = False
        
        self.header_frame = tk.Frame(self, bg=self['bg'], cursor="hand2")
        self.header_frame.pack(fill='x')
        
        self.icon_lbl = tk.Label(self.header_frame, text="▶", font=ForensiDriveTheme.FONTS['BODY_SMALL'], bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_SECONDARY'])
        self.icon_lbl.pack(side='left')
        
        self.title_lbl = tk.Label(self.header_frame, text=label, font=ForensiDriveTheme.FONTS['BODY_SMALL'], bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_SECONDARY'])
        self.title_lbl.pack(side='left', padx=5)
        
        self.content_frame = tk.Frame(self, bg=self['bg'])
        
        self.text_widget = tk.Text(self.content_frame, height=5, bg=ForensiDriveTheme.COLORS['BG_CARD'], fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'], font=ForensiDriveTheme.FONTS['MONO_SMALL'], wrap='word', bd=1, relief=tk.FLAT)
        self.text_widget.pack(fill='both', expand=True, padx=ForensiDriveTheme.SPACING['PAD_MEDIUM'], pady=5)
        
        for w in (self.header_frame, self.icon_lbl, self.title_lbl):
            w.bind("<Button-1>", lambda e: self.toggle())
            
    def set_content(self, text):
        self.text_widget.config(state='normal')
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert('1.0', text)
        self.text_widget.config(state='disabled')
        
    def toggle(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.icon_lbl.config(text="▼")
            self.content_frame.pack(fill='both', expand=True)
        else:
            self.icon_lbl.config(text="▶")
            self.content_frame.pack_forget()

class InfoRow(tk.Frame):
    def __init__(self, parent, label, value, mono=False):
        super().__init__(parent, bg=parent.cget('bg'))
        self.grid_columnconfigure(1, weight=1)
        
        lbl = tk.Label(self, text=label, bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_SECONDARY'], font=ForensiDriveTheme.FONTS['BODY_SMALL'])
        lbl.grid(row=0, column=0, sticky='w', pady=2, padx=(0, 10))
        
        val_font = ForensiDriveTheme.FONTS['MONO'] if mono else ForensiDriveTheme.FONTS['BODY']
        val = tk.Label(self, text=value, bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'], font=val_font)
        val.grid(row=0, column=1, sticky='w', pady=2)

class SectionHeader(tk.Frame):
    def __init__(self, parent, title, subtitle=None):
        super().__init__(parent, bg=parent.cget('bg'))
        
        t_lbl = tk.Label(self, text=title, font=ForensiDriveTheme.FONTS['HEADING'], bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'])
        t_lbl.pack(anchor='w', pady=(ForensiDriveTheme.SPACING['PAD_LARGE'], 5))
        
        if subtitle:
            s_lbl = tk.Label(self, text=subtitle, font=ForensiDriveTheme.FONTS['BODY'], bg=self['bg'], fg=ForensiDriveTheme.COLORS['TEXT_SECONDARY'])
            s_lbl.pack(anchor='w', pady=(0, ForensiDriveTheme.SPACING['PAD_MEDIUM']))

class ScrollableFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=ForensiDriveTheme.COLORS['BG_PRIMARY'])
        
        self.canvas = tk.Canvas(self, bg=self['bg'], bd=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        self.interior = tk.Frame(self.canvas, bg=self['bg'])
        self.interior.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.interior, anchor="nw", tags="window")
        self.canvas.bind("<Configure>", self._configure_canvas)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        
    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.itemconfigure("window", width=self.canvas.winfo_width())

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
