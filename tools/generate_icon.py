"""Build the ALA icon from code; no course assets or binary download required."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os

def generate(destination):
    image = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((8, 8, 248, 248), radius=56, fill='#25614b')
    font = ImageFont.truetype(str(Path(os.environ.get('WINDIR', 'C:/Windows'))/'Fonts/segoeuib.ttf'), 184)
    draw.text((128, 119), 'a', font=font, anchor='mm', fill='white')
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])

if __name__ == '__main__':
    generate(Path(__file__).resolve().parents[1]/'assets/ala.ico')
