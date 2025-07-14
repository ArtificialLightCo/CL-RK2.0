#!/usr/bin/env python3
import os
import re

TEMPLATES_DIR = "templates"
LANG_PLACEHOLDER = '{{ request.state.locale if request.state.locale else "en" }}'

pattern = re.compile(r"<html([^>]*)>", re.IGNORECASE)

for root, _, files in os.walk(TEMPLATES_DIR):
    for fn in files:
        if not fn.endswith(".html"):
            continue
        path = os.path.join(root, fn)
        text = open(path, encoding="utf-8").read()
        # Replace or insert lang="{{…}}"
        new_text = pattern.sub(
            rf'<html\1 lang="{LANG_PLACEHOLDER}">', text
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"Updated lang attr: {path}")

print("✅ lang attributes added to all HTML templates.")
