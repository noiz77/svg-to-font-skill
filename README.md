# svg-to-font — Claude Code Skill

A Claude Code skill that turns a folder of SVG glyph files into a complete, production-ready font package: **OTF desktop font**, **WOFF2 web font**, **CSS icon classes**, and an **interactive HTML preview page** — all in one command.

## What it does

Tell Claude something like:

- "Make a font from these SVGs"
- "Convert my SVG glyphs into an icon font"
- "Build an OTF and WOFF2 from the files in `./svg`"

Claude will guide you through naming conventions and config, then run the bundled Python scripts to produce:

```
output/
├── fonts/
│   ├── my-font.otf       # Desktop font (CFF cubic bezier)
│   └── my-font.woff2     # Web font (Brotli-compressed)
├── css/
│   └── my-font.css       # @font-face + icon ::before classes
└── my-font.html          # Interactive preview page
```

## Installation

Clone the repository directly into Claude's skills directory:

```bash
git clone https://github.com/noiz77/svg-to-font-skill.git ~/.claude/skills/svg-to-font
```

Then install the required Python dependencies:

```bash
pip install fonttools brotli
```

That's it. The skill activates automatically the next time you start Claude Code.

## Uninstall

```bash
rm -rf ~/.claude/skills/svg-to-font
```

## Requirements

- Python 3.8+
- `fonttools` and `brotli` Python packages
- Claude Code

## License

MIT
