import qrcode
import base64, io
from PIL import Image
from pathlib import Path

import settings


def make_qr_code(text:str = ''):
    """
    Основная CPU-bound функция, генерирующая QR-код. Принимает текст в виде str-строки и возвращает base64(str ascii)-строку с png файлом.
    """
    logo_path = Path(settings.logo_path) if settings.logo_path else None
    add_logo = logo_path and logo_path.is_file()
    
    if add_logo:
        version = 4
        correction = settings.correction_level['maximum']
    else:
        version = 1
        correction = settings.correction_level['minimum']
    
    code = qrcode.QRCode(
        version=version,
        error_correction=correction,
        box_size=10,
        border=0
    )
    code.add_data(text)
    code.make(fit=True)
    img = code.make_image().convert('RGB') # type: ignore
    
    if add_logo:
        logo = Image.open(settings.logo_path if settings.logo_path else '')
        qr_width, qr_height = img.size
        logo_size = int(qr_width / 2.4)
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        logo_pos = (
        (qr_width - logo_size) // 2,
        (qr_height - logo_size) // 2
        )
        img.paste(logo, logo_pos)
    
    buf = io.BytesIO()
    img.save(buf, format='PNG') # type: ignore
    png_bytes = buf.getvalue()
    base64_str = base64.b64encode(png_bytes)
    return base64_str.decode('ascii')

if __name__ == '__main__':
    b64pic = make_qr_code('4C0404004')
    img_bytes = base64.b64decode(b64pic)
    with open(f'test_picture.png', 'wb') as file:
        file.write(img_bytes)