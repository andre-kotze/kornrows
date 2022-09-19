import os
import subprocess
import platform



x = 864
y = 972
cwd = os.getcwd()
os.chdir(os.path.join(cwd, 'train-data/second50/'))
cwd = os.getcwd()
outdir = os.path.join(cwd, 'cropped/')
if not os.path.exists(outdir):
    os.mkdir(outdir)

platf = platform.system()


if platf == 'Linux':
    for n, img in enumerate(os.listdir()):
        if ".JPG" in img:
            print("converting", img)
            os.system(f'convert {img} -crop {x}x{y} {outdir}crop_{n}-%02d.jpg') 
elif platf == 'Windows':
    for n, img in enumerate(os.listdir()):
        if ".JPG" in img:
            print("converting", img)
            subprocess.call(f'"C:\Program Files\ImageMagick-7.1.0-Q16-HDRI\convert.exe" {img} -crop {x}x{y} crop_{n}-%02d.jpg') 
else:
    print('OS not supported')