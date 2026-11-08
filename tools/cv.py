"""Verify the owner's existing CV; the website never regenerates it."""
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader


def check_cv(root):
    root = Path(root)
    manifest = json.loads((root / 'content/cv.json').read_text(encoding='utf-8'))
    if set(manifest) != {'filename', 'version', 'pages', 'sha256'}:
        raise ValueError('Unexpected CV manifest fields')
    if manifest['filename'] != 'Justin_Do_CV.pdf':
        raise ValueError('Unexpected CV filename')
    pdf = root / 'assets/pdf' / manifest['filename']
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != manifest['sha256']:
        raise ValueError('CV differs from the reviewed version; update the manifest after review')
    reader = PdfReader(pdf)
    if len(reader.pages) != manifest['pages']:
        raise ValueError('CV page count differs from the reviewed version')
    if reader.attachments or reader.trailer['/Root'].get('/OpenAction'):
        raise ValueError('Unexpected PDF attachment or open action')
    metadata = str(reader.metadata)
    if any(marker in metadata for marker in ('OneDrive', 'C:\\', '/Users/', '/home/')):
        raise ValueError('Machine path in CV metadata')
    text = '\n'.join(page.extract_text() or '' for page in reader.pages)
    if 'Justin Do' not in text or 'Curriculum Vitae' not in text:
        raise ValueError('Unexpected CV document')
    return len(reader.pages)
