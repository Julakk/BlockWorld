import re, os, glob

CSS = r"""
@media (orientation: landscape) and (max-height: 520px) {
  #hud { top: calc(6px + env(safe-area-inset-top, 0px)); }
  .hudPanel { padding: 4px 10px 4px 16px; border-width: 2px; }
  #hudPills { top: calc(8px + env(safe-area-inset-top, 0px)); left: auto; right: calc(70px + env(safe-area-inset-right, 0px)); transform: none; max-width: none; gap: 4px; }
  .hudPill { font-size: 9px; padding: 4px 8px; }
  #versionBadge { top: auto; bottom: calc(3px + env(safe-area-inset-bottom, 0px)); }
  #envLabel { top: auto !important; bottom: calc(18px + env(safe-area-inset-bottom, 0px)) !important; }
  #topRightBW { top: calc(6px + env(safe-area-inset-top, 0px)); gap: 5px; }
  .iconBtn { width: 46px; }
  .iconCircle { width: 40px; height: 40px; }
  #topRightBW .ico { width: 20px !important; height: 20px !important; }
  #joystickZone { width: 104px; height: 104px; bottom: calc(12px + env(safe-area-inset-bottom, 0px)); }
  #fishActionWrap { bottom: calc(10px + env(safe-area-inset-bottom, 0px)); }
  #fishBtn { width: 84px; height: 84px; font-size: 11px; border-width: 3px; }
  #fishBtn .ico { width: 17px; height: 17px; }
  #powerWrap, #reelWrap { bottom: calc(40px + env(safe-area-inset-bottom, 0px)); }
  #castRating { bottom: 100px; }
  #interactBtn { bottom: calc(24px + env(safe-area-inset-bottom, 0px)); right: calc(132px + env(safe-area-inset-right, 0px)); }
  #toastWrap { top: 56px; }
  .modalOverlay { padding: 8px calc(8px + env(safe-area-inset-right, 0px)) 8px calc(8px + env(safe-area-inset-left, 0px)); }
  .modalBox { width: min(92vw, 620px); max-height: 92vh; max-height: 92dvh; }
  .modalHead { padding: 9px 14px; }
  .modalBody { padding: 8px 12px; }
  .modalFoot { padding: 8px 14px; }
  #invList { grid-template-columns: repeat(3, 1fr); }
  #startScreen { gap: 8px; padding: 10px; overflow-y: auto; justify-content: flex-start; }
  #startScreen > :first-child { margin-top: auto; }
  #startScreen > :last-child { margin-bottom: auto; }
  #startTitle { font-size: 30px; }
  #startBtn { padding: 10px 36px; margin-top: 2px; }
  #startTips { padding: 6px 12px; }
  #loadingScreen { gap: 10px; }
  #loadingLogo { font-size: 26px; }
}
"""

JS = r"""
(function () {
  function f() { window.dispatchEvent(new Event('resize')); }
  function later() { setTimeout(f, 120); setTimeout(f, 400); }
  window.addEventListener('orientationchange', later);
  if (screen.orientation && screen.orientation.addEventListener) screen.orientation.addEventListener('change', later);
})();
"""

BLOCK = '<!-- landscape-fix v2.4 -->\n<style>' + CSS + '</style>\n<script>' + JS + '</script>\n'
LOGNEW = 'var LOG = [\n    ["Tampilan Landscape", ["Game sekarang auto-rotate: bisa dimainkan portrait maupun landscape.", "HUD, tombol, dan menu otomatis menyesuaikan layar landscape."]],'

def read(p): return open(p, encoding='utf-8').read()
def write(p, s): open(p, 'w', encoding='utf-8').write(s)

def patch_html(p):
    s = read(p)
    s = re.sub(r'<!-- landscape-fix[^>]*-->.*?</script>\s*', '', s, flags=re.S)
    if "lbl.id = 'envLabel'" not in s:
        s = s.replace('document.body.appendChild(lbl);', "lbl.id = 'envLabel'; document.body.appendChild(lbl);", 1)
    s = s.replace('<div id="versionBadge">v2.3</div>', '<div id="versionBadge">v2.4</div>')
    s = s.replace("var VER = 'v2.3'", "var VER = 'v2.4'")
    if 'Tampilan Landscape' not in s:
        s = s.replace('var LOG = [', LOGNEW, 1)
    i = s.rfind('</body>')
    s = s[:i] + BLOCK + s[i:] if i != -1 else s + BLOCK
    write(p, s)
    print('HTML OK  :', p)

def patch_manifest(p):
    s = read(p)
    m = re.search(r'<activity\b[^>]*>', s)
    if not m: return
    tag = m.group(0)
    new = re.sub(r'\s+android:screenOrientation="[^"]*"', '', tag)
    new = new.replace('<activity', '<activity android:screenOrientation="fullSensor"', 1)
    cfg = 'orientation|screenSize|smallestScreenSize|screenLayout|keyboardHidden|keyboard|uiMode'
    if 'android:configChanges="' in new:
        def fix(mm):
            v = set(mm.group(1).split('|')); v.update(cfg.split('|'))
            return 'android:configChanges="' + '|'.join(sorted(v)) + '"'
        new = re.sub(r'android:configChanges="([^"]*)"', fix, new)
    else:
        new = new.replace('<activity', '<activity android:configChanges="' + cfg + '"', 1)
    write(p, s.replace(tag, new, 1))
    print('Manifest OK:', p)

def patch_json(p, val):
    s = read(p)
    n = re.sub(r'("orientation"\s*:\s*)"[^"]*"', r'\1"' + val + '"', s)
    if n != s:
        write(p, n); print('JSON OK  :', p)

for p in ['index.html', 'www/index.html']:
    if os.path.exists(p): patch_html(p)

for p in glob.glob('android*/**/AndroidManifest.xml', recursive=True):
    if '/build/' not in p: patch_manifest(p)

for p in ['manifest.json', 'www/manifest.json']:
    if os.path.exists(p): patch_json(p, 'any')
if os.path.exists('android-twa/twa-manifest.json'):
    patch_json('android-twa/twa-manifest.json', 'default')

print('Selesai.')
