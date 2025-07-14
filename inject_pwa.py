# inject_pwa.py — Batch-inject PWA manifest and service worker into HTML <head>

import os
from pathlib import Path

FRONTEND_DIR = "frontend"
MANIFEST_LINE = '<link rel="manifest" href="/manifest.json">'
SW_SCRIPT = """<script>
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('/service-worker.js');
</script>"""

def already_has_pwa(lines):
    return any("rel=\"manifest\"" in l or "serviceWorker.register" in l for l in lines)

def inject_pwa_to_html(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if already_has_pwa(lines):
        print(f"Already present: {path}")
        return
    injected = []
    injected_pwa = False
    for line in lines:
        injected.append(line)
        if "<head" in line:
            # If <head> tag on its own line
            continue
        if "<head>" in line or "<head " in line:
            injected.append("  " + MANIFEST_LINE + "\n")
            injected.append("  " + SW_SCRIPT + "\n")
            injected_pwa = True
    if not injected_pwa:
        # Try to find first <meta> or <title> line as a backup
        for i, line in enumerate(lines):
            if "<title>" in line or "<meta" in line:
                injected.insert(i+1, "  " + MANIFEST_LINE + "\n  " + SW_SCRIPT + "\n")
                break
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(injected)
    print(f"Injected into: {path}")

def main():
    html_files = list(Path(FRONTEND_DIR).glob("*.html"))
    for html in html_files:
        inject_pwa_to_html(html)

if __name__ == "__main__":
    main()
