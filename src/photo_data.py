"""Captions for the photography gallery.

The storage bucket only knows a camera filename -- IMG_8350 -- which makes a
useless alt attribute and tells an image search nothing about the picture.
Captions live here instead, keyed by the id the gallery serves each photo
under, so a frame is described once and the page, the sitemap and the
structured data all say the same thing about it.

Add one whenever you know what a frame is:

    CAPTIONS = {
        4: 'Barbican walkway in low winter sun',
    }

A photo without a caption falls back to a plain description that is at least
true, rather than to its filename. The fallback is the same on every photo,
though, so captions are what actually earns these pictures a place in image
search -- they are the one thing here that can't be generated.
"""

# Said of the whole body of work, so it holds for any frame in it.
FALLBACK_ALT = 'Black-and-white street photography by Sasha Bagrov, shot around London'

CAPTIONS = {}


def caption(image_id):
    """What this photo is of, or None if nobody has said yet."""
    return CAPTIONS.get(image_id)


def alt_text(image_id):
    """Always something describing the picture -- never a camera filename."""
    return CAPTIONS.get(image_id) or FALLBACK_ALT
