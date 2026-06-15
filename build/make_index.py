#!/usr/bin/env python3
"""Embed cards.json into index.template.html -> index.html (self-contained)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl = open(os.path.join(ROOT, "index.template.html"), encoding="utf-8").read()
data = open(os.path.join(ROOT, "cards.json"), encoding="utf-8").read()

# JSON sits inside a <script> tag; only "</" could prematurely close it.
data = data.replace("</", "<\\/")
html = tpl.replace("__CARDS__", data)

with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)
print(f"wrote index.html ({len(html)//1024} KB)")
