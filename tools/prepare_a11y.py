"""Prepare a disposable local copy instrumented with pinned axe-core.

The production artifact is left untouched. Serve .build/a11y-site on port 8081
and inspect #qa-a11y-result through the browser after each page loads.
"""
import base64
import hashlib
import io
from pathlib import Path
import shutil
import tarfile
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
VERSION = '4.14.0'
INTEGRITY = '9WTZxEjsZ7b13TH8JPmbV2z8CHbl80/2hm3XPEG4JgNdQLK81IBRXmSxHfMAOkSqQeRxT/0dwNDz2GOm3zzpcQ=='


def prepare():
    cache = ROOT / '.build' / ('axe-core-' + VERSION + '.js')
    if not cache.exists():
        payload = urlopen('https://registry.npmjs.org/axe-core/-/axe-core-' + VERSION + '.tgz', timeout=30).read()
        if base64.b64encode(hashlib.sha512(payload).digest()).decode() != INTEGRITY:
            raise ValueError('axe-core archive integrity mismatch')
        with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as archive:
            cache.write_bytes(archive.extractfile('package/axe.min.js').read())
    target = (ROOT / '.build/a11y-site').resolve()
    intended = ROOT.resolve() / '.build/a11y-site'
    if target != intended or target.is_symlink():
        raise ValueError('Unexpected accessibility artifact target')
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(ROOT / '_site', target)
    shutil.copyfile(cache, target / 'axe.min.js')
    harness = '''
window.addEventListener('load',()=>axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}}).then(result=>{
const out=document.createElement('script');out.type='application/json';out.id='qa-a11y-result';
out.textContent=JSON.stringify({version:axe.version,violations:result.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,nodes:v.nodes.map(n=>({target:n.target,failureSummary:n.failureSummary}))})),passes:result.passes.length,incomplete:result.incomplete.map(v=>v.id)});document.body.append(out);
}));'''
    (target / 'qa-harness.js').write_text(harness, encoding='utf-8')
    for file in target.rglob('*.html'):
        text = file.read_text(encoding='utf-8')
        scripts = '<script src="/axe.min.js"></script><script src="/qa-harness.js"></script>'
        file.write_text(text.replace('</body>', scripts + '</body>'), encoding='utf-8')
    print('Prepared axe-core ' + VERSION + ' QA copy; production artifact unchanged')


if __name__ == '__main__':
    prepare()
