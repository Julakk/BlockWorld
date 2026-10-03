import re, sys, shutil

def read(p):
    return open(p, encoding='utf8').read()

# 1) pm-look.js: warna langsung terpasang + bisa dibuka dari layar utama
s = read('pm-look.js')
if 'window.PMLook' not in s:
    a = "function use(d) { KEYS.forEach(function (k) { cols[k].set(d[k]); }); on = true; }"
    b = "    draft[k] = c; cols[k].set(c); on = true;\n"
    c = "  var host = document.getElementById('menuPanel') || document.getElementById('hudPills');"
    for x in (a, b, c):
        if x not in s:
            sys.exit('pm-look.js: potongan kode tidak ketemu: ' + x[:50])
    s = s.replace(a, a.replace('on = true; }', 'on = true; applyLook(); }'), 1)
    s = s.replace(b, "    draft[k] = c; cols[k].set(c); on = true; applyLook();\n", 1)
    s = s.replace(c, "  window.PMLook = { open: openPanel, apply: applyLook };\n" + c, 1)
    open('pm-look.js', 'w', encoding='utf8').write(s)
    print('pm-look.js diperbarui')

# 2) index.html
html = read('index.html')
shutil.copy('index.html', 'index.html.bak')

# bersihkan blok lama
for tag in ('BW-CHAR', 'PM-LOOK', 'PM-START'):
    html = re.sub(r'<!--%s-START-->.*?<!--%s-END-->\n?' % (tag, tag), '', html, flags=re.S)

# buka akses Peringkat buat tombol baru
OLD = "function openLB() { netSend({ t: 'lbget' }); renderLB(); }"
if 'window.PMOpenLB' not in html:
    if OLD in html:
        html = html.replace(OLD, OLD + "\n  window.PMOpenLB = function () { openLB(); mLB.open(); };", 1)
        print('PMOpenLB dipasang')
    else:
        print('PERINGATAN: fungsi openLB tidak ketemu, tombol Peringkat belum berfungsi')

blocks = ''
for tag, fn in (('PM-LOOK', 'pm-look.js'), ('PM-START', 'pm-start.js')):
    js = read(fn)
    if '</scr' + 'ipt' in js:
        sys.exit(fn + ' mengandung penutup script, batal')
    blocks += '<!--%s-START-->\n<scr' % tag + 'ipt>\n' + js + '\n</scr' + 'ipt>\n<!--%s-END-->\n' % tag

i = html.rfind('</body>')
if i < 0:
    sys.exit('tidak ketemu penutup body')
html = html[:i] + blocks + html[i:]
open('index.html', 'w', encoding='utf8').write(html)
print('OK: PM-LOOK + PM-START ditanam')
