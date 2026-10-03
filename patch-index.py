import re, sys, shutil
f = 'index.html'
js = open('pm-look.js', encoding='utf8').read()
if '</scr' + 'ipt>' in js:
    sys.exit('pm-look.js mengandung penutup script, batal')
html = open(f, encoding='utf8').read()
shutil.copy(f, f + '.bak')
for tag in ('BW-CHAR', 'PM-LOOK'):
    html = re.sub(r'<!--%s-START-->.*?<!--%s-END-->\n?' % (tag, tag), '', html, flags=re.S)
block = '<!--PM-LOOK-START-->\n<scr' + 'ipt>\n' + js + '\n</scr' + 'ipt>\n<!--PM-LOOK-END-->\n'
i = html.rfind('</body>')
if i < 0:
    sys.exit('tidak ketemu penutup body')
html = html[:i] + block + html[i:]
open(f, 'w', encoding='utf8').write(html)
print('OK, PM-LOOK ditanam')
