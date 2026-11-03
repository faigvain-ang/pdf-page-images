"""Build this independent bilingual site. Python 3.11+, no dependencies."""
import html
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site"
OUT = ROOT / "docs"

STYLE = r"""
:root{--paper:#f4f1e7;--ink:#173a30;--accent:#a44228;--muted:#52645c;--line:#b8c4b9;--display:Georgia,'Times New Roman',serif;--body:Cambria,Georgia,serif}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:19px/1.7 var(--body)}a{color:inherit;text-underline-offset:.23em}a:hover{color:var(--accent)}a:focus-visible{outline:3px solid var(--accent);outline-offset:5px}.skip{position:absolute;left:1rem;top:-6rem;background:var(--paper);padding:.5rem;z-index:10}.skip:focus{top:0}.shell{max-width:1190px;margin:auto;padding:0 5vw}header{display:flex;align-items:center;justify-content:space-between;gap:2rem;padding:28px 0;border-bottom:1px solid var(--line)}.brand{font:bold 1.25rem var(--display);letter-spacing:-.04em;text-decoration:none}.brand-mark{color:var(--accent);margin-right:.6em}nav{display:flex;gap:1.2rem;font:14px/1.6 Consolas,monospace;flex-wrap:wrap}nav [aria-current]{text-decoration:underline;text-decoration-thickness:2px}.hero{padding:82px 0 65px;max-width:1000px}.eyebrow,.meta{font:12px/1.7 Consolas,monospace;text-transform:uppercase;letter-spacing:.17em;color:var(--accent)}h1,h2,h3{font-family:var(--display);line-height:1.08;letter-spacing:-.045em}h1{font-size:clamp(3.1rem,7vw,6.4rem);font-weight:normal;margin:.35em 0}h2{font-size:2rem;margin:1.5em 0 .7em}h3{font-size:1.5rem}.lead{font-size:1.35rem;max-width:740px;color:var(--muted)}.rule{width:65px;border-top:4px solid var(--accent);margin:2rem 0}.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:26px;margin:0 0 65px}.card{display:flex;flex-direction:column;min-height:245px;border-top:1px solid var(--ink);padding:22px 0;position:relative}.card h2{font-size:2rem;margin:.4em 0}.card p{color:var(--muted);font-size:1rem}.card .read{margin-top:auto;font:13px Consolas,monospace}.tool-panel{border:1px solid var(--line);padding:30px;margin:0 0 65px;display:grid;grid-template-columns:1fr 1.3fr;gap:35px}.tool-panel>*{min-width:0}.tool-panel h2{margin:0;overflow-wrap:anywhere}.tool-panel p{font-size:1rem;overflow-wrap:anywhere}.prose{max-width:780px;padding-bottom:65px}.prose p,.prose li{max-width:75ch}.prose h2{padding-top:.3em}.prose a{overflow-wrap:anywhere}pre{font:14px/1.75 Consolas,'Courier New',monospace;background:color-mix(in srgb,var(--ink) 5%,var(--paper));border-left:3px solid var(--accent);padding:20px;overflow:auto;white-space:pre;max-width:100%}code{font: .83em Consolas,monospace;overflow-wrap:anywhere}pre code{font:inherit;overflow-wrap:normal}.note{padding:20px 24px;border-left:3px solid var(--accent);background:color-mix(in srgb,var(--ink) 4%,var(--paper));font-size:1rem}footer{border-top:1px solid var(--line);padding:30px 0 45px;font:13px/1.8 Consolas,monospace;color:var(--muted)}.footer-links{display:flex;flex-wrap:wrap;gap:1rem}.back{display:inline-block;margin-top:1rem;font:14px Consolas,monospace}.language-choice{display:flex;gap:24px;margin:3rem 0}.language-choice a{border:1px solid var(--ink);padding:18px 32px;text-decoration:none}
body.workshop{--paper:#152626;--ink:#eef1dc;--accent:#efaa86;--muted:#b8c8bd;--line:#46605b;--display:Consolas,'Courier New',monospace;--body:'Trebuchet MS',sans-serif}body.workshop .shell{max-width:1260px}body.workshop header{border-bottom:4px solid var(--accent)}body.workshop .hero{max-width:none;display:grid;grid-template-columns:1fr 1.4fr;gap:15px 70px}body.workshop .hero h1{grid-column:2;font-size:clamp(2.8rem,5vw,4.5rem);margin:0}body.workshop .hero .eyebrow{grid-column:1;grid-row:1;border-top:1px solid var(--line);padding-top:14px}body.workshop .hero .lead{grid-column:2}body.workshop .hero .rule{grid-column:1;grid-row:2;width:100%}body.workshop .card{border:1px solid var(--line);padding:28px}body.workshop .card h2{font-size:1.7rem;font-weight:normal}body.workshop .tool-panel{border:none;border-top:2px solid var(--accent);padding:28px 0}body.workshop .prose{margin-left:auto;margin-right:auto}
body.images{--paper:#f8f9fc;--ink:#202f5a;--accent:#164ddd;--muted:#58627c;--line:#c4cbdc;--display:'Trebuchet MS',Verdana,sans-serif;--body:Verdana,'Trebuchet MS',sans-serif;font-size:17px}body.images header{border:0}body.images .hero{margin:28px 0 60px;padding:45px;border:2px solid var(--ink);max-width:none;box-shadow:12px 12px 0 #dce4f9}body.images h1{font-weight:800;font-size:clamp(2.9rem,6vw,5.5rem);max-width:900px}body.images .rule{display:none}body.images .cards{grid-template-columns:1fr;gap:0;border-bottom:1px solid var(--line)}body.images .card{display:grid;grid-template-columns:80px 1fr 1fr;gap:25px;min-height:0;padding:30px 0;border-color:var(--line)}body.images .card h2{font-size:1.8rem;margin:0}body.images .card p{margin:0}body.images .card .read{grid-column:2}body.images .tool-panel{border:0;background:#e9eefb;grid-template-columns:1fr 1.7fr}
body.journal{--paper:#fcf3e7;--ink:#452b24;--accent:#ad3c27;--muted:#775e54;--line:#c6ab98;--display:'Palatino Linotype',Palatino,Georgia,serif;--body:Georgia,serif}body.journal header{border-top:7px solid var(--ink);margin-top:20px}body.journal .hero{max-width:960px;margin:auto;text-align:center;padding-bottom:75px}body.journal .hero .lead{margin:auto}body.journal .hero .rule{margin:30px auto}body.journal h1{font-style:italic;font-size:clamp(3.4rem,8vw,7rem)}body.journal .cards{grid-template-columns:repeat(3,minmax(0,1fr));gap:38px}body.journal .card h2{font-size:1.9rem}body.journal .prose{margin:auto}body.journal .tool-panel{border:0;border-top:1px solid var(--ink);padding-left:0;padding-right:0}
@media(max-width:760px){header{align-items:flex-start;gap:1rem;flex-direction:column}.hero{padding:48px 0}.cards,body.journal .cards{grid-template-columns:1fr}.tool-panel,body.images .tool-panel{grid-template-columns:1fr}.hero .lead{font-size:1.15rem}body.workshop .hero{display:block}body.images .hero{padding:25px 20px;box-shadow:6px 6px 0 #dce4f9}body.images .card{grid-template-columns:1fr;gap:12px}body.images .card .read{grid-column:auto}.shell{padding:0 6vw}h1{overflow-wrap:anywhere}.language-choice{flex-direction:column}}@media(prefers-reduced-motion:no-preference){.hero{animation:arrive .55s ease-out}@keyframes arrive{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}}
"""


def build():
    config = json.loads((SOURCE / "config.json").read_text(encoding="utf-8"))
    content = json.loads((SOURCE / "content.json").read_text(encoding="utf-8"))
    base = "https://" + config["hostname"]
    github = "https://github.com/faigvain-ang/" + config["repo"]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "style.css").write_text(STYLE, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "CNAME").write_text(config["hostname"] + "\n", encoding="ascii")
    pages = []
    esc = html.escape

    def url(lang, slug=""):
        return f"/{lang}/" + (slug + "/" if slug else "")

    def write(lang, slug, title, description, main, root=False):
        path = "/" if root else url(lang, slug)
        en = "/en/" if root else url("en", slug)
        es = "/es/" if root else url("es", slug)
        current = "es" if lang == "es" else "en"
        tr = lambda a, b: b if current == "es" else a
        document = f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · {esc(config['brand'])}</title><meta name="description" content="{esc(description, quote=True)}">
<link rel="canonical" href="{base}{path}"><link rel="alternate" hreflang="en" href="{base}{en}"><link rel="alternate" hreflang="es" href="{base}{es}"><link rel="alternate" hreflang="x-default" href="{base}{'/' if root or not slug else url('en',slug)}">
<link rel="stylesheet" href="/style.css"><meta name="theme-color" content="{config['color']}"></head>
<body class="{config['theme']}"><a class="skip" href="#main">{tr('Skip to content','Saltar al contenido')}</a><div class="shell">
<header><a class="brand" href="/{current}/"><span class="brand-mark" aria-hidden="true">{config['mark']}</span>{esc(config['brand'])}</a><nav aria-label="{tr('Main navigation','Navegación principal')}"><a href="/{current}/">{tr('Notebook','Cuaderno')}</a><a href="/{current}/about/">{tr('About','Acerca de')}</a><a href="{github}">{tr('Source','Código')}</a><a href="{en}" lang="en" hreflang="en" {'aria-current="page"' if current == 'en' else ''}>EN</a><a href="{es}" lang="es" hreflang="es" {'aria-current="page"' if current == 'es' else ''}>ES</a></nav></header>
<main id="main">{main}</main><footer><p>{tr('Independent open-source notebook, maintained by the related-product team under faigvain-ang. Not an independent review.','Cuaderno de código abierto mantenido por el equipo de productos relacionados, bajo faigvain-ang. No es una reseña independiente.')}</p><div class="footer-links"><a href="/{current}/about/">{tr('Maintenance & relationship','Mantenimiento y relación')}</a><a href="{github}">GitHub / MIT</a><a href="/sitemap.xml">Sitemap</a></div><p>{tr('No document uploads. No tracking, account, backend, external fonts or CDN scripts.','Sin carga de documentos, seguimiento, cuentas, backend, fuentes externas ni scripts de CDN.')}</p></footer></div></body></html>'''
        destination = OUT / path.strip("/") / "index.html" if not root else OUT / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(document, encoding="utf-8")
        pages.append(path)

    for lang in ("en", "es"):
        text = config[lang]
        read = "Read the note" if lang == "en" else "Leer la nota"
        cards = "".join(f'<article class="card"><span class="meta">{i + 1:02d} / {esc(article[lang]["kind"])}</span><h2><a href="{url(lang,article["slug"])}">{esc(article[lang]["title"])}</a></h2><p>{esc(article[lang]["description"])}</p><a class="read" href="{url(lang,article["slug"])}">{read} →</a></article>' for i, article in enumerate(content))
        panel = f'<section class="tool-panel" aria-label="{esc(text["panel_title"])}"><div><span class="eyebrow">LOCAL / OPEN SOURCE</span><h2>{esc(text["panel_title"])}</h2><p>{text["panel_intro"]}</p><a href="{github}">{esc(text["source_label"])}</a></div><div>{text["panel_body"]}</div></section>'
        hero = f'<section class="hero"><span class="eyebrow">{esc(text["eyebrow"])}</span><h1>{esc(text["title"])}</h1><div class="rule" aria-hidden="true"></div><p class="lead">{esc(text["intro"])}</p></section>'
        write(lang, "", text["title"], text["description"], hero + '<section class="cards" aria-label="'+esc(text['notes_label'])+'">' + cards + '</section>' + panel)
        about_title = "Who maintains this notebook" if lang == "en" else "Quién mantiene este cuaderno"
        about = text["about"] + ('<h2>How this site works</h2><p>Articles use synthetic data. This is a static educational site: commands run on your own computer, not in the browser. Runtime dependencies, if any, are installed separately as documented in the repository. No files are uploaded here, and there are no analytics, third-party fonts, CDN scripts, backend or login. The related cloud services have their own data handling.</p>' if lang == "en" else '<h2>Cómo funciona este sitio</h2><p>Los artículos usan datos sintéticos. Este sitio educativo es estático: los comandos se ejecutan en su ordenador, no en el navegador. Las dependencias, si existen, se instalan por separado según el repositorio. Aquí no se cargan archivos ni hay analítica, fuentes externas, scripts CDN, backend o cuentas. Los servicios en la nube relacionados gestionan sus datos por separado.</p>')
        write(lang, "about", about_title, text["about_description"], f'<section class="hero"><span class="eyebrow">ABOUT / MAINTENANCE</span><h1>{about_title}</h1></section><article class="prose">{about}<p><a href="{github}">{github}</a> · MIT</p></article>')
        for article in content:
            item = article[lang]
            main = f'<section class="hero"><span class="eyebrow">{esc(item["kind"])} / {esc(config["brand"])}</span><h1>{esc(item["title"])}</h1><p class="lead">{esc(item["description"])}</p></section><article class="prose">{item["body"]}<a class="back" href="/{lang}/">← {text["notes_label"]}</a></article>'
            write(lang, article["slug"], item["title"], item["description"], main)
    write("en", "", "Choose your notebook language / Elija idioma", "Practical finance and document notes in English and Spanish. Notas de finanzas y documentos en inglés y español.", '<section class="hero"><span class="eyebrow">ENGLISH / ESPAÑOL</span><h1>'+esc(config["brand"])+'</h1><p class="lead">'+esc(config["en"]["intro"])+'</p><div class="language-choice"><a href="/en/" lang="en">Read in English →</a><a href="/es/" lang="es">Leer en español →</a></div></section>', root=True)
    entries = []
    for path in sorted(pages):
        if path == "/":
            en, es, default = "/en/", "/es/", "/"
        else:
            tail = path.split("/", 2)[2]
            en, es = "/en/" + tail, "/es/" + tail
            default = "/" if not tail else en
        entries.append('<url><loc>' + escape(base + path) + '</loc>' + ''.join(f'<xhtml:link rel="alternate" hreflang="{language}" href="{escape(base + link)}"/>' for language, link in (("en",en),("es",es),("x-default",default))) + '</url>')
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">' + ''.join(entries) + '</urlset>\n', encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="ascii")
    print(f"{config['repo']}: {len(pages)} HTML pages -> {OUT}")


if __name__ == "__main__":
    build()
