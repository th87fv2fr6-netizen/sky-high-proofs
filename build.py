"""Build the Sky High proofs site.

Each shoot is one JSON file in shoots/:
  {
    "slug": "3-39-globe-st-ashgrove",          # URL folder
    "title": "3/39 Globe St",                   # big heading
    "addr": "Ashgrove QLD",                     # line under heading
    "eyebrow": "Photo proofs",                  # small red label
    "property": "3/39 Globe St, Ashgrove",      # first line of the client's selection list
    "autohdr_listing": "3/39 Globe St Ashgrove, QLD, Australia",
    "shoot_id": "2dfcc1ce-...",                 # AutoHDR photoshoot id (CloudFront folder)
    "photos": [["DSC04436.jpg", 800, 534, "g"], ...]   # file, width, height, g=ground a=aerial
  }

Photos are shown straight from AutoHDR's preview server, so nothing is copied.
Run:  python3 build.py   -> writes site/<slug>/index.html for every shoot.
Logo lives at site/logo.png.
"""
import json, os, glob, re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, 'site')
CDN = 'https://d12d7k64f4jt1d.cloudfront.net/'


def rep(t, a, b):
    assert a in t, 'template changed, missing: ' + a[:70]
    return t.replace(a, b, 1)


def display_name(f):
    return re.sub(r'(_replaced_camera)?\.jpe?g$', '', f, flags=re.I)


def page(sh, base):
    photos = sh['photos']
    rows = [[i + 1, display_name(p[0]), p[1], p[2], p[3], p[0]] for i, p in enumerate(photos)]
    t = base.replace('__DATA__', json.dumps(rows, separators=(',', ':')))
    t = rep(t, '<title>The Bonobo Proofs</title>', f"<title>{sh['title']} Proofs</title>")
    t = rep(t, 'Photo proofs · Shot 31 Oct 2026', sh.get('eyebrow', 'Photo proofs'))
    t = rep(t, '<h1>The Bonobo</h1>', f"<h1>{sh['title']}</h1>")
    t = rep(t, '116 Jonson St, Byron Bay NSW 2481', sh['addr'])
    t = rep(t, "const src=i=>'img/bonobo-'+String(i).padStart(3,'0')+'.jpg';", "const src=i=>BASE+P[i-1][5];")
    t = t.replace("'bonobo-picks'", f"'{sh['slug']}-picks'")
    t = rep(t, 'alt="The Bonobo, photo ${i}"', f'alt="{sh["title"]}, photo ${{i}}"')
    t = rep(t, "lbimg.alt='The Bonobo, photo '", f"lbimg.alt='{sh['title']}, photo '")
    t = rep(t, "const txt='The Bonobo, 116 Jonson St, Byron Bay: '", "const txt=PROPERTY+': '")
    t = rep(t, 'loading="lazy" alt=', 'loading="lazy" referrerpolicy="no-referrer" alt=')
    t = rep(t, '<img id="lbimg" alt="">', '<img id="lbimg" alt="" referrerpolicy="no-referrer">')
    t = rep(t, '<link rel="preconnect" href="https://fonts.googleapis.com">',
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://d12d7k64f4jt1d.cloudfront.net">')
    t = rep(t, 'src="logo.png"', 'src="/logo.png"')
    if not any(p[3] == 'a' for p in photos):
        t = rep(t, '<button class="tab" data-f="g" aria-pressed="false">Interior &amp; exterior<span class="n" id="n-g"></span></button>\n', '')
        t = rep(t, '<button class="tab" data-f="a" aria-pressed="false">Aerial<span class="n" id="n-a"></span></button>\n', '')
        t = rep(t, "document.getElementById('n-g').textContent=P.filter(p=>p[4]==='g').length;", '')
        t = rep(t, "document.getElementById('n-a').textContent=P.filter(p=>p[4]==='a').length;", '')

    # Send-my-selection form (Netlify Forms)
    t = rep(t, "When you're done, press <b>Copy my selection</b> and paste it into an email back to us.",
            "When you're done, press <b>Send my selection</b> and add your name. It comes straight to us.")
    t = rep(t, '<button class="btn primary" id="copy">Copy my selection</button>',
            '<button class="btn" id="copy">Copy list</button>\n      <button class="btn primary" id="send">Send my selection</button>')
    t = rep(t, '<div class="listbox" id="listbox" hidden>', '''<form class="sendbox" id="sendbox" hidden>
    <label>Your name<input id="sname" name="name" required autocomplete="name"></label>
    <label>Email<input id="semail" name="email" type="email" autocomplete="email"></label>
    <label>Notes (optional)<input id="snote" name="note"></label>
    <button class="btn primary" type="submit" id="sendgo">Send</button>
  </form>
  <div class="listbox" id="listbox" hidden>''')
    t = rep(t, '.toast{', '''.sendbox{max-width:1400px;margin:10px auto 0;display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px 12px;align-items:end}
.sendbox label{font-size:12px;color:var(--muted);display:block}
.sendbox input{width:100%;font:14px var(--body);padding:9px 10px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);margin-top:4px}
.toast{''')
    t = rep(t, "document.getElementById('copy').disabled=picked.size===0;",
            "document.getElementById('copy').disabled=picked.size===0;document.getElementById('send').disabled=picked.size===0;")
    t = rep(t, "const P=", f"const PROPERTY={json.dumps(sh['property'])};\nconst BASE={json.dumps(base_url(sh))};\nconst P=")
    t = rep(t, "document.getElementById('copy').addEventListener('click',async()=>{", '''const listText=()=>{const ids=[...picked].sort((a,b)=>a-b);return PROPERTY+': '+ids.length+' photos selected\\n'+ids.map(i=>label(i)+'  ('+P[i-1][1]+')').join('\\n')};
document.getElementById('send').addEventListener('click',()=>{const f=document.getElementById('sendbox');f.hidden=!f.hidden;if(!f.hidden)document.getElementById('sname').focus()});
document.getElementById('sendbox').addEventListener('submit',async e=>{
  e.preventDefault();const t=document.getElementById('toast'),b=document.getElementById('sendgo');b.disabled=true;
  const v=id=>document.getElementById(id).value;
  const body=new URLSearchParams({'form-name':'proof-selection',property:PROPERTY,name:v('sname'),email:v('semail'),note:v('snote'),count:String(picked.size),selection:listText()});
  try{const r=await fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body});
    if(!r.ok)throw 0;document.getElementById('sendbox').hidden=true;t.textContent='Sent. Thanks, we\\'ll take it from here.'}
  catch(err){t.textContent='Couldn\\'t send. Press Copy list and email it to jayce@skyhighphotography.com.au instead.'}
  b.disabled=false;
});
document.getElementById('copy').addEventListener('click',async()=>{''')
    return ('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex">
<link rel="icon" href="/logo.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>
<form name="proof-selection" data-netlify="true" netlify-honeypot="bot-field" hidden><input name="bot-field"><input name="property"><input name="name"><input name="email"><input name="note"><input name="count"><textarea name="selection"></textarea></form>
''' + t + '\n</body></html>\n')


def base_url(sh):
    return CDN + sh['shoot_id'] + '/processed/'


def main():
    base = open(os.path.join(HERE, 'template.html')).read()
    for f in sorted(glob.glob(os.path.join(HERE, 'shoots', '*.json'))):
        sh = json.load(open(f))
        d = os.path.join(SITE, sh['slug'])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w').write(page(sh, base))
        print('built', sh['slug'], len(sh['photos']), 'photos')
    open(os.path.join(SITE, 'index.html'), 'w').write(
        '<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>Sky High Photography</title>'
        '<meta http-equiv="refresh" content="0;url=https://www.skyhighphotography.com.au/">')


if __name__ == '__main__':
    main()
