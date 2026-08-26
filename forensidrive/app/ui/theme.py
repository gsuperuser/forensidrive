import tkinter as tk

class ForensiDriveTheme:
    COLORS = {
        'BG_PRIMARY': '#1a1a2e',
        'BG_SECONDARY': '#16213e',
        'BG_CARD': '#1f2b47',
        'BG_HOVER': '#2a3a5c',
        'TEXT_PRIMARY': '#e8e8e8',
        'TEXT_SECONDARY': '#a0a0b0',
        'TEXT_MUTED': '#6a6a7a',
        'ACCENT_BLUE': '#4a9eff',
        'ACCENT_GREEN': '#4ade80',
        'ACCENT_ORANGE': '#fb923c',
        'ACCENT_RED': '#ef4444',
        'ACCENT_PURPLE': '#a78bfa',
        'BORDER': '#2a3a5c',
        'SCROLLBAR': '#3a4a6c'
    }

    FONTS = {
        'HEADING_LARGE': ('Helvetica', 24, 'bold'),
        'HEADING': ('Helvetica', 18, 'bold'),
        'HEADING_SMALL': ('Helvetica', 14, 'bold'),
        'BODY': ('Helvetica', 12),
        'BODY_SMALL': ('Helvetica', 10),
        'MONO': ('Courier', 11),
        'MONO_SMALL': ('Courier', 9)
    }

    SPACING = {
        'PAD_SMALL': 5,
        'PAD_MEDIUM': 10,
        'PAD_LARGE': 20,
        'PAD_XL': 30,
        'BORDER_RADIUS': 8
    }

    @staticmethod
    def apply_to_root(root: tk.Tk):
        root.configure(bg=ForensiDriveTheme.COLORS['BG_PRIMARY'])

    @staticmethod
    def style_button(btn: tk.Button, style: str = 'primary'):
        colors = ForensiDriveTheme.COLORS
        bg = colors['ACCENT_BLUE']
        fg = '#ffffff'
        
        if style == 'success':
            bg = colors['ACCENT_GREEN']
            fg = '#000000'
        elif style == 'warning':
            bg = colors['ACCENT_ORANGE']
            fg = '#000000'
        elif style == 'danger':
            bg = colors['ACCENT_RED']
            fg = '#ffffff'
        elif style == 'secondary':
            bg = colors['BG_SECONDARY']
            fg = colors['TEXT_PRIMARY']
            
        btn.configure(
            bg=bg, fg=fg,
            activebackground=colors['BG_HOVER'],
            activeforeground=fg,
            font=ForensiDriveTheme.FONTS['BODY_SMALL'],
            relief=tk.FLAT,
            bd=0,
            padx=ForensiDriveTheme.SPACING['PAD_MEDIUM'],
            pady=ForensiDriveTheme.SPACING['PAD_SMALL']
        )

    @staticmethod
    def style_label(label: tk.Label, style: str = 'body'):
        fonts = ForensiDriveTheme.FONTS
        colors = ForensiDriveTheme.COLORS
        font = fonts['BODY']
        fg = colors['TEXT_PRIMARY']
        
        if style == 'heading_large':
            font = fonts['HEADING_LARGE']
        elif style == 'heading':
            font = fonts['HEADING']
        elif style == 'heading_small':
            font = fonts['HEADING_SMALL']
        elif style == 'body_small':
            font = fonts['BODY_SMALL']
            fg = colors['TEXT_SECONDARY']
        elif style == 'mono':
            font = fonts['MONO']
        elif style == 'mono_small':
            font = fonts['MONO_SMALL']
            fg = colors['TEXT_SECONDARY']
            
        label.configure(
            bg=label.master.cget('bg'),
            fg=fg,
            font=font
        )

    @staticmethod
    def style_frame(frame: tk.Frame):
        frame.configure(bg=ForensiDriveTheme.COLORS['BG_PRIMARY'])

    @staticmethod
    def style_entry(entry: tk.Entry):
        colors = ForensiDriveTheme.COLORS
        entry.configure(
            bg=colors['BG_CARD'],
            fg=colors['TEXT_PRIMARY'],
            insertbackground=colors['TEXT_PRIMARY'],
            font=ForensiDriveTheme.FONTS['BODY'],
            relief=tk.FLAT,
            bd=1,
            highlightbackground=colors['BORDER'],
            highlightcolor=colors['ACCENT_BLUE'],
            highlightthickness=1
        )
