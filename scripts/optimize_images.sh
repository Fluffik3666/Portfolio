#!/usr/bin/env bash
#
# Generate the responsive AVIF/WebP/JPEG derivatives the hero and about photos
# are served from.
#
# The source JPEGs are full-resolution camera files (20MP, ~3MB each) but they
# render into a half-width column, so the browser was downloading roughly 20x
# the pixels it could ever show. The derivatives land in
# src/static/images/derived/ and are committed, so Vercel needs no build step
# and no image tooling at deploy time.
#
# Re-run after replacing a source photo:  ./scripts/optimize_images.sh
#
# Requires: sips (macOS), cwebp, avifenc  (brew install webp libavif)

set -euo pipefail

cd "$(dirname "$0")/.."

SRC_DIR="src/static/images"
OUT_DIR="$SRC_DIR/derived"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

for tool in sips cwebp avifenc; do
    command -v "$tool" >/dev/null || { echo "missing required tool: $tool" >&2; exit 1; }
done

mkdir -p "$OUT_DIR"

# "<source basename>:<width> <width> ..." — widths are CSS-pixel widths at 1x
# and 2x for the column each photo renders into.
IMAGES=(
    "sb_photos_bw-2:600 900 1400"
    "sb_photos_bw:900 1400 2000"
)

MANIFEST="src/image_manifest.json"
: > "$TMP/manifest-entries"

for entry in "${IMAGES[@]}"; do
    name="${entry%%:*}"
    widths="${entry#*:}"
    src="$SRC_DIR/$name.jpg"

    [[ -f "$src" ]] || { echo "missing source: $src" >&2; exit 1; }
    echo "==> $name.jpg"

    for w in $widths; do
        # sips resamples from the source each time; encoding from a clean
        # intermediate PNG keeps the AVIF/WebP encoders from inheriting the
        # source JPEG's compression artifacts.
        png="$TMP/$name-$w.png"
        sips --resampleWidth "$w" --setProperty format png "$src" --out "$png" >/dev/null

        avifenc --min 0 --max 40 --speed 4 --yuv 420 \
            "$png" "$OUT_DIR/$name-$w.avif" >/dev/null
        cwebp -q 80 -m 6 -quiet "$png" -o "$OUT_DIR/$name-$w.webp"
        # JPEG fallback for browsers without AVIF or WebP.
        sips --setProperty format jpeg --setProperty formatOptions 72 \
            "$png" --out "$OUT_DIR/$name-$w.jpg" >/dev/null

        # Record a content hash per derivative. The app reads these from the
        # manifest instead of hashing image bytes at request time, so the
        # serverless bundle no longer has to ship the images at all.
        for ext in avif webp jpg; do
            f="$OUT_DIR/$name-$w.$ext"
            hash="$(shasum -a 256 "$f" | cut -c1-12)"
            printf '  "%s-%s.%s": "%s",\n' "$name" "$w" "$ext" "$hash" \
                >> "$TMP/manifest-entries"
        done

        printf '    %5sw  avif %6s  webp %6s  jpg %6s\n' "$w" \
            "$(du -h "$OUT_DIR/$name-$w.avif" | cut -f1)" \
            "$(du -h "$OUT_DIR/$name-$w.webp" | cut -f1)" \
            "$(du -h "$OUT_DIR/$name-$w.jpg"  | cut -f1)"
    done
done

# Hash the non-derived static assets the templates still reference directly,
# so they keep their ?v= cache busting once images leave the bundle.
for f in "$SRC_DIR"/press/*.svg "$SRC_DIR"/press/*.png; do
    [[ -f "$f" ]] || continue
    hash="$(shasum -a 256 "$f" | cut -c1-12)"
    printf '  "press/%s": "%s",\n' "$(basename "$f")" "$hash" \
        >> "$TMP/manifest-entries"
done

{
    echo "{"
    # Trailing comma on the last entry would be invalid JSON.
    sed '$ s/,$//' "$TMP/manifest-entries"
    echo "}"
} > "$MANIFEST"

python3 -c "import json,sys; json.load(open('$MANIFEST'))" \
    || { echo "generated manifest is not valid JSON" >&2; exit 1; }

echo
echo "derived total: $(du -sh "$OUT_DIR" | cut -f1)"
echo "manifest: $MANIFEST ($(python3 -c "import json;print(len(json.load(open('$MANIFEST'))))") entries)"
