#!/usr/bin/env python3
"""
build_font.py — Compile SVG glyphs into OTF + WOFF2 font files.

Usage:
    python build_font.py \
        --config   path/to/config.json \
        --svg-dir  path/to/svg/ \
        --out-dir  path/to/output/ \
        --font-name  my-font \
        --family-name "My Font" \
        [--version "Version 1.000"] \
        [--vendor-id MYFN] \
        [--side-bearing 45] \
        [--scale 4.0] \
        [--ascender 800] \
        [--descender -200]
"""
import os
import json
import string
import argparse

from fontTools.ttLib import TTFont
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from fontTools.svgLib.path import SVGPath
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen


# ── Symbol name mapping (char → PostScript-safe name) ────────────────────────
SPECIALS = {
    '!': 'exclam', '@': 'at', '#': 'numbersign', '$': 'dollar',
    '%': 'percent', '^': 'asciicircum', '&': 'ampersand', '*': 'asterisk',
    '(': 'parenleft', ')': 'parenright', '-': 'hyphen', '+': 'plus',
    '=': 'equal', '{': 'braceleft', '}': 'braceright', '[': 'bracketleft',
    ']': 'bracketright', '|': 'bar', ':': 'colon', ';': 'semicolon',
    '"': 'quotedbl', "'": 'quotesingle', '<': 'less', '>': 'greater',
    ',': 'comma', '.': 'period', '?': 'question', '/': 'slash',
    '\\': 'backslash', '_': 'underscore', '`': 'grave', '~': 'asciitilde',
    ' ': 'space',
}


def get_svg_filename(prefix, char):
    """Map a character to its SVG filename using safe naming conventions."""
    if char.isalpha() and char.isascii():
        return f"{prefix}-{char}_upper.svg" if char.isupper() else f"{prefix}-{char}.svg"
    if char.isdigit():
        return f"{prefix}-{char}.svg"
    name = SPECIALS.get(char)
    return f"{prefix}-{name}.svg" if name else None


def make_glyph_name(char, pua_code):
    """
    Return (glyph_name, unicode_codepoint).
    Alphanumeric chars map to their standard Unicode slot.
    Special chars map to their PostScript names (also standard Unicode).
    Unknown chars fall back to PUA slot only.
    """
    if len(char) == 1 and char.isalnum():
        return f"uni{ord(char):04X}", ord(char)
    if char in SPECIALS:
        if char == ' ':
            return 'space', ord(' ')
        return SPECIALS[char], ord(char)
    return f"uni{pua_code:04X}", None


def detect_baseline_shift(svg_dir, prefix, scale, em_size):
    """
    Auto-detect the vertical shift needed to align SVG glyphs to the
    typographic baseline. Scans flat lowercase letters (no descenders)
    and takes the average of their bottom bounds.

    Without this correction, glyphs float above or sit below the baseline
    depending on how the designer set up their SVG canvas.
    """
    base_y_sum, base_y_count = 0, 0
    scan_tf = Transform(scale, 0, 0, -scale, 0, em_size)

    for ch in string.ascii_lowercase:
        fp = os.path.join(svg_dir, get_svg_filename(prefix, ch) or '')
        if not os.path.exists(fp):
            continue
        rec = RecordingPen()
        SVGPath(fp).draw(rec)
        bpen = BoundsPen(None)
        rec.replay(TransformPen(bpen, scan_tf))
        if bpen.bounds:
            base_y_sum += bpen.bounds[1]
            base_y_count += 1

    return -(base_y_sum / base_y_count) if base_y_count else 0


def build(config_path, svg_dir, out_dir, font_name, family_name,
          version, vendor_id, side_bearing, scale, ascender, descender):

    with open(config_path) as f:
        icons = json.load(f)['icons']

    # The prefix is the part before the first '-' in any key, e.g. "my" from "my-a"
    first_key = next(iter(icons))
    prefix = first_key.split('-')[0]

    os.makedirs(os.path.join(out_dir, 'fonts'), exist_ok=True)

    em_size = 1000  # Standard UPM

    shift_y = detect_baseline_shift(svg_dir, prefix, scale, em_size)
    print(f"Baseline shift: {shift_y:.2f}")

    # Initialize with mandatory .notdef and space glyphs
    glyph_order = ['.notdef', 'space']
    cmap = {0x0020: 'space'}
    charstrings = {}
    metrics = {}

    empty_pen = T2CharStringPen(400, None)
    charstrings['.notdef'] = empty_pen.getCharString()
    charstrings['space'] = empty_pen.getCharString()
    metrics['.notdef'] = (400, 0)
    metrics['space'] = (300, 0)

    for key, pua_hex in icons.items():
        # key is like "my-a" or "my-A" — extract the actual character after the prefix
        char = key[len(prefix) + 1:]
        pua_code = int(pua_hex, 16)
        gname, std_code = make_glyph_name(char, pua_code)

        svg_fp = os.path.join(svg_dir, get_svg_filename(prefix, char) or '')
        if not os.path.exists(svg_fp):
            print(f"  [SKIP] Not found: {svg_fp}")
            continue

        if gname not in glyph_order:
            glyph_order.append(gname)

        # Register both PUA and standard Unicode codepoints so the font works
        # both as an icon font (via CSS ::before content) and as a normal typeface.
        cmap[pua_code] = gname
        if std_code and std_code != 0x0020:
            cmap[std_code] = gname

        # Load SVG path data
        raw = RecordingPen()
        SVGPath(svg_fp).draw(raw)

        # Apply scale + Y-flip (SVG Y grows down, font Y grows up) + baseline shift
        init_tf = Transform(scale, 0, 0, -scale, 0, em_size + shift_y)
        tmp = RecordingPen()
        raw.replay(TransformPen(tmp, init_tf))

        # Measure actual glyph bounds after transformation
        bpen = BoundsPen(None)
        tmp.replay(bpen)
        b = bpen.bounds

        if b:
            # Shift glyph so its left edge lands at side_bearing
            dx = side_bearing - b[0]
            final_tf = Transform(1, 0, 0, 1, dx, 0).transform(init_tf)
            final_rec = RecordingPen()
            raw.replay(TransformPen(final_rec, final_tf))
            adv_w = int(round((b[2] - b[0]) + side_bearing * 2))
            lsb = side_bearing
        else:
            final_rec, adv_w, lsb = tmp, 400, 0

        metrics[gname] = (adv_w, lsb)

        # CFF requires counter-clockwise contour winding; SVG uses clockwise.
        # ReverseContourPen fixes this — without it, fills render as solid black.
        cff_pen = T2CharStringPen(adv_w, None)
        final_rec.replay(ReverseContourPen(cff_pen))
        charstrings[gname] = cff_pen.getCharString()

    # Assemble the font
    fb = FontBuilder(em_size, isTTF=False)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupCFF(
        psName=f"{font_name}-Regular",
        fontInfo={"FullName": f"{family_name} Regular", "FamilyName": family_name},
        charStringsDict=charstrings,
        privateDict={},
    )
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ascender, descent=descender, lineGap=0)
    fb.setupNameTable({
        "familyName": family_name,
        "styleName": "Regular",
        "psName": f"{font_name}-Regular",
        "version": version,
        "uniqueFontIdentifier": f"1.000;{vendor_id};{font_name}-Regular",
        "fullName": f"{family_name} Regular",
    })
    fb.setupOS2(
        sTypoAscender=ascender, sTypoDescender=descender, sTypoLineGap=0,
        usWinAscent=ascender, usWinDescent=abs(descender),
        sxHeight=450, sCapHeight=700,
        fsType=0, achVendID=vendor_id,
    )
    # Set the Regular bit — without this, macOS Font Book shows a validation warning
    fb.font['OS/2'].fsSelection |= (1 << 6)
    fb.font['head'].macStyle = 0
    fb.setupPost()

    otf_path = os.path.join(out_dir, 'fonts', f"{font_name}.otf")
    woff2_path = os.path.join(out_dir, 'fonts', f"{font_name}.woff2")

    fb.font.save(otf_path)
    print(f"OTF   → {otf_path}")

    # Convert OTF → WOFF2 (Brotli-compressed; typically ~50% smaller)
    font = TTFont(otf_path)
    font.flavor = 'woff2'
    font.save(woff2_path)
    font.close()
    print(f"WOFF2 → {woff2_path}")


def main():
    p = argparse.ArgumentParser(description="Build OTF + WOFF2 from SVG glyphs")
    p.add_argument('--config',       required=True, help='Path to icons config JSON')
    p.add_argument('--svg-dir',      required=True, help='Directory containing SVG files')
    p.add_argument('--out-dir',      required=True, help='Output root directory')
    p.add_argument('--font-name',    required=True, help='Font identifier (used in filenames)')
    p.add_argument('--family-name',  required=True, help='Display family name (shown in font menus)')
    p.add_argument('--version',      default='Version 1.000')
    p.add_argument('--vendor-id',    default='UNKN', help='4-char vendor ID for OS/2 table')
    p.add_argument('--side-bearing', type=int,   default=45,   help='Left/right side bearing in font units')
    p.add_argument('--scale',        type=float, default=4.0,  help='SVG-to-font coordinate scale factor')
    p.add_argument('--ascender',     type=int,   default=800)
    p.add_argument('--descender',    type=int,   default=-200)
    args = p.parse_args()

    build(
        config_path=args.config,
        svg_dir=args.svg_dir,
        out_dir=args.out_dir,
        font_name=args.font_name,
        family_name=args.family_name,
        version=args.version,
        vendor_id=args.vendor_id,
        side_bearing=args.side_bearing,
        scale=args.scale,
        ascender=args.ascender,
        descender=args.descender,
    )


if __name__ == '__main__':
    main()
