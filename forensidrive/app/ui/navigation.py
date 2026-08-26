import tkinter as tk
from .theme import ForensiDriveTheme
from .widgets import ScrollableFrame

class NavigationManager:
    def __init__(self, container: tk.Frame):
        self.container = container
        self.pages = {}
        self.history = []
        self.current_page = None
        self.current_page_name = None

    def register_page(self, name: str, page_class):
        self.pages[name] = page_class

    def navigate_to(self, name: str, **kwargs):
        if name not in self.pages:
            raise ValueError(f"Page '{name}' not registered")
        
        if self.current_page_name:
            self.history.append((self.current_page_name, self.current_kwargs))
        
        self._show_page(name, kwargs)

    def _show_page(self, name: str, kwargs):
        if self.current_page:
            self.current_page.destroy()
            
        page_class = self.pages[name]
        self.current_page = page_class(self.container, self, **kwargs)
        self.current_page.pack(fill='both', expand=True)
        self.current_page.build()
        self.current_page_name = name
        self.current_kwargs = kwargs

    def go_back(self):
        if self.can_go_back():
            name, kwargs = self.history.pop()
            self._show_page(name, kwargs)

    def can_go_back(self) -> bool:
        return len(self.history) > 0

    def get_current_page(self) -> str:
        return self.current_page_name

    def clear_history(self):
        self.history.clear()

class BasePage(tk.Frame):
    def __init__(self, parent, nav_manager: NavigationManager, **kwargs):
        super().__init__(parent, bg=ForensiDriveTheme.COLORS['BG_PRIMARY'])
        self.nav = nav_manager
        self.kwargs = kwargs

    def build(self):
        raise NotImplementedError("Subclasses must implement build()")

    def create_header(self, title, subtitle=None, show_back=True) -> tk.Frame:
        header = tk.Frame(self, bg=self['bg'])
        header.pack(fill='x', padx=ForensiDriveTheme.SPACING['PAD_LARGE'], pady=ForensiDriveTheme.SPACING['PAD_LARGE'])
        
        if show_back and self.nav.can_go_back():
            btn = tk.Button(header, text="← Back", command=self.nav.go_back)
            ForensiDriveTheme.style_button(btn, 'secondary')
            btn.pack(side='left', padx=(0, ForensiDriveTheme.SPACING['PAD_LARGE']))
            
        title_frame = tk.Frame(header, bg=self['bg'])
        title_frame.pack(side='left', fill='both', expand=True)
        
        lbl_title = tk.Label(title_frame, text=title)
        ForensiDriveTheme.style_label(lbl_title, 'heading_large')
        lbl_title.pack(anchor='w')
        
        if subtitle:
            lbl_sub = tk.Label(title_frame, text=subtitle)
            ForensiDriveTheme.style_label(lbl_sub, 'body')
            lbl_sub.pack(anchor='w', pady=(5, 0))
            
        return header

    def create_scrollable_content(self) -> ScrollableFrame:
        scrollable = ScrollableFrame(self)
        scrollable.pack(fill='both', expand=True, padx=ForensiDriveTheme.SPACING['PAD_LARGE'], pady=(0, ForensiDriveTheme.SPACING['PAD_LARGE']))
        return scrollable
