import os
import shutil
import subprocess
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tmp = os.path.join(ROOT, 'tools', 'bearserver-zip')
out = os.path.join(ROOT, 'tools', 'bearserver-dec')
dex = os.path.join(ROOT, 'tools', 'dex-out', 'classes.dex')

for d in (tmp, out):
    if os.path.exists(d):
        shutil.rmtree(d)
os.makedirs(tmp)
zipfile.ZipFile(os.path.join(tmp, 'dummy.zip'), 'w').write(dex, 'classes.dex')

r = subprocess.run(['java', '-jar', os.path.join(ROOT, 'tools', 'apktool.jar'),
                    'd', os.path.join(tmp, 'dummy.zip'), '-o', out, '-f'],
                   capture_output=True, text=True, timeout=300)
print(r.stdout[-500:] if r.stdout else '', r.stderr[-500:] if r.stderr else '')

# copy smali into the apk build tree
src = os.path.join(out, 'smali', 'com', 'bearfarm')
dst = os.path.join(ROOT, 'apk-src', 'smali', 'com', 'bearfarm')
if os.path.exists(dst):
    shutil.rmtree(dst)
os.makedirs(dst)
for f in os.listdir(src):
    shutil.copy(os.path.join(src, f), dst)
    print('copied', f)
