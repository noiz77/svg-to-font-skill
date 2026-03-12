#!/usr/bin/env python3
"""
gen_css.py — Generate @font-face declaration and icon CSS classes.

Usage:
    python gen_css.py \
        --config   path/to/config.json \
        --out-dir  path/to/output/ \
        --font-name  my-font \
        --family-name "My Font"
"""
import os
import re
import json
import argparse


def css_escape(name):
    """Escape characters that are not valid unquoted in a CSS class selector."""
    return re.sub(r'([^a-zA-Z0-9_-])', r'\\\1', name)


def generate(config_path, out_dir, font_name, family_name):
    with open(config_path) as f:
        icons = json.load(f)['icons']

    lines = [
        f"@font-face {{",
        f"  font-family: '{family_name}';",
        f"  /* WOFF2: modern browsers (preferred); OTF: local fallback */",
        f"  src: url('../fonts/{font_name}.woff2') format('woff2'),",
        f"       url('../fonts/{font_name}.otf') format('opentype');",
        f"}}",
        f"",
        f".{font_name} {{",
        f"  font-family: '{family_name}' !important;",
        f"  font-style: normal;",
        f"  -webkit-font-smoothing: antialiased;",
        f"  -moz-osx-font-smoothing: grayscale;",
        f"}}",
        f"",
    ]

    for key, pua_hex in icons.items():
        # CSS-escape the class name so special chars (!, @, ,, :, etc.) don't
        # break the selector. HTML class attributes don't need escaping.
        escaped = css_escape(key)
        lines.append(f".{escaped}::before {{ content: \"\\{pua_hex}\"; }}")

    css_path = os.path.join(out_dir, 'css', f"{font_name}.css")
    os.makedirs(os.path.dirname(css_path), exist_ok=True)
    with open(css_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"CSS → {css_path}")


def main():
    p = argparse.ArgumentParser(description="Generate CSS for SVG-built font")
    p.add_argument('--config',      required=True, help='Path to icons config JSON')
    p.add_argument('--out-dir',     required=True, help='Output root directory')
    p.add_argument('--font-name',   required=True, help='Font identifier (used in class names)')
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
