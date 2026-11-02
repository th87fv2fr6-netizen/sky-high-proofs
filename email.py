"""Render the 'photos ready to choose' client email.

Usage: python3 email.py <slug> "<first name>" [--count N]
Prints JSON: {"subject", "htmlBody", "body"}. The logo is styled text (no image attachment),
because Apple Mail shows inline attachments a second time at the bottom.
"""
import json, sys, os, base64, html

HERE = os.path.dirname(os.path.abspath(__file__))
RED = '#ec1c24'


def render(slug, first, count=None):
    sh = json.load(open(os.path.join(HERE, 'shoots', slug + '.json')))
    url = f'https://proofs.skyhighphotography.com.au/{slug}/'
    prop = sh['title'] + (f", {sh['addr']}" if sh.get('addr') else '')
    n = count or len(sh['photos'])
    e = html.escape
    greet = f'Hi {e(first)},' if first else 'Hi there,'
    subject = f"Your photos are ready to choose: {sh['title']}"
    htmlbody = f"""<div style="font-family:Helvetica,Arial,sans-serif;color:#1d1d1f;font-size:15px;line-height:1.6;max-width:560px">
<table cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width:560px;font-family:Helvetica,Arial,sans-serif;color:#1d1d1f;font-size:15px;line-height:1.6">
<tr><td style="padding:4px 0 18px 0"><table cellpadding="0" cellspacing="0" border="0"><tr><td style="font-family:Ubuntu,Helvetica,Arial,sans-serif;font-size:32px;line-height:1;letter-spacing:-0.5px"><span style="color:#a8a7a7">sky</span><span style="color:{RED};font-weight:bold">high</span></td></tr><tr><td align="right" style="font-family:Ubuntu,Helvetica,Arial,sans-serif;font-size:13px;line-height:1.2;color:#a8a7a7">photography</td></tr></table></td></tr>
<tr><td style="padding:0;font-size:12px;letter-spacing:1.5px;text-transform:uppercase;color:{RED}">Photo proofs</td></tr>
<tr><td style="padding:2px 0 0 0;font-size:24px;line-height:1.25;font-weight:bold;color:#1d1d1f">{e(sh['title'])}</td></tr>
{f'<tr><td style="padding:2px 0 0 0;font-size:15px;color:#6e6d6d">{e(sh["addr"])}</td></tr>' if sh.get('addr') else ''}
<tr><td style="padding:22px 0 0 0">{greet}</td></tr>
<tr><td style="padding:12px 0 0 0">Your edited photos are ready to review. There are {n} images in the gallery. Have a look through and pick the ones you'd like finalised.</td></tr>
<tr><td style="padding:22px 0 4px 0">
<table cellpadding="0" cellspacing="0" border="0"><tr><td bgcolor="{RED}" style="background-color:{RED};border-radius:6px;padding:13px 28px"><a href="{url}" style="color:#ffffff;text-decoration:none;font-weight:bold;font-size:16px">View &amp; choose your photos</a></td></tr></table>
</td></tr>
<tr><td style="padding:22px 0 0 0;font-weight:bold">How it works</td></tr>
<tr><td style="padding:4px 0 0 0;font-size:14px;color:#3a3a3c">1. Tap the heart on each photo you'd like.<br>2. Tap any photo to see it larger.<br>3. Press <b>Send my selection</b> at the top of the page and add your name.</td></tr>
<tr><td style="padding:14px 0 0 0;font-size:14px;color:#3a3a3c">Once your selection comes through, I'll deliver the final full-resolution files.</td></tr>
<tr><td style="padding:22px 0 24px 0">Thanks,<br><b>Jayce</b><br><span style="color:#6e6d6d">Sky High Photography</span></td></tr>
<tr><td style="padding:14px 0 0 0;border-top:1px solid #e5e5e5;font-size:12px;color:#8e8e93;line-height:1.5">Link not working? Copy this into your browser:<br><a href="{url}" style="color:#8e8e93">{url}</a></td></tr>
</table></div>"""
    text = (f"{greet}\n\nYour edited photos for {prop} are ready to review ({n} images). "
            f"Pick the ones you'd like finalised here:\n{url}\n\n"
            "1. Tap the heart on each photo you'd like.\n2. Tap any photo to see it larger.\n"
            "3. Press Send my selection at the top of the page and add your name.\n\n"
            "Once your selection comes through, I'll deliver the final full-resolution files.\n\n"
            "Thanks,\nJayce\nSky High Photography")
    return dict(subject=subject, htmlBody=htmlbody, body=text)


if __name__ == '__main__':
    a = sys.argv[1:]
    count = int(a[a.index('--count') + 1]) if '--count' in a else None
    print(json.dumps(render(a[0], a[1] if len(a) > 1 and not a[1].startswith('--') else '', count)))
