#!/usr/bin/env python3
"""Build the static pages from Markdown sources.

Usage: python3 tools/build.py <privacy-policy.md> [--set=NAME=value ...] [--allow-placeholders]
The policy file may have notes above a line '# Публикуемый текст'; only the text after it is published.
Pages: /, /astir/privacy/, /astir/support/. Placeholders {{...}} left in the text make the build fail
unless --allow-placeholders is given (so that nothing unfinished is published by accident).
"""
import html, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
EMAIL = "harborlight-apps@proton.me"

CSS = """body{font:17px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;max-width:42rem;margin:2rem auto;padding:0 1rem;color:#1d1d1f;background:#fff}
h1{font-size:1.7rem}h2{font-size:1.2rem;margin-top:2rem}a{color:#0a64c8}code{background:#f2f2f4;padding:.1em .3em;border-radius:4px}
footer{margin-top:3rem;font-size:.85rem;color:#6e6e73}
@media(prefers-color-scheme:dark){body{color:#f5f5f7;background:#1c1c1e}a{color:#64a8ff}code{background:#2c2c2e}footer{color:#98989d}}"""

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    t = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"(?<![\w>\"/])([\w.+-]+@[\w-]+(?:\.[\w-]+)+)", r'<a href="mailto:\1">\1</a>', t)
    return t

def md(text):
    out, para, bullets = [], [], []
    def flush():
        nonlocal para, bullets
        if para:
            out.append("<p>" + "<br>\n".join(inline(x) for x in para) + "</p>")
            para = []
        if bullets:
            out.append("<ul>" + "".join(f"<li>{inline(b)}</li>" for b in bullets) + "</ul>")
            bullets = []
    for line in text.splitlines():
        if not line.strip():
            flush()
        elif line.startswith("# "):
            flush(); out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.startswith("## "):
            flush(); out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("- "):
            if para: flush()
            bullets.append(line[2:])
        else:
            if bullets: flush()
            para.append(line)
    flush()
    return "\n".join(out)

def page(title, body, back=None):
    nav = f'<p><a href="{back[1]}">{back[0]}</a></p>' if back else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head>
<body>
{nav}
{body}
<footer>Harborlight Apps</footer>
</body></html>
"""

SUPPORT = f"""# Astir — Support

Write to us at {EMAIL}. We read every message.

## An alarm did not ring

This matters most to us. Please include:
- your iPhone model and iOS version;
- the Astir version (at the bottom of Settings in the app);
- the alarm time and repeat days, and what happened instead;
- whether Silent mode, a Focus mode or Low Power Mode was on.

## Subscriptions and refunds

Subscriptions are sold and billed by Apple. To cancel, open Settings on your iPhone, tap your name, then Subscriptions. For refunds, use reportaproblem.apple.com. We cannot cancel or refund on Apple's behalf.

## Privacy requests

To ask what we hold or to have it deleted, email us and follow the steps in section 4 of the [Privacy Policy](/astir/privacy/).
"""

INDEX = """# Harborlight Apps

Apps for iPhone.

- [Astir: Heavy Sleeper Alarm](/astir/privacy/) — Privacy Policy
- [Astir: Heavy Sleeper Alarm](/astir/support/) — Support
"""

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    allow = "--allow-placeholders" in sys.argv
    values = dict(a[6:].split("=", 1) for a in sys.argv[1:] if a.startswith("--set=") and "=" in a[6:])
    if not args:
        sys.exit(__doc__)
    src = pathlib.Path(args[0]).read_text(encoding="utf-8")
    marker = "# Публикуемый текст"
    policy = src.split(marker, 1)[1] if marker in src else src
    policy = policy.strip("\n")
    for k, v in values.items():
        policy = policy.replace("{{" + k + "}}", v)
    pages = {
        "index.html": page("Harborlight Apps", md(INDEX)),
        "astir/privacy/index.html": page("Astir — Privacy Policy", md(policy), ("Support", "/astir/support/")),
        "astir/support/index.html": page("Astir — Support", md(SUPPORT), ("Privacy Policy", "/astir/privacy/")),
    }
    left = sorted({m for p in pages.values() for m in re.findall(r"\{\{\w+\}\}", p)})
    if left and not allow:
        sys.exit("Placeholders left (nothing written): " + ", ".join(left))
    for rel, content in pages.items():
        f = ROOT / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content, encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print("written:", ", ".join(pages), "| placeholders:", left or "none")

main()
