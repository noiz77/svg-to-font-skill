# svg-to-font — Claude Code Skill

A Claude Code skill that turns a folder of SVG glyph files into a complete, production-ready font package: **OTF desktop font**, **WOFF2 web font**, **CSS icon classes**, and an **interactive HTML preview page** — all in one command.

## How to Create Your Own SVG Glyphs

If you don't have SVG glyph files yet, you can use a **text-to-image model** (recommended: Nano Banana Pro / Nano Banana 2) to generate a font image, then process it with design software. Here's the workflow (for Latin/English fonts):

### Step 1 — Generate the Font Design

#### Option A: With a reference font image

![Option A: reference image + prompt](screenshots/image1.png)

Reference image + prompt:

```
Based on the design style of this font, create a complete English typeface including: a–z, A–Z, 0–9, and special characters. Arrange in order: all lowercase, all uppercase, then special characters.
```

#### Option B: No reference image

![Option B: prompt only](screenshots/image2.png)

Describe the style in your prompt:

```
Design a typewriter-style English font.
Include: a–z, A–Z, 0–9, and special characters. Arrange in order: all lowercase, all uppercase, 0–9, then special characters.
White background, black letterforms.
```

> The generated image may have duplicate or missing characters. Regenerate if needed, or make manual adjustments afterward.

### Step 2 — Refine the Glyphs

![Organizing SVGs in Figma](screenshots/image3.png)

> Convert the generated image to SVG using a plugin or Adobe Illustrator's **Image Trace → Black and White Logo** option. Import into Figma, merge shapes, align baselines, and name each artboard. Export all artboards as SVG (a full English character set is typically 94 artboards).

### Step 3 — Run the Skill to Generate the Font

![Using the Skill to generate the font](screenshots/image4.png)

## What the Skill Does

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
