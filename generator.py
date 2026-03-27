import os
import random
from PIL import Image
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.pil import PilImage

def get_random_hex() -> str:
    return '{:06x}'.format(random.randint(0, 0xffffff))

def normalize_hex(hex: str) -> str:
    if len(hex) not in (3, 6): # invalid
        return ''
    
    if len(hex) == 3: # expand 3-digit hex
        hex = ''.join(digit * 2 for digit in hex)
    
    return '#' + hex
    
def resize_display(img: Image.Image, box_size: int) -> Image.Image:
    old_width, old_height = img.size
    box_scale = min(box_size / old_width, box_size / old_height) # scale to fit
    new_width = int(old_width * box_scale)
    new_height = int(old_height * box_scale)
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return img_resized

def embed_logo(img: Image.Image, logo_path: str) -> Image.Image:
    logo = Image.open(logo_path)

    # resize to 20% of QR code
    qr_width, qr_height = img.size
    logo_scale = 0.2
    logo_width = int(qr_width * logo_scale)
    logo_height = int(qr_height * logo_scale)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
    
    logo_pos = ((qr_width - logo_width) // 2, (qr_height - logo_height) // 2) # center on QR code
    logo_mask = logo if logo.mode == 'RGBA' else None

    img.paste(logo, logo_pos, logo_mask)
    return img

def generate_qr(data: str) -> qrcode.QRCode:
    qr = qrcode.QRCode(version = None, error_correction = ERROR_CORRECT_H, box_size = 10, border = 4) # logo support
    qr.add_data(data)
    qr.make(fit = True) # autosize
    return qr

def render_qr(qr: qrcode.QRCode, fg_color: str, bg_color: str, logo_path: str) -> Image.Image:
    if not fg_color: # default to black if None or empty
        fg_color = '#000000'
    if not bg_color: # default to white if None or empty
        bg_color = '#ffffff'

    pil_img: PilImage = qr.make_image(fill_color = fg_color, back_color = bg_color)
    img = pil_img.get_image() # unwrap Image.Image object

    if logo_path: # logo provided
        img = embed_logo(img, logo_path)
    return img

def next_copy_path(path: str) -> str:
    copy_path = path # start with initial path
    copy_index = 1 # start at (1)

    while os.path.exists(copy_path):
        # decompose path
        directory = os.path.dirname(path)
        filename = os.path.basename(path)
        base, extension = os.path.splitext(filename)
        
        # insert copy index
        copy_filename = f'{base} ({copy_index}){extension}'
        copy_path = os.path.join(directory, copy_filename)
        copy_index += 1 # increment to next copy if copy exists
    
    return copy_path

def save_qr(img: Image.Image, path: str) -> str:
    img.save(path)
    return os.path.basename(path) # display path name for status
