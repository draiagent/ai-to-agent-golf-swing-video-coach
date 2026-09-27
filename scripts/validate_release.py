"""Offline packaging validation, not a video accuracy test. Python standard library only."""
import ast, hashlib, json, re
from pathlib import Path
root = Path(__file__).resolve().parents[1]
errors = []
def check(ok, msg):
    if not ok: errors.append(msg)
version = (root / 'VERSION').read_text().strip()
meta = json.loads((root / 'project.json').read_text())
check(meta['version'] == version, 'project version mismatch')
check(f'name: {meta["name"]}' in (root/'SKILL.md').read_text(), 'skill name mismatch')
for name in ['README.md','SKILL.md','CHANGELOG.md','RELEASE_NOTES.md']:
    check(version in (root/name).read_text(), 'missing version: '+name)
for p in root.rglob('*.py'):
    ast.parse(p.read_text(), filename=str(p))
for p in root.rglob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if '://' in target or target.startswith('#'): continue
        check((p.parent/target.split('#')[0]).exists(), str(p.relative_to(root))+': '+target)
manifest=json.loads((root/'assets/manifest.json').read_text())
check([x['page'] for x in manifest]==list(range(1,13)), 'card sequence mismatch')
for x in manifest:
    p=root/x['file']
    check(p.exists(), 'missing image '+x['file'])
    if p.exists(): check(hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'], 'image hash mismatch')
source=json.loads((root/'docs/source-provenance.json').read_text())
for x in source['unchanged_files']:
    check(hashlib.sha256((root/x['file']).read_bytes()).hexdigest()==x['sha256'], 'original modified: '+x['file'])
for p in root.rglob('*'):
    if p.is_file():
        check(p.stat().st_size < 100_000_000, 'large git file: '+str(p))
        check(p.suffix.lower() not in ['.mov','.mp4','.avi','.pem','.key'], 'private file type: '+str(p))
if errors:
    raise SystemExit('\n'.join(errors))
print('PASS: version, skill name, syntax, local links, 12 card hashes, original files and package file types.')
print('NOT TESTED: dependency installation, real video execution, analysis accuracy, remote publication.')
