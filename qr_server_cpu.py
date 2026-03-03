import qrcode
import base64, io
from qrcode.image.pure import PyPNGImage

import settings


def make_qr_code(text:str = ''):
    """
    Основная CPU-bound функция, генерирующая QR-код. Принимает текст в виде str-строки и возвращает base64(str ascii)-строку с png файлом.
    """
    
    code = qrcode.QRCode(
        version=1,
        error_correction=settings.correction_level['minimum'],
        box_size=10,
        border=0,
        image_factory=PyPNGImage
    )
    code.add_data(text)
    code.make(fit=True)
    img = code.make_image()
    
    buf = io.BytesIO()
    img.save(buf)
    png_bytes = buf.getvalue()
    base64_str = base64.b64encode(png_bytes)
    return base64_str.decode('ascii')

if __name__ == '__main__':
    b64pic = make_qr_code('4C0404004')
    img_bytes = base64.b64decode(b64pic)
    with open(f'test_picture.png', 'wb') as file:
        file.write(img_bytes)