#!/usr/bin/env python3
"""
translate_locales_argos.py

1) Installs Argos Translate packages for English → target languages.
2) Reads locales/en.json, translates every string, writes locales/{code}.json.
"""

import os, json
import argostranslate.package
import argostranslate.translate

# Your target ISO codes (must match generate script)
TARGET_LANGS = [
    "es","fr","de","it","pt","zh","ja","ko","ar","ru",
    "hi","bn","ur","tr","vi","th","id","nl","sv","da",
    "fi","no","pl","uk","he","el","cs","hu","ro","bg",
    "ms","ta","te"
]

os.makedirs("locales", exist_ok=True)

# 1. Install needed Argos packages
print("🔍 Fetching available Argos packages…")
available = argostranslate.package.get_available_packages()
to_install = [p for p in available if p.from_code=="en" and p.to_code in TARGET_LANGS]

if not to_install:
    print("⚠️ No Argos packages for English→targets. Exiting.")
    exit(1)

for pkg in to_install:
    print(f"📥 Installing en→{pkg.to_code} model…")
    path = pkg.download()
    argostranslate.package.install_from_path(path)

# 2. Load languages
langs = argostranslate.translate.get_installed_languages()
en_lang = next((l for l in langs if l.code=="en"), None)
if not en_lang:
    print("❌ English model missing. Exiting."); exit(1)

# 3. Read base English JSON
base_path = "locales/en.json"
if not os.path.isfile(base_path):
    print("❌ locales/en.json missing. Run generate_full_locales.py first."); exit(1)

with open(base_path, encoding="utf-8") as f:
    base_strings = json.load(f)

# 4. Translate and overwrite each locale file
for code in TARGET_LANGS:
    to_lang = next((l for l in langs if l.code==code), None)
    if not to_lang:
        print(f"⚠️ No translation model for en→{code}, skipping.")
        continue

    print(f"🔄 Translating into {code}.json…")
    translator = en_lang.get_translation(to_lang)
    out = {}
    for k, txt in base_strings.items():
        try:
            out[k] = translator.translate(txt)
        except Exception as e:
            print(f"   ⚠️  '{k}' failed: {e}; using EN")
            out[k] = txt

    with open(f"locales/{code}.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"✅ locales/{code}.json written")

print("🎉 Argos translation complete.")
