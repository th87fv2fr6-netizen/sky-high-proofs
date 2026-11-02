"""Render the 'photos ready to choose' client email.

Usage: python3 email.py <slug> "<first name>" [--count N]
Prints JSON: {"subject", "htmlBody", "body", "logo_b64"}.
The HTML references the logo as inline attachment 0, so create the Gmail draft with
attachments=[{"content": logo_b64, "mimeType": "image/png", "filename": "skyhigh.png", "inline": true}].
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
    htmlbody = f'''<!doctype html><html><body style="margin:0;padding:0;background:#f4f4f4">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:24px 12px">
<tr><td align="center">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#ffffff;border-radius:8px;overflow:hidden;font-family:Helvetica,Arial,sans-serif;color:#1d1d1f">
<tr><td style="padding:28px 32px 8px 32px"><img src="cid:0" width="160" alt="Sky High Photography" style="display:block;width:160px;height:auto;border:0"></td></tr>
<tr><td style="padding:8px 32px 0 32px">
<p style="margin:0 0 6px 0;font-size:12px;letter-spacing:1.5px;text-transform:uppercase;color:{RED}">Photo proofs</p>
<h1 style="margin:0 0 4px 0;font-size:24px;line-height:1.25;font-weight:bold">{e(sh['title'])}</h1>
{f'<p style="margin:0;font-size:15px;color:#6e6d6d">{e(sh["addr"])}</p>' if sh.get('addr') else ''}
</td></tr>
<tr><td style="padding:20px 32px 0 32px;font-size:15px;line-height:1.6">
<p style="margin:0 0 14px 0">{greet}</p>
<p style="margin:0 0 14px 0">Your edited photos are ready to review. There are {n} images in the gallery. Have a look through and pick the ones you'd like finalised.</p>
</td></tr>
<tr><td align="center" style="padding:10px 32px 6px 32px">
<a href="{url}" style="display:inline-block;background:{RED};color:#ffffff;text-decoration:none;font-weight:bold;font-size:16px;padding:14px 30px;border-radius:6px">View &amp; choose your photos</a>
</td></tr>
<tr><td style="padding:18px 32px 0 32px;font-size:14px;line-height:1.6;color:#3a3a3c">
<p style="margin:0 0 6px 0;font-weight:bold;color:#1d1d1f">How it works</p>
<p style="margin:0">1. Tap the heart on each photo you'd like.<br>2. Tap any photo to see it larger.<br>3. Press <b>Send my selection</b> at the bottom of the page and add your name.</p>
<p style="margin:14px 0 0 0">Once your selection comes through, I'll deliver the final full-resolution files.</p>
</td></tr>
<tr><td style="padding:22px 32px 28px 32px;font-size:15px;line-height:1.6">
<p style="margin:0">Thanks,<br><b>Jayce</b><br><span style="color:#6e6d6d">Sky High Photography</span></p>
</td></tr>
<tr><td style="padding:14px 32px;background:#fafafa;border-top:1px solid #eeeeee;font-size:12px;color:#8e8e93;line-height:1.5">
Link not working? Copy this into your browser:<br><a href="{url}" style="color:#8e8e93">{url}</a>
</td></tr>
</table></td></tr></table></body></html>'''
    text = (f"{greet}\n\nYour edited photos for {prop} are ready to review ({n} images). "
            f"Pick the ones you'd like finalised here:\n{url}\n\n"
            "1. Tap the heart on each photo you'd like.\n2. Tap any photo to see it larger.\n"
            "3. Press Send my selection at the bottom of the page and add your name.\n\n"
            "Once your selection comes through, I'll deliver the final full-resolution files.\n\n"
            "Thanks,\nJayce\nSky High Photography")
    logo = base64.b64encode(open(os.path.join(HERE, 'email-logo.png'), 'rb').read()).decode()
    return dict(subject=subject, htmlBody=htmlbody, body=text, logo_b64=logo)


if __name__ == '__main__':
    a = sys.argv[1:]
    count = int(a[a.index('--count') + 1]) if '--count' in a else None
    print(json.dumps(render(a[0], a[1] if len(a) > 1 and not a[1].startswith('--') else '', count)))
