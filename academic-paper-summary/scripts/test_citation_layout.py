import unittest
from paper_artifacts import citation_paragraphs


class CitationLayoutTests(unittest.TestCase):
    def test_inline_doi_becomes_last_paragraph(self):
        self.assertEqual(citation_paragraphs('A. Title[J]. Journal, 2026: 1. DOI: 10.1234/test.'),
                         ['A. Title[J]. Journal, 2026: 1.', 'DOI: 10.1234/test.'])

    def test_existing_linebreak_and_url(self):
        self.assertEqual(citation_paragraphs('Entry\nDOI: 10.1234/a(b)'), ['Entry', 'DOI: 10.1234/a(b)'])
        self.assertEqual(citation_paragraphs('Entry https://doi.org/10.1234/test'),
                         ['Entry', 'DOI: 10.1234/test'])

    def test_no_doi_is_not_invented(self):
        self.assertEqual(citation_paragraphs('Entry without DOI.'), ['Entry without DOI.'])


if __name__ == '__main__':
    unittest.main()
