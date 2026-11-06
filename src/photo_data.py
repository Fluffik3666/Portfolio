"""Captions for the photography gallery.

The storage bucket only knows a camera filename -- IMG_8350 -- which makes a
useless alt attribute and tells an image search nothing about the picture.
Captions live here instead, keyed by the id the gallery serves each photo
under, so a frame is described once and the page, the sitemap and the
structured data all say the same thing about it.

A caption is what the photograph is of, in a few words, the way you would
describe it to someone who can't see it. Place names earn their keep: they
are what somebody types into an image search.

These were drafted from the photographs themselves and are meant to be
corrected -- nobody but the photographer knows where a frame was actually
taken. Edit freely; a caption is the one thing here that can't be generated.
"""

# Only reached by a photo with no caption, so it stays deliberately plain
# rather than claiming a place or a treatment the picture may not have.
FALLBACK_ALT = 'Photograph by Sasha Bagrov'

CAPTIONS = {
    # ── Prague ──
    1: 'Golden hour on the baroque facades of Old Town Square, Prague',
    2: 'The spires of the Týn Church over the square at dusk, Prague',
    3: 'The Old Town Hall tower catching the last of the light, Prague',
    4: 'Sunlit gables above Old Town Square, Prague',
    15: 'A baroque altar seen through the ironwork of a church gate, Prague',
    16: 'The Fat Cat sign hanging over a side street at night, Prague',

    # ── Germany and the Alps ──
    7: 'The Holstentor at sunset, Lübeck',
    12: 'Badminton on the grass beside an alpine lake',
    23: 'A mown meadow path between chalets and pine forest',

    # ── New York ──
    9: 'A Cold War fallout shelter sign still bolted to a brick wall, New York',
    10: 'The Manhattan Bridge from the East River, Brooklyn behind it',
    11: 'The top of the Empire State Building lost in cloud, New York',

    # ── Mariánské Lázně ──
    29: 'The spa houses of Mariánské Lázně under heavy cloud',
    31: 'An afternoon on the benches of the spa promenade, Mariánské Lázně',
    32: 'A gilded spring pavilion against a hard blue sky, Mariánské Lázně',
    34: 'The pastel spa houses of Mariánské Lázně seen from the hillside',
    35: 'The cast-iron colonnade and its pavilion in late sun, Mariánské Lázně',
    36: 'Benches in the shade of the spa promenade, Mariánské Lázně',

    # ── Forest and water ──
    5: 'A winter stream running over iced rock, shot long exposure',
    6: 'A waxing gibbous moon in a black sky',
    24: 'A forest lake framed by overhanging leaves',
    25: 'Looking up into a stand of tall spruce',
    26: 'Reeds along the edge of a forest lake under building cloud',
    27: 'Late light in the canopy of a mixed forest',
    28: 'A forestry road sign at the edge of the Czech woods',
    30: 'A boardwalk running into dark spruce forest',
    33: 'A boardwalk through sunlit pines',
    37: 'A still lake under breaking cloud, seen through the trees',
    38: 'A lake framed by spruce branches',
    39: 'Reed beds and young spruce along a lake shore',

    # ── Aviation ──
    8: 'A Virgin Atlantic wingtip above the clouds at sunset',
    17: 'A British Airways A320 climbing out past the control tower, Heathrow',
    18: 'A British Airways A320 on short final, gear down',

    # ── England ──
    13: 'Ivy swallowing the front of an old stone building',
    14: 'Commuters at the ticket barriers, station concourse behind',
    21: 'The domes of the Royal Pavilion over the gardens, Brighton',

    # ── After dark ──
    40: 'Two figures on an empty street late at night',
    41: 'A lit shop window pulled into streaks by a long exposure',
    42: 'A single lit sign on a dark street corner',
    43: 'A neon shop sign smeared into blue by camera movement',
    44: 'A floodlit tower alone in the dark',
    45: 'A floodlit tower above the treeline at night',

    # ── Notting Hill ──
    46: 'Tourists photographing the painted houses on Farmer Street, Notting Hill',
    47: 'A "Trick or Treat" neon in a Notting Hill window at Halloween',
    48: 'A man checking his phone outside Los Mochis, Notting Hill',
    49: 'The pastel terrace on Farmer Street, Notting Hill',
    50: "Farmer Street's painted houses under a building crane, Notting Hill",
    51: 'A pasted-up mural beside a sunlit Portobello pavement',
    52: 'A woman stepping out of a mews archway, Notting Hill',
    53: 'Waiting on her phone in a shop doorway, Notting Hill',
    54: 'A man on his phone against a cobalt mews wall, Notting Hill',
    55: 'Against the blue wall of a private mews, Notting Hill',
}


def caption(image_id):
    """What this photo is of, or None if nobody has said yet."""
    return CAPTIONS.get(image_id)


def alt_text(image_id):
    """Always something describing the picture -- never a camera filename."""
    return CAPTIONS.get(image_id) or FALLBACK_ALT
