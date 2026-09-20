import pdfplumber,sys
from pathlib import Path
pdf=Path(sys.argv[1]); out=Path(sys.argv[2]); out.parent.mkdir(parents=True,exist_ok=True)
with pdfplumber.open(pdf) as p:
    chunks=[]
    for i,page in enumerate(p.pages,1):
        txt=page.extract_text(x_tolerance=1.5,y_tolerance=3) or ''
        chunks.append(f'===== PAGE {i} =====\n{txt}\n')
out.write_text('\n'.join(chunks),encoding='utf-8')
print(out)
