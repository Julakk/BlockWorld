import sys

def patch(fn, pairs):
    s = open(fn, encoding='utf8').read()
    for old, new in pairs:
        if old not in s:
            sys.exit('%s: potongan tidak ketemu: %s' % (fn, old[:60]))
        s = s.replace(old, new, 1)
    open(fn, 'w', encoding='utf8').write(s)
    print(fn, 'OK')

patch('pm-start.js', [
    ("pv.r.toneMapping = T.ACESFilmicToneMapping; pv.r.toneMappingExposure = 1.15;",
     "pv.r.toneMapping = T.NoToneMapping;"),
    ("var dl = new T.DirectionalLight(0xffe2c0, 0.9); dl.position.set(3, 5, 4); pv.sc.add(dl);",
     "var dl = new T.DirectionalLight(0xffe2c0, 0.55); dl.position.set(3, 5, 4); pv.sc.add(dl);"),
    ("l: '82%', t: '20%'", "l: '72%', t: '20%'"),
    ("(prof && prof.name) || 'Pemancing';", "(prof && prof.name) || 'Tamu';"),
    ("var has = !!ls(SAVE_KEY), s = C.save;\n    if (!has && s) has = s.level > 1 || s.xp > 0 || Object.keys(s.discovered || {}).length > 0;",
     "var s = C.save, has = !!s && (s.level > 1 || s.xp > 0 || Object.keys(s.discovered || {}).length > 0 || ((s.stats && s.stats.catches) || 0) > 0);"),
])

patch('pm-look.js', [
    ("R.r.toneMapping = T.ACESFilmicToneMapping; R.r.toneMappingExposure = 1.15;",
     "R.r.toneMapping = T.NoToneMapping;"),
    ("var dl = new T.DirectionalLight(0xffe2c0, 0.9); dl.position.set(3, 5, 4); R.sc.add(dl);",
     "var dl = new T.DirectionalLight(0xffe2c0, 0.55); dl.position.set(3, 5, 4); R.sc.add(dl);"),
])
