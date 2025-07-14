import os, json
from fastapi import Request

class I18n:
    def __init__(self, default="en", locales_dir="locales"):
        self.default = default
        self.locales_dir = locales_dir
        self.cache = {}

    def load(self, code):
        if code in self.cache:
            return self.cache[code]
        path = os.path.join(self.locales_dir, f"{code}.json")
        if not os.path.isfile(path):
            path = os.path.join(self.locales_dir, f"{self.default}.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.cache[code] = data
        return data

    def gettext(self, request: Request, key: str) -> str:
        locale = getattr(request.state, "locale", self.default)
        strings = self.load(locale)
        return strings.get(key, self.load(self.default).get(key, key))
