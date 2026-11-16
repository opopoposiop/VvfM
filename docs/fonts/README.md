# Website fonts

The site retains locally installed Apple system and Hiragino fonts on macOS/iOS.
For other platforms it serves Inter and Noto Sans JP from this directory.
These are visual alternatives, not copies of San Francisco or Hiragino.
No Apple font files are redistributed.

- Inter variable font: https://github.com/google/fonts/tree/main/ofl/inter
- Noto Sans JP variable font: https://github.com/google/fonts/tree/main/ofl/notosansjp
- Both use SIL Open Font License 1.1; full license notices are included here.
- The original variable TTFs were losslessly re-encoded to WOFF2 with fontTools.
- Full glyph coverage is retained so future page text needs no subset regeneration.
- Fonts are served from this site, not Google Fonts, with font-display: swap.
- Safari can use local fonts immediately and does not need these fallback downloads.
