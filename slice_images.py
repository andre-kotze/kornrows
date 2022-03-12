import os
import subprocess

x = 864
y = 972

for n, img in enumerate(os.listdir()):
    if ".JPG" in img:
        print("converting", img)
        subprocess.call(f'"C:\Program Files\ImageMagick-7.1.0-Q16-HDRI\convert.exe" {img} -crop {x}x{y} crop_{n}-%02d.jpg') 
