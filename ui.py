import os
import string
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk
import generator

# PyInstaller helper for bundled resources
def resource_path(relative_path: str) -> str:
    try: # access PyInstaller temporary folder
        base_path = sys._MEIPASS
    except AttributeError: # access current directory
        base_path = os.path.abspath('.')
    
    return os.path.join(base_path, relative_path)

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title('QRever Studio')
        self.iconbitmap(resource_path('assets/icon.ico'))
        self.geometry('600x450')
        self.resizable(False, False) # lock size

        # QR code state
        self.data = ''
        self.qr = None
        self.fg_color = ''
        self.bg_color = ''
        self.logo_path = ''
        self.img = None
        self.img_tk = None

        # data widgets
        data_frame = tk.LabelFrame(self, text = 'Generate QR Code', padx = 10, pady = 10)
        data_frame.pack(fill = 'x', padx = 10)
        tk.Label(data_frame, text = 'QR Code Data', anchor = 'w').pack(fill = 'x')
        self.data_entry = tk.Entry(data_frame)
        self.data_entry.pack(expand = True, fill = 'x', side = 'left', padx = 5)
        tk.Button(data_frame, text = 'Generate', command = self.on_generate).pack(side = 'right', padx = 5)

        # image frame for editing and preview widgets
        img_frame = tk.Frame(self)
        img_frame.pack(expand = True, fill = 'both', padx = 10)

        # editing frame for color, logo, and saving widgets
        edit_frame = tk.LabelFrame(img_frame, text = 'Edit QR Code', padx = 10, pady = 10)
        edit_frame.pack(fill = 'both', side = 'left', pady = 10)
        
        # color editing widgets
        vcmd = (self.register(self.validate_hex), '%P') # validate after every keystroke
        fg_frame = tk.Frame(edit_frame)
        fg_frame.pack(fill = 'x', pady = (10, 2))
        self.fg_color_entry = tk.Entry(fg_frame, width = 20, validate = 'key', validatecommand = vcmd)
        tk.Label(fg_frame, text = 'Foreground Color', anchor = 'w').pack(fill = 'x')
        self.fg_color_entry.pack(fill = 'x', side = 'left')
        tk.Button(fg_frame, text = 'Randomize Colors', command = self.on_randomize_colors).pack(fill = 'x', padx = 5)
        bg_frame = tk.Frame(edit_frame)
        bg_frame.pack(fill = 'x', pady = 2)
        self.bg_color_entry = tk.Entry(bg_frame, width = 20, validate = 'key', validatecommand = vcmd)
        tk.Label(bg_frame, text = 'Background Color', anchor = 'w').pack(fill = 'x')
        self.bg_color_entry.pack(fill = 'x', side = 'left')
        tk.Button(bg_frame, text = 'Apply Colors', command = self.on_apply_colors).pack(fill = 'x', padx = 5)

        # logo editing widgets
        logo_frame = tk.Frame(edit_frame)
        logo_frame.pack(fill = 'x', pady = 20)
        self.logo_button = tk.Button(logo_frame, text = 'Add Logo', command = self.on_add_logo)
        self.logo_button.pack(expand = True, fill = 'x', padx = 10, pady = 5)
        tk.Button(logo_frame, text = 'Remove Logo', command = self.on_remove_logo).pack(expand = True, fill = 'x', padx = 10, pady = 5)
        
        # saving widget
        tk.Button(edit_frame, text = 'Save', command = self.on_save).pack(expand = True, fill = 'x', side = 'left', padx = 10, pady = 10)

        # preview widgets
        preview_frame = tk.LabelFrame(img_frame, text = 'Preview QR Code')
        preview_frame.pack(expand = True, fill = 'both', side = 'right', pady = 10)
        preview_frame.pack_propagate(False)
        self.preview_label = tk.Label(preview_frame)
        self.preview_label.pack(expand = True)

        # status bar
        status_frame = tk.Frame(self, bd = 1, relief = 'sunken')
        status_frame.pack(fill = 'x', side = 'bottom')
        self.status_var = tk.StringVar(status_frame)
        tk.Label(status_frame, anchor = 'w', textvariable = self.status_var).pack(fill = 'x', padx = 10)

    def validate_hex(self, proposed: str) -> bool:
        if not proposed: # allow empty entry
            return True
        
        if len(proposed) > 6: # 6-digit limit exceeded
            return False
        
        return all(digit in string.hexdigits for digit in proposed)
    
    def can_edit(self) -> bool:
        if not self.qr: # no QR code generated
            self.status_var.set('Nothing to edit')
            return False
        
        return True # allow editing

    def update_image(self) -> None:
        self.img = generator.render_qr(self.qr, self.fg_color, self.bg_color, self.logo_path)

        # resize preview to 50% of the window's smaller dimension
        width = self.winfo_width()
        height = self.winfo_height()
        resize_dimension = min(width, height)
        preview_scale = 0.5
        box_size = int(resize_dimension * preview_scale)

        img_resized = generator.resize_display(self.img, box_size)
        self.img_tk = ImageTk.PhotoImage(img_resized)
        self.preview_label.config(image = self.img_tk)

    def on_generate(self) -> None:
        data = self.data_entry.get()
        if self.qr and data == self.data: # generated and unchanged
            self.status_var.set('Data unchanged')
            return
        
        try:
            qr = generator.generate_qr(data)
        except Exception as e:
            self.status_var.set(f'Generate failed: {e}')
            return
        
        self.data = data
        self.qr = qr
        self.update_image()
        self.status_var.set(f'Generated QR code for {self.data!r}')
        
    def on_randomize_colors(self) -> None:
        fg_color = generator.get_random_hex()
        bg_color = generator.get_random_hex()

        # overwrite both color Entry texts
        self.fg_color_entry.delete(0, 'end')
        self.fg_color_entry.insert(0, fg_color)
        self.bg_color_entry.delete(0, 'end')
        self.bg_color_entry.insert(0, bg_color)
        self.status_var.set('Colors randomized')

    def on_apply_colors(self) -> None:
        if not self.can_edit():
            return
        
        fg_color = generator.normalize_hex(self.fg_color_entry.get())
        bg_color = generator.normalize_hex(self.bg_color_entry.get())
        if fg_color == self.fg_color and bg_color == self.bg_color: # unchanged
            self.status_var.set('Colors unchanged')
            return
        
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.update_image()
        self.status_var.set('Colors applied')
    
    def on_add_logo(self) -> None:
        if not self.can_edit():
            return
        
        path = filedialog.askopenfilename(title = 'Add Logo', filetypes = [('Image Files', '*.png *.jpg *.jpeg')])
        if not path: # open cancelled
            self.status_var.set('Select logo cancelled')
            return
        
        if path == self.logo_path: # unchanged
            self.status_var.set('Logo unchanged')
            return
        
        is_add = not self.logo_path # nothing to change
        self.logo_path = path
        self.update_image()
        if is_add:
            self.logo_button.config(text = 'Change Logo')
            self.status_var.set('Logo added')
        else:
            self.status_var.set('Logo changed')

    def on_remove_logo(self) -> None:
        if not self.can_edit():
            return
        
        if not self.logo_path: # no logo added
            self.status_var.set('No logo to remove')
            return
        
        self.logo_path = ''
        self.update_image()
        self.logo_button.config(text = 'Add Logo')
        self.status_var.set('Logo removed')

    def on_save(self) -> None:
        if self.img is None: # no QR code generated
            self.status_var.set('Nothing to save')
            return
        
        path = filedialog.asksaveasfilename(title = 'Save QR Code', initialfile = 'qrcode.png', defaultextension = '.png', filetypes = [('PNG Image', '*.png'), ('JPEG Image', '*.jpg;*.jpeg'), ('All Files', '*.*')])
        if not path: # save cancelled
            self.status_var.set('Save cancelled')
            return
        
        if os.path.exists(path): # prompt overwrite or copy
            overwrite = messagebox.askyesnocancel('File exists', 'A file with this name already exists. Do you want to overwrite it?')
            if overwrite is None: # cancel save
                self.status_var.set('Save cancelled')
                return
            
            if not overwrite: # make a copy
                path = generator.next_copy_path(path)
        
        try:
            filename = generator.save_qr(self.img, path) # save new or overwrite
            self.status_var.set(f'Saved as {filename}')
        except Exception as e:
            self.status_var.set(f'Save failed: {e}')
