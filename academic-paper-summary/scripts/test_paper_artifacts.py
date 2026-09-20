"""Test artifact invariants with synthetic PDFs, not real paper summaries."""
import tempfile
import unittest
from pathlib import Path
import fitz
from docx import Document
from docx.oxml.ns import qn
from paper_artifacts import (initialize, crop, build, inside, save_json, read_json,
                            render_pages, inspect_crop, review_crop, crop_review_path)


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.parent=Path(self.tmp.name)
        source=self.parent/'input.pdf'
        with fitz.open() as doc:
            page=doc.new_page()
            page.insert_text((50,50),'English paper title and authors')
            page.draw_rect(fitz.Rect(50,100,250,200))
            page.insert_text((50,240),'Fig. 1. Synthetic caption outside crop')
            doc.save(source)
        self.root=initialize(source,self.parent/'outputs')
        self.identity=crop(self.root,1,[30,20,400,75],'identity')
        self.figure=crop(self.root,1,[40,90,260,210],'figure1')
        # Synthetic fixture attestations only: coordinates enclose the known text/rectangle.
        for image in [self.identity,self.figure]:
            review_crop(self.root,image.relative_to(self.root).as_posix(),
                        'Synthetic fixture: full known geometry enclosed; external caption and body excluded.')
        self.data=dict(title_zh='中文合成测试题目',identity_images=[self.identity.relative_to(self.root).as_posix()],
            background=['背景一','背景二'],methods=[dict(heading='测试方法',paragraphs=['测试内容'])],
            conclusions=[dict(heading='合成测试结果',paragraphs=['测试描述'],figures=[dict(number=1,image=self.figure.relative_to(self.root).as_posix(),caption='合成图注')])],
            innovations=['一项','二项','三项'],citation='Test A. English paper title and authors. Synthetic Journal, 2026.',
            citation_metadata=dict(original_title='English paper title and authors',authors=['Test A'],journal='Synthetic Journal',year='2026'))
        save_json(self.root/'draft/report.json',self.data)

    def test_workspace_and_version_isolation(self):
        second=initialize(self.root/'source/paper.pdf',self.parent/'outputs')
        self.assertNotEqual(self.root,second)
        a=build(self.root);original=a.read_bytes();b=build(self.root)
        self.assertNotEqual(a,b);self.assertEqual(a.read_bytes(),original)
        self.assertTrue(a.is_relative_to(self.root/'final'))

    def test_chinese_title_and_english_screenshot_both_present(self):
        doc=Document(build(self.root))
        self.assertEqual(doc.paragraphs[0].text,'中文合成测试题目')
        self.assertTrue(doc.paragraphs[1]._p.xpath('.//a:blip'))
        self.assertEqual(doc.paragraphs[2].text,'一、研究背景')
        self.assertEqual(len(doc.inline_shapes),2)

    def test_numbering_fonts_and_no_paragraph_keep_flags(self):
        doc=Document(build(self.root))
        self.assertEqual([p.text for p in doc.paragraphs if p.style.name=='Heading 3'],['1. 测试方法','1. 合成测试结果'])
        for name,east,size,bold in [('Normal','楷体',12,False),('Heading 1','宋体',14,True),('Heading 2','宋体',18,True),('Caption','楷体',11,True),('Citation','Times New Roman',12,False)]:
            style=doc.styles[name]
            self.assertEqual(style.font.size.pt,size)
            self.assertEqual(style.font.bold,bold)
            self.assertEqual(style.element.rPr.rFonts.get(qn('w:eastAsia')),east)
            self.assertEqual(style.element.rPr.rFonts.get(qn('w:ascii')),'Times New Roman')
            self.assertFalse(style.paragraph_format.keep_with_next)
            self.assertFalse(style.paragraph_format.keep_together)
            self.assertFalse(style.paragraph_format.page_break_before)

    def test_outside_paths_and_invalid_crop_rejected(self):
        with self.assertRaises(ValueError):inside(self.root,'../../escape.png')
        with self.assertRaises(ValueError):crop(self.root,1,[-1,0,30,40],'bad')
        self.data['identity_images']=['../other-paper/header.png']
        save_json(self.root/'draft/report.json',self.data)
        with self.assertRaises(ValueError):build(self.root)

    def test_missing_chinese_title_or_identity_rejected(self):
        self.data['title_zh']='English only';save_json(self.root/'draft/report.json',self.data)
        with self.assertRaises(ValueError):build(self.root)
        self.data['title_zh']='中文题目';self.data['identity_images']=[]
        save_json(self.root/'draft/report.json',self.data)
        with self.assertRaises(ValueError):build(self.root)

    def test_crop_provenance_and_page_preview(self):
        self.assertTrue(self.figure.with_suffix('.json').is_file())
        out=render_pages(self.root,'source/paper.pdf',[1])
        self.assertTrue((out/'page-001.png').is_file())

    def test_example_citation_cannot_replace_current_paper(self):
        self.data['citation']='Other A. A different example paper. Synthetic Journal, 2026.'
        save_json(self.root/'draft/report.json',self.data)
        with self.assertRaisesRegex(ValueError,'title does not match'):build(self.root)

    def test_missing_citation_metadata_rejected(self):
        del self.data['citation_metadata']
        save_json(self.root/'draft/report.json',self.data)
        with self.assertRaisesRegex(ValueError,'citation_metadata'):build(self.root)

    def test_citation_year_and_doi_checked(self):
        self.data['citation_metadata']['year']='2025'
        save_json(self.root/'draft/report.json',self.data)
        with self.assertRaisesRegex(ValueError,'year does not match'):build(self.root)
        self.data['citation_metadata']['year']='2026'
        self.data['citation_metadata']['doi']='10.0000/synthetic-test'
        save_json(self.root/'draft/report.json',self.data)
        with self.assertRaisesRegex(ValueError,'DOI'):build(self.root)
        self.data['citation']+=' https://doi.org/10.0000/synthetic-test'
        save_json(self.root/'draft/report.json',self.data)
        self.assertTrue(build(self.root).is_file())

    def test_crop_warns_on_caption_and_cut_text(self):
        image=crop(self.root,1,[60,35,260,250],'bad-crop').relative_to(self.root).as_posix()
        result=read_json(crop_review_path(self.root,image))
        self.assertEqual(result['status'],'pending')
        kinds={w['kind'] for w in result['warnings']}
        self.assertIn('cut_text',kinds)
        self.assertIn('possible_source_caption',kinds)
        self.assertTrue((self.root/result['context']).is_file())

    def test_build_blocks_pending_and_changed_images(self):
        image=self.figure.relative_to(self.root).as_posix()
        inspect_crop(self.root,image)
        with self.assertRaisesRegex(ValueError,'review missing'):build(self.root)
        review_crop(self.root,image,'Synthetic geometry checked: rectangle complete and caption excluded.')
        build(self.root)
        self.figure.write_bytes(self.figure.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError,'stale'):build(self.root)
        with self.assertRaisesRegex(ValueError,'changed'):review_crop(self.root,image,'This old inspection cannot apply to a changed image file.')

    def test_changed_coordinates_invalidate_review(self):
        meta=read_json(self.figure.with_suffix('.json'));meta['rect'][0]+=1
        save_json(self.figure.with_suffix('.json'),meta)
        with self.assertRaisesRegex(ValueError,'stale'):build(self.root)

    def test_rotated_page_text_warnings(self):
        source=self.parent/'rotated.pdf'
        with fitz.open() as doc:
            page=doc.new_page(width=300,height=400)
            page.insert_text((50,80),'Fig. 2. Caption')
            page.set_rotation(90)
            expected=fitz.Rect(page.get_text('words')[0][:4])*page.rotation_matrix
            doc.save(source)
        root=initialize(source,self.parent/'outputs')
        image=crop(root,1,[expected.x0-1,expected.y0+2,expected.x1+1,expected.y1+1],'rotated').relative_to(root).as_posix()
        kinds={w['kind'] for w in read_json(crop_review_path(root,image))['warnings']}
        self.assertIn('cut_text',kinds)
        self.assertIn('possible_source_caption',kinds)

    def test_neighboring_body_warning(self):
        source=self.parent/'columns.pdf'
        with fitz.open() as doc:
            page=doc.new_page()
            page.insert_textbox(fitz.Rect(310,50,550,300),
                'This is neighboring article body text. '*12,fontsize=11)
            doc.save(source)
        root=initialize(source,self.parent/'outputs')
        image=crop(root,1,[20,20,560,310],'wide').relative_to(root).as_posix()
        self.assertIn('possible_body_text',{w['kind'] for w in read_json(crop_review_path(root,image))['warnings']})


if __name__=='__main__':unittest.main(verbosity=2)
