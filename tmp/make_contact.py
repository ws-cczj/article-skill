from PIL import Image, ImageOps, ImageDraw
from pathlib import Path
src=Path(r"tmp/pdfs/source_render")
out=Path(r"tmp/pdfs/contact")
files=sorted(src.glob('page-*.png'))
for k in range(0,len(files),4):
    ims=[Image.open(f).convert('RGB') for f in files[k:k+4]]
    scale=0.42
    ims=[im.resize((int(im.width*scale), int(im.height*scale))) for im in ims]
    w=max(im.width for im in ims); h=max(im.height for im in ims)
    sheet=Image.new('RGB',(w*2,h*2+80),'white'); d=ImageDraw.Draw(sheet)
    for j,im in enumerate(ims):
        x=(j%2)*w; y=(j//2)*(h+40)
        sheet.paste(im,(x,y+20)); d.text((x+5,y+2),f'Page {k+j+1}',fill='black')
    sheet.save(out/f'contact-{k//4+1}.png')
print('\n'.join(str(p) for p in sorted(out.glob('*.png'))))
