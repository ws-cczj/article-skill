"""Set truthful properties on new reports, without a template preview."""
from datetime import datetime, timezone

from docx.opc.constants import RELATIONSHIP_TYPE as RT


def prepare_report_properties(document, title):
    """Call before saving a newly generated report (not an existing user file)."""
    properties = document.core_properties
    properties.title = title
    properties.author = '捶捶自己'
    for name in ('last_modified_by', 'comments', 'subject', 'keywords',
                 'category', 'identifier', 'language', 'version', 'content_status'):
        setattr(properties, name, '')
    now = datetime.now(timezone.utc).replace(microsecond=0)
    properties.created = properties.modified = now
    for element in properties._element.xpath('./cp:lastPrinted'):
        properties._element.remove(element)
    properties.revision = 1

    package = document.part.package
    # python-docx's default template includes a blank JPEG. Windows may show
    # that preview instead of the ordinary Word icon. Drop its package link;
    # the unreachable image is then omitted by the package writer.
    for relationship in list(package.rels.values()):
        if relationship.reltype == RT.THUMBNAIL:
            del package.rels[relationship.rId]

    # These are template statistics, not measurements of this report. Do not
    # claim it was saved by Macintosh Word or carry over its page/word counts.
    app = package.part_related_by(RT.EXTENDED_PROPERTIES)
    app._blob = (
        b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        b'<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
        b'<Application>article-skill</Application></Properties>'
    )
