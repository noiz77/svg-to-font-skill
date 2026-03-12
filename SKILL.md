---
name: svg-to-font
description: Build a production-ready font package (OTF + WOFF2 + CSS + HTML preview) from a set of SVG glyph files. Use this skill whenever the user mentions making a font from SVGs, converting SVG glyphs to a typeface, building an icon font, generating OTF or WOFF2 files, or provides a folder of SVG files and asks to turn them into a usable font. Even if the user just says "make a font" or "package these SVGs", use this skill.
---

# SVG → Font Package Builder

This skill turns a set of SVG glyph files into a complete, installable font package: an OTF desktop font, a WOFF2 web font, a CSS icon class file, and an interactive HTML preview page.

---

## Step 1: Gather Required Information

Before doing anything else, collect the four required inputs. Infer what you can from context (open files, project structure); ask the user only for what's genuinely missing.

| Input | Description | Example |
|---|---|---|
| `svg_dir` | Folder containing all glyph SVGs | `./svg` |
| `config_json` | JSON mapping icon names → PUA hex codes | `./my-font.json` |
| `font_name` | Short identifier, used for filenames | `my-font` |
| `family_name` | Display name shown in font menus | `My Font` |
| `out_dir` | Root folder for all output files | `./` |

The output directory will receive `fonts/`, `css/`, and `{font_name}.html` as subdirectories/files.

---

## Step 2: Verify SVG Naming Convention

Check that the SVG files follow PostScript-safe naming rules. SVG filenames cannot use raw special characters or capital letters (macOS filesystems are case-insensitive, which would silently overwrite lowercase glyphs).

**Required naming pattern: `{prefix}-{safe_name}.svg`**

| Character type | Rule | Example |
|---|---|---|
| Lowercase letter | `{prefix}-{char}.svg` | `my-a.svg` |
| **Uppercase letter** | `{prefix}-{char}_upper.svg` | `my-A_upper.svg` |
| Digit | `{prefix}-{char}.svg` | `my-0.svg` |
| Special symbol | `{prefix}-{english_name}.svg` | `my-question.svg` |
| Space | `{prefix}-space.svg` | `my-space.svg` |

**Symbol name reference:**
```
! exclam    @ at         # numbersign  $ dollar    % percent
^ asciicircum  & ampersand  * asterisk   ( parenleft  ) parenright
- hyphen    + plus       = equal       { braceleft  } braceright
[ bracketleft  ] bracketright  | bar    : colon    ; semicolon
" quotedbl  ' quotesingle   < less    > greater   , comma
. period    ? question   / slash    \ backslash  _ underscore
` grave     ~ asciitilde
```

If SVG files don't match this convention, point out which ones need renaming before proceeding.

---

## Step 3: Verify or Create the Config JSON

The config JSON maps each icon name to a unique PUA (Private Use Area) code point. Check if one already exists; if not, generate it.

**Format:**
```json
{
  "name": "my-font",
  "icons": {
    "my-a": "ea01",
    "my-b": "ea02",
    "my-A": "ea1b",
    "my-!": "ea3f"
  }
}
```

- Icon key format: `{font_name}-{char}` where `{char}` is the literal character (not the safe name)
- PUA codes: start at `ea01`, increment by 1 per glyph, no duplicates
- Every SVG that should appear in the font needs an entry

---

## Step 4: Install Dependencies

Check whether `fonttools` and `brotli` are available, then install if missing. Both are required — `fonttools` drives all font construction, and `brotli` is the compression engine for WOFF2.

```bash
pip install fonttools brotli
```

---

## Step 5: Build OTF + WOFF2

Run the build script with the gathered parameters:

```bash
_S2F_SCRIPTS="$HOME/.claude/skills/svg-to-font/scripts"
python "$_S2F_SCRIPTS/build_font.py" \
  --config   {config_json} \
  --svg-dir  {svg_dir} \
  --out-dir  {out_dir} \
  --font-name  {font_name} \
  --family-name "{family_name}"
```

The script will print `Baseline shift: X.XX` (the auto-detected vertical alignment correction), then report paths for OTF and WOFF2. If any SVGs are missing, it logs `[SKIP]` per glyph and continues.

---

## Step 6: Generate CSS

```bash
_S2F_SCRIPTS="$HOME/.claude/skills/svg-to-font/scripts"
python "$_S2F_SCRIPTS/gen_css.py" \
  --config   {config_json} \
  --out-dir  {out_dir} \
  --font-name  {font_name} \
  --family-name "{family_name}"
```

Outputs `{out_dir}/css/{font_name}.css` containing the `@font-face` declaration and a `::before` rule for every icon class.

---

## Step 7: Generate HTML Preview

```bash
_S2F_SCRIPTS="$HOME/.claude/skills/svg-to-font/scripts"
python "$_S2F_SCRIPTS/gen_html.py" \
  --config   {config_json} \
  --out-dir  {out_dir} \
  --font-name  {font_name} \
  --family-name "{family_name}"
```

Outputs `{out_dir}/{font_name}.html` — an interactive page with a live typing box (Standard Unicode input) and a glyph grid (PUA CSS icon classes).

---

## Step 8: Open and Verify

```bash
open {out_dir}/{font_name}.html
```

Ask the user to check:
- Do all glyphs render (nothing blank or filled solid black)?
- Is the baseline consistent across upper/lowercase?
- Do special characters display correctly?

---

## Known Pitfalls

These issues have been encountered in practice and are already handled by the scripts. Document them here so you can diagnose regressions.

| Symptom | Root cause | Fix applied in scripts |
|---|---|---|
| Characters render as solid black blocks | CFF requires CCW contour winding; SVG uses CW | `ReverseContourPen` wraps every CFF pen |
| macOS Font Book: "cannot verify" warning | Missing `OS/2.fsSelection` Regular bit | `fsSelection \|= (1 << 6)` |
| Uppercase SVG silently missing | macOS case-insensitive FS: `A.svg` == `a.svg` | Uppercase glyphs use `_upper.svg` suffix |
| Glyphs float above or below baseline | SVG origin ≠ typographic baseline | Auto-scan flat lowercase letters, compute `shift_y` |
| All glyphs same width (monospace effect) | Default 1000×1000 SVG canvas | BoundsPen measures actual width; adds side bearings |
| `~` or `<` break HTML output | Raw special chars in CSS/HTML content | CSS `content` uses hex escape `\ea5e`; HTML uses `&lt;` |
| All special-char glyphs render as comma | CSS selector splitting: `.wave-,::before` is parsed as `.wave-` **and** `::before` as separate selectors — the bare `::before` injects the comma glyph onto every element's `::before`, overriding all others | `gen_css.py` CSS-escapes all non-alphanumeric chars in class names via `re.sub(r'([^a-zA-Z0-9_-])', r'\\\1', name)`, producing e.g. `.wave-\,::before` |

---

## Output Structure

```
{out_dir}/
├── fonts/
│   ├── {font_name}.otf      # Desktop font (CFF cubic bezier)
│   └── {font_name}.woff2    # Web font (Brotli-compressed, ~50% smaller)
├── css/
│   └── {font_name}.css      # @font-face + icon ::before classes
└── {font_name}.html         # Interactive preview page
```
