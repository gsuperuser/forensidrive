import tkinter as tk
from tkinter import filedialog
from .theme import ForensiDriveTheme
from .widgets import TechnicalDetails

def center_window(win, width, height):
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f'{width}x{height}+{x}+{y}')

def _create_dialog_window(parent, title, width=500, height=None):
    win = tk.Toplevel(parent)
    win.title(title)
    win.configure(bg=ForensiDriveTheme.COLORS['BG_PRIMARY'])
    win.transient(parent)
    win.grab_set()
    if height:
        center_window(win, width, height)
    else:
        win.update_idletasks()
        center_window(win, width, 300)
    return win

def show_confirmation(parent, title, message, detail=None, confirm_text='Continue', cancel_text='Cancel', danger=False) -> bool:
    win = _create_dialog_window(parent, title, 450)
    result = tk.BooleanVar(value=False)
    
    lbl = tk.Label(win, text=message, font=ForensiDriveTheme.FONTS['BODY'], bg=win['bg'], fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'], wraplength=400, justify='left')
    lbl.pack(padx=20, pady=20, fill='x')
    
    if detail:
        td = TechnicalDetails(win)
        td.set_content(detail)
        td.pack(padx=20, pady=(0, 20), fill='x')
        
    btn_frame = tk.Frame(win, bg=win['bg'])
    btn_frame.pack(side='bottom', fill='x', padx=20, pady=20)
    
    def on_confirm():
        result.set(True)
        win.destroy()
        
    def on_cancel():
        result.set(False)
        win.destroy()
        
    if cancel_text:
        cancel_btn = tk.Button(btn_frame, text=cancel_text, command=on_cancel)
        ForensiDriveTheme.style_button(cancel_btn, 'secondary')
        cancel_btn.pack(side='right', padx=(10, 0))
    
    confirm_btn = tk.Button(btn_frame, text=confirm_text, command=on_confirm)
    ForensiDriveTheme.style_button(confirm_btn, 'danger' if danger else 'primary')
    confirm_btn.pack(side='right')
    
    win.wait_window()
    return result.get()

def show_info(parent, title, message, detail=None):
    show_confirmation(parent, title, message, detail, confirm_text='OK', cancel_text='')

def show_error(parent, title, message, technical_detail=None):
    show_confirmation(parent, title, message, technical_detail, confirm_text='OK', cancel_text='', danger=True)

def show_warning(parent, title, message, detail=None):
    show_confirmation(parent, title, message, detail, confirm_text='OK', cancel_text='')

def choose_directory(parent, title='Choose a folder', initial_dir='/') -> str:
    return filedialog.askdirectory(parent=parent, title=title, initialdir=initial_dir)

def show_multi_step_confirmation(parent, title, steps: list) -> bool:
    win = _create_dialog_window(parent, title, 500)
    result = tk.BooleanVar(value=False)
    
    current_step = 0
    
    content_frame = tk.Frame(win, bg=win['bg'])
    content_frame.pack(padx=20, pady=20, fill='both', expand=True)
    
    lbl = tk.Label(content_frame, text="", font=ForensiDriveTheme.FONTS['BODY'], bg=win['bg'], fg=ForensiDriveTheme.COLORS['TEXT_PRIMARY'], wraplength=450, justify='left')
    lbl.pack(fill='x', pady=(0, 10))
    
    entry_var = tk.StringVar()
    entry = tk.Entry(content_frame, textvariable=entry_var)
    ForensiDriveTheme.style_entry(entry)
    
    btn_frame = tk.Frame(win, bg=win['bg'])
    btn_frame.pack(side='bottom', fill='x', padx=20, pady=20)
    
    def update_step():
        if current_step >= len(steps):
            result.set(True)
            win.destroy()
            return
            
        step = steps[current_step]
        lbl.config(text=step.get('message', ''))
        if step.get('require_type'):
            entry.pack(fill='x', pady=10)
            entry_var.set('')
            confirm_btn.config(state='disabled')
        else:
            entry.pack_forget()
            confirm_btn.config(state='normal')
            
    def on_type(*args):
        step = steps[current_step]
        if step.get('require_type'):
            if entry_var.get().strip().lower() == "confirm":
                confirm_btn.config(state='normal')
            else:
                confirm_btn.config(state='disabled')
                
    entry_var.trace_add("write", on_type)
    
    def on_next():
        nonlocal current_step
        current_step += 1
        update_step()
        
    def on_cancel():
        result.set(False)
        win.destroy()
        
    cancel_btn = tk.Button(btn_frame, text="Cancel", command=on_cancel)
    ForensiDriveTheme.style_button(cancel_btn, 'secondary')
    cancel_btn.pack(side='right', padx=(10, 0))
    
    confirm_btn = tk.Button(btn_frame, text="Next", command=on_next)
    ForensiDriveTheme.style_button(confirm_btn, 'danger')
    confirm_btn.pack(side='right')
    
    update_step()
    win.wait_window()
    return result.get()
