import pdfplumber,sys
from pathlib import Path
pdf=Path(sys.argv[1]); out=Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)
with pdfplumber.open(pdf) as p:
  for i,page in enumerate(p.pages,1):
    txt=page.extract_text(x_tolerance=1.5,y_tolerance=3) or ''
    (out/f'page-{i:02d}.txt').write_text(txt,encoding='utf-8')
print('done')
