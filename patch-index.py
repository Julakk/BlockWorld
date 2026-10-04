import re, sys, shutil

def read(p):
    return open(p, encoding='utf8').read()

if 'window.PMLook' not in read('pm-look.js'):
    sys.exit('pm-look.js belum versi terbaru (jalankan fix-v410.py / patch lama dulu)')

html = read('index.html')
shutil.copy('index.html', 'index.html.bak')
for tag in ('BW-CHAR', 'PM-LOOK', 'PM-START', 'PM-GACHA'):
    html = re.sub(r'<!--%s-START-->.*?<!--%s-END-->\n?' % (tag, tag), '', html, flags=re.S)

blocks = ''
for tag, fn in (('PM-LOOK', 'pm-look.js'), ('PM-START', 'pm-start.js'), ('PM-GACHA', 'pm-gacha.js')):
    js = read(fn)
    if '</scr' + 'ipt' in js:
        sys.exit(fn + ' mengandung penutup script, batal')
    blocks += '<!--%s-START-->\n<scr' % tag + 'ipt>\n' + js + '\n</scr' + 'ipt>\n<!--%s-END-->\n' % tag

i = html.rfind('</body>')
if i < 0:
    sys.exit('tidak ketemu penutup body')
html = html[:i] + blocks + html[i:]
open('index.html', 'w', encoding='utf8').write(html)
if 'window.PMOpenLB' not in html:
    print('PERINGATAN: PMOpenLB belum ada, tombol Peringkat di layar utama belum berfungsi')
print('OK: PM-LOOK + PM-START + PM-GACHA ditanam')
