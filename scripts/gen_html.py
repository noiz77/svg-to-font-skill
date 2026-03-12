#!/usr/bin/env python3
"""
gen_html.py — Generate an interactive HTML font preview page.

The page has two sections:
  1. A live text input box — lets users type directly using the font
     (works because glyphs are mapped to standard Unicode codepoints)
  2. A glyph grid — shows every icon via CSS ::before class (PUA method)

Usage:
    python gen_html.py \
        --config   path/to/config.json \
        --out-dir  path/to/output/ \
        --font-name  my-font \
        --family-name "My Font"
"""
import os
import json
import argparse


def generate(config_path, out_dir, font_name, family_name):
    with open(config_path) as f:
        icons = json.load(f)['icons']

    items_html = ''
    for key, pua_hex in icons.items():
        # Extract the display character — the part after the first '-'
        char = key.split('-', 1)[-1]
        if char == ' ':
            display = 'space'
        else:
            # Escape < > so they render correctly in HTML
            display = char.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Escape the key itself for use in HTML attributes
        safe_key = key.replace('"', '&quot;')

        items_html += f'''\
      <div class="item">
        <i class="{font_name} {safe_key}"></i>
        <span class="label">.{safe_key}</span>
        <span class="label">char: {display}</span>
      </div>
'''

    html = f'''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{family_name} — Font Preview</title>
  <link rel="stylesheet" href="css/{font_name}.css">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{ font-family: sans-serif; background: #f0f1f3; margin: 0; padding: 24px; }}
    h1 {{ text-align: center; color: #183153; margin-bottom: 32px; }}
    .section {{ margin-bottom: 48px; }}
    .section h2 {{ padding-bottom: 8px; border-bottom: 2px solid #ddd; color: #333; margin-bottom: 16px; }}
    .section p {{ color: #555; margin: 0 0 12px; }}
    /* Glyph grid */
    .grid {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); }}
    .item {{
      background: #fff; text-align: center; display: flex; flex-direction: column;
      align-items: center; justify-content: center; border-radius: 8px;
      padding: 14px 10px; box-shadow: 0 1px 4px rgba(0,0,0,.07);
      transition: box-shadow .15s;
    }}
    .item:hover {{ box-shadow: 0 3px 10px rgba(0,0,0,.12); }}
    .{font_name} {{ font-size: 2.2em; margin-bottom: 8px; color: #183153; }}
    .label {{
      font-size: 11px; color: #666; font-family: monospace;
      background: #eef; padding: 2px 5px; border-radius: 3px; margin-top: 4px;
      word-break: break-all;
    }}
    /* Typing demo */
    .type-demo input {{
      font-family: '{family_name}', sans-serif;
      font-size: 2em; width: 100%; padding: 12px;
      border: 1px solid #ccc; border-radius: 6px;
      background: #fff; outline: none;
    }}
    .type-demo input:focus {{ border-color: #4a90e2; box-shadow: 0 0 0 2px rgba(74,144,226,.2); }}
  </style>
</head>
<body>
  <h1>{family_name}</h1>

  <div class="section">
    <h2>Live Typing (Standard Unicode)</h2>
    <p>This font is mapped to standard Unicode codepoints — type in the box below to preview it directly.</p>
    <div class="type-demo">
      <input type="text" value="abc ABC 123 !@#$%" placeholder="Type here...">
    </div>
  </div>

  <div class="section">
    <h2>Glyph Reference (CSS Icon Classes)</h2>
    <p>Use these class names with <code>&lt;i class="{font_name} {font_name}-a"&gt;&lt;/i&gt;</code> in your HTML.</p>
    <div class="grid">
{items_html}    </div>
  </div>
</body>
</html>
'''

    html_path = os.path.join(out_dir, f"{font_name}.html")
    with open(html_path, 'w') as f:
        f.write(html)
    print(f"HTML → {html_path}")


def main():
    p = argparse.ArgumentParser(description="Generate interactive HTML font preview")
    p.add_argument('--config',      required=True, help='Path to icons config JSON')
    p.add_argument('--out-dir',     required=True, help='Output root directory')
    p.add_argument('--font-name',   required=True, help='Font identifier (used in CSS class names)')
    p.add_argument('--family-name', required=True, help='Display family name')
    args = p.parse_args()

    generate(
        config_path=args.config,
        out_dir=args.out_dir,
        font_name=args.font_name,
        family_name=args.family_name,
    )


if __name__ == '__main__':
    main()
