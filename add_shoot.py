"""Record AutoHDR listings and decide which are ready to publish.

Usage:  python3 add_shoot.py listings.json
listings.json is a list scraped from AutoHDR Listings, one entry per listing:
  {"listing": "3/39 Globe St Ashgrove, QLD, Australia",
   "shoot_id": "2dfcc1ce-...",
   "photos": [["DSC04436.jpg", 800, 534], ...]}      # file name, natural width, height

Rules:
- A listing already in shoots/ (same shoot_id) is updated only if its photo list changed.
- A NEW listing is published only once its photo list is identical on two consecutive
  runs (AutoHDR may still be processing). Until then it waits in state.json.
- Drone files (DJI_...) are tagged aerial; everything else ground.
Prints a JSON summary: {"published": [...], "updated": [...], "waiting": [...]}.
"""
import json, os, re, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, 'state.json')


def slugify(s):
    s = s.lower().replace('/', '-')
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def parse_listing(name):
    """'3/39 Globe St Ashgrove, QLD, Australia' -> title '3/39 Globe St', suburb 'Ashgrove', state 'QLD'.
    'The Bonobo 116 Jonson St, Byron Bay NSW 2481, Australia' -> kept whole when it doesn't fit."""
    name = re.sub(r',?\s*Australia\s*$', '', name.strip())
    parts = [p.strip() for p in name.split(',')]
    m = re.match(r'^(.*?\b(?:St|Street|Rd|Road|Ave|Avenue|Tce|Terrace|Ct|Court|Dr|Drive|Pl|Place|Cres|Crescent|Pde|Parade|Way|Lane|Ln|Cl|Close|Hwy|Highway|Bvd|Boulevard|Cct|Circuit|Gr|Grove|Esp|Esplanade))\s+(.+)$', parts[0], re.I)
    if m and len(parts) >= 2 and len(parts[1]) <= 4:
        street, suburb = m.group(1), m.group(2)
        st = parts[1]
        return dict(title=street, addr=f'{suburb} {st}', property=f'{street}, {suburb}', slug=slugify(f'{street} {suburb}'))
    # fallback: whole first part as title, rest as address line
    title = parts[0]
    addr = ', '.join(parts[1:]) if len(parts) > 1 else ''
    return dict(title=title, addr=addr, property=name, slug=slugify(parts[0]))


def main():
    listings = json.load(open(sys.argv[1]))
    state = json.load(open(STATE)) if os.path.exists(STATE) else {'pending': {}}
    existing = {}
    for f in glob.glob(os.path.join(HERE, 'shoots', '*.json')):
        sh = json.load(open(f))
        existing[sh['shoot_id']] = (f, sh)
    out = {'published': [], 'updated': [], 'waiting': []}
    for L in listings:
        photos = [[p[0], int(p[1]), int(p[2]), 'a' if p[0].upper().startswith('DJI') else 'g'] for p in L['photos']]
        if not photos:
            continue
        sid = L['shoot_id']
        if sid in existing:
            f, sh = existing[sid]
            if sh['photos'] != photos:
                sh['photos'] = photos
                json.dump(sh, open(f, 'w'), indent=1)
                out['updated'].append(sh['slug'])
            continue
        sig = [p[0] for p in photos]
        prev = state['pending'].get(sid)
        if prev != sig:
            state['pending'][sid] = sig
            out['waiting'].append(L['listing'])
            continue
        info = parse_listing(L['listing'])
        slug = info['slug']
        n = 2
        while os.path.exists(os.path.join(HERE, 'shoots', slug + '.json')):
            slug = f"{info['slug']}-{n}"; n += 1
        sh = dict(slug=slug, title=info['title'], addr=info['addr'], eyebrow='Photo proofs',
                  property=info['property'], autohdr_listing=L['listing'], shoot_id=sid, photos=photos)
        json.dump(sh, open(os.path.join(HERE, 'shoots', slug + '.json'), 'w'), indent=1)
        state['pending'].pop(sid, None)
        out['published'].append({'slug': slug, 'listing': L['listing'], 'property': info['property'],
                                 'url': f'https://proofs.skyhighphotography.com.au/{slug}/', 'photos': len(photos)})
    json.dump(state, open(STATE, 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
