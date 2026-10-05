"""Content for the work section.

The section is a timeline: five lanes of work running in parallel from 2023 to
now, with a playhead you drag through time. So everything here is dated, and
dates carry a ``precision`` because the CV is honest about what it knows --
some things are pinned to a month, most to a year, and a few are genuinely
approximate. The UI draws approximate spans dotted rather than pretending.

Skills are cross-linked: every slug in an entry's ``stack`` must exist in
``SKILL_GROUPS``, and every skill must be used by at least one entry, or its
chip would never light up. ``_validate()`` enforces both at import.
"""

from datetime import date

AXIS_START = 2023.0


def _t(year, month=1):
    """A year-and-month as a float, so the axis is simple arithmetic."""
    return year + (month - 1) / 12


def now_t():
    """Today on the same scale, so 'ongoing' never goes stale."""
    today = date.today()
    return _t(today.year, today.month)


def axis_end():
    """A little room past today, so 'now' isn't jammed against the edge."""
    return now_t() + 2 / 12


# ── Lanes ──
# Top to bottom. The order is the point: the eye runs down one vertical slice
# and finds several lanes busy at the same moment.
LANES = [
    ('building', 'building'),
    ('shipping', 'shipping'),
    ('making', 'making'),
    ('stage', 'stage'),
    ('community', 'community'),
]

# ── Stack vocabulary ──
# Grouped the way the CV groups it, with the extras the old portfolio listed
# separately (Firebase, OAuth2, GitHub Actions) folded in.
SKILL_GROUPS = [
    {
        'label': 'iOS & Apple',
        'skills': [
            ('swiftui', 'SwiftUI'),
            ('storekit', 'StoreKit 2'),
            ('avkit', 'AVKit'),
            ('accessorysetupkit', 'AccessorySetupKit'),
            ('cloudkit', 'CloudKit'),
            ('swiftdata', 'SwiftData'),
            ('nfc', 'NFC'),
            ('mqtt', 'MQTT'),
        ],
    },
    {
        'label': 'Backend',
        'skills': [
            ('python', 'Python'),
            ('flask', 'Flask'),
            ('postgresql', 'PostgreSQL'),
            ('redis', 'Redis'),
            ('elasticsearch', 'Elasticsearch'),
            ('firebase', 'Firebase'),
            ('oauth2', 'OAuth2'),
        ],
    },
    {
        'label': 'Infrastructure',
        'skills': [
            ('gke', 'GKE'),
            ('gcp', 'GCP'),
            ('cloudflare', 'Cloudflare'),
            ('terraform', 'Terraform'),
            ('docker', 'Docker'),
            ('github-actions', 'GitHub Actions'),
            ('proxmox', 'Proxmox'),
            ('unifi', 'UniFi'),
        ],
    },
    {
        'label': 'Tooling',
        'skills': [
            ('stripe', 'Stripe'),
            ('grafana', 'Grafana'),
            ('posthog', 'PostHog'),
            ('stream', 'Stream.io'),
            ('customerio', 'Customer.io'),
            ('intercom', 'Intercom'),
        ],
    },
    {
        'label': 'Hardware',
        'skills': [
            ('kicad', 'KiCad'),
            ('pcb', 'PCB design'),
            ('raspberry-pi', 'Raspberry Pi'),
            ('esp32', 'ESP32'),
            ('electronics', 'Electronics'),
        ],
    },
]

# ── Milestones ──
# Only beats the CV pins to an actual month. Three marks punctuate the axis;
# a dozen would be noise.
MILESTONES = [
    {'at': _t(2023, 3), 'label': 'KidsHustle begins'},
    {'at': _t(2026, 4), 'label': 'KidsHustle ships'},
    {'at': _t(2026, 8), 'label': 'Tech.eu feature'},
]

# ── Work ──
# `end: None` means still running. `precision` is one of:
#   'month'  -- the CV pins it to a month
#   'year'   -- the CV gives a year
#   'approx' -- no date on record; a best guess, drawn dotted
WORK = [
    {
        'slug': 'kidshustle',
        'title': 'KidsHustle',
        'role': 'Founder · Urban Mechanics Ltd',
        'period': 'Mar 2023 — now',
        'lane': 'building',
        'start': _t(2023, 3),
        'end': None,
        'precision': 'month',
        'summary': 'A regulated UK marketplace connecting 13–17 year-olds with '
                   'local paid work posted by parents. Architecture through to '
                   'App Store launch.',
        'bullets': [
            'Launched on the App Store in April 2026 after building the whole '
            'thing from architecture to release.',
            'Architected 15 Python microservices on GKE across GCP and '
            'Cloudflare, with Stripe Connect, Stripe Identity and '
            'Elasticsearch wired in.',
            'Handled all legal and compliance myself — ICO registration '
            '(ZC095698), Terms of Service, Privacy Policy, GDPR Compliance '
            'Policy and Security Policy.',
            'Built a 10-sheet financial model and pitch deck for pre-seed '
            'fundraising.',
            'Ran growth end to end: Google Ads and Meta targeting SW London '
            'parents, TikTok campaigns, and journalist outreach that landed '
            'coverage in Tech.eu.',
            'Designed and operate the creator referral programme at '
            'referrals.kidshustle.app.',
        ],
        'stack': [
            'python', 'flask', 'gke', 'gcp', 'cloudflare', 'terraform',
            'docker', 'postgresql', 'redis', 'elasticsearch', 'stripe',
            'oauth2', 'swiftui', 'posthog', 'grafana', 'stream', 'customerio',
            'intercom', 'github-actions',
        ],
        'links': [
            ('kidshustle.app', 'https://kidshustle.app'),
            ('read the Tech.eu piece',
             'https://tech.eu/2026/08/21/at-14-sasha-bagrov-is-building-a-safer-marketplace-for-teenage-odd-jobs/'),
        ],
    },
    {
        'slug': 'dsmprompt',
        'title': 'DSMPrompt',
        'role': 'App Store · solo',
        'period': '2025 — now',
        'lane': 'shipping',
        'start': _t(2025),
        'end': None,
        'precision': 'year',
        'summary': 'A SwiftUI iPad app for theatre Deputy Stage Managers — '
                   'script and cue management, fully offline, no data '
                   'collection.',
        'bullets': [
            'Cue management talking over MQTT to the Promptly Clicker, a '
            'custom ESP32 Bluetooth remote built with AccessorySetupKit.',
            'Spectator live-sync view, NFC card managers and a Liquid Glass '
            'UI.',
            'Published under Urban Mechanics Ltd at 99p; earned roughly £21 '
            'organically over 26 weeks with zero advertising.',
        ],
        'stack': [
            'swiftui', 'storekit', 'mqtt', 'nfc', 'accessorysetupkit', 'esp32',
        ],
        'links': [],
    },
    {
        'slug': 'anime-atlas',
        'title': 'Anime Atlas',
        'role': 'App Store · solo',
        'period': '2024',
        'lane': 'shipping',
        'start': _t(2024),
        'end': _t(2024, 12),
        'precision': 'year',
        'summary': 'A native iOS anime tracker with StoreKit 2 subscriptions, '
                   'published on the App Store.',
        'bullets': [],
        'stack': ['swiftui', 'storekit'],
        'links': [
            ('App Store',
             'https://apps.apple.com/gb/app/animeatlas/id6739979715'),
        ],
    },
    {
        'slug': 'pollify',
        'title': 'Pollify',
        'role': 'Web · open source',
        'period': '2024 — now',
        'lane': 'shipping',
        'start': _t(2024, 6),
        'end': None,
        'precision': 'approx',
        'summary': 'Privacy-focused, open-source poll creation — no accounts, '
                   'no tracking.',
        'bullets': [],
        'stack': ['python', 'flask', 'firebase'],
        'links': [('pollify.co.uk', 'https://pollify.co.uk')],
    },
    {
        'slug': 'afisha-scanner',
        'title': 'Afisha Ticket Scanner',
        'role': 'iOS + macOS',
        'period': '2024',
        'lane': 'shipping',
        'start': _t(2024, 3),
        'end': _t(2024, 10),
        'precision': 'approx',
        'summary': 'A ticket scanning system for live events, syncing across '
                   'iOS and macOS with CloudKit and SwiftData.',
        'bullets': [],
        'stack': ['swiftui', 'cloudkit', 'swiftdata'],
        'links': [
            ('afishalondontickets.com', 'https://www.afishalondontickets.com/'),
        ],
    },
    {
        'slug': 'kassa',
        'title': 'Kassa Notifications',
        'role': 'iOS',
        'period': '2024',
        'lane': 'shipping',
        'start': _t(2024, 6),
        'end': _t(2024, 12),
        'precision': 'approx',
        'summary': 'Real-time Stripe purchase alerts on iOS, for watching a '
                   'box office fill up live.',
        'bullets': [],
        'stack': ['swiftui', 'stripe', 'python'],
        'links': [
            ('afishalondontickets.com', 'https://www.afishalondontickets.com/'),
        ],
    },
    {
        'slug': 'seurt',
        'title': 'Seurt',
        'role': 'Web',
        'period': '2024',
        'lane': 'shipping',
        'start': _t(2024, 9),
        'end': _t(2025, 3),
        'precision': 'approx',
        'summary': 'Secure, token-based chat with a retro 8-bit aesthetic.',
        'bullets': [],
        'stack': ['python', 'flask'],
        'links': [('seurt.vercel.app', 'https://seurt.vercel.app/')],
    },
    {
        'slug': 'pcb-lamp',
        'title': 'Modular PCB Lamp',
        'role': 'School Design & Engineering project',
        'period': '2025',
        'lane': 'making',
        'start': _t(2025),
        'end': _t(2025, 12),
        'precision': 'year',
        'summary': 'A modular lamp built around a hand-designed PCB, '
                   'fabricated by JLCPCB and driven by a Raspberry Pi.',
        'bullets': [
            'Board designed from scratch in KiCad and sent to JLCPCB for '
            'fabrication.',
            'Raspberry Pi drives the modules over USB-PD for power and I2C '
            'for control.',
        ],
        'stack': ['kicad', 'pcb', 'raspberry-pi', 'electronics'],
        'links': [],
    },
    {
        'slug': 'homelab',
        'title': 'Homelab',
        'role': 'Self-hosted · ongoing',
        'period': 'ongoing',
        'lane': 'making',
        'start': _t(2024, 1),
        'end': None,
        'precision': 'approx',
        'summary': 'A three-node Proxmox cluster behind a UniFi network, '
                   'running everything I would rather not rent.',
        'bullets': [
            'Home Assistant and Music Assistant for the house, plus a Plex '
            'stack for media.',
            'SearXNG for search and Nginx Proxy Manager in front of it all.',
            'ESPSomfy-RTS driving the awning automation.',
        ],
        'stack': ['proxmox', 'unifi', 'docker'],
        'links': [],
    },
    {
        'slug': 'theatre-tech',
        'title': 'Theatre Tech',
        'role': 'Hampton School club',
        'period': '2023 — now',
        'lane': 'stage',
        'start': _t(2023, 9),
        'end': None,
        'precision': 'year',
        'summary': 'Daily help in the theatre and production management '
                   'outside school hours, plus weekly assembly video and '
                   'audio mixing.',
        'bullets': [
            'Deputy Stage Manager on productions including Treasure Island '
            'and The Hound of the Baskervilles.',
            'Lighting design, audio design, audio mixing, patching and video '
            'mixing across many productions and events.',
            'Set tech on Les Misérables at The Hammond Theatre.',
        ],
        'stack': [],
        'links': [],
    },
    {
        'slug': 'all-saints',
        'title': 'All Saints',
        'role': 'School History documentary',
        'period': '2026',
        'lane': 'stage',
        'start': _t(2026),
        'end': _t(2026, 7),
        'precision': 'year',
        'summary': 'A documentary on Black British civil rights after 1945 — '
                   'written, directed, filmed and edited solo.',
        'bullets': [],
        'stack': ['avkit'],
        'links': [],
    },
    {
        'slug': 'photography-club',
        'title': 'Photography Club',
        'role': 'Hampton School club · co-founder',
        'period': '2025 — now',
        'lane': 'community',
        'start': _t(2025, 9),
        'end': None,
        'precision': 'year',
        'summary': 'A weekly session a friend and I started and run, teaching '
                   'a different photography idea each week.',
        'bullets': [
            'Partnered with the school media team for equipment access.',
            'Occasionally takes on videography for school events.',
        ],
        'stack': [],
        'links': [],
    },
    {
        'slug': 'yfl',
        'title': 'Young Founders of London',
        'role': 'Member',
        'period': 'Sep 2026 — now',
        'lane': 'community',
        'start': _t(2026, 9),
        'end': None,
        'precision': 'month',
        'summary': "A curated community of London's most ambitious student "
                   'entrepreneurs.',
        'bullets': [],
        'stack': [],
        'links': [('yfl.lovable.app', 'https://yfl.lovable.app/')],
    },
    {
        'slug': 'perse',
        'title': 'Perse Coding Team Challenge',
        'role': 'Competition',
        'period': '2025',
        'lane': 'community',
        'start': _t(2025, 2),
        'end': _t(2025, 5),
        'precision': 'approx',
        'summary': 'Competed in Python in Round 1 and qualified for Round 2.',
        'bullets': [],
        'stack': ['python'],
        'links': [],
    },
]

LANGUAGES = [
    ('English', 'fluent'),
    ('Russian', 'fluent'),
    ('German', 'studying'),
]

EDUCATION = {'name': 'Hampton School', 'place': 'London', 'period': '2023 — now'}


def skill_names():
    """Slug -> display name, for the chips rendered inside each entry."""
    return {
        slug: name
        for group in SKILL_GROUPS
        for slug, name in group['skills']
    }


def skill_usage():
    """Slug -> how many work entries use it."""
    counts = {}
    for entry in WORK:
        for slug in entry['stack']:
            counts[slug] = counts.get(slug, 0) + 1
    return counts


def skill_projects():
    """Slug -> the work entries that use it.

    The stack panel lights a chip while any of its projects is running at the
    playhead, which is why this maps to projects rather than to a date. The CV
    records no per-skill adoption dates, so a tool is credited to the whole
    span of the work that used it -- the panel is labelled "in play" rather
    than "learned by" for exactly that reason.
    """
    used = {}
    for entry in WORK:
        for slug in entry['stack']:
            used.setdefault(slug, []).append(entry['slug'])
    return used


def lanes():
    """Lanes with their entries, in render order, skipping any empty lane."""
    out = []
    for slug, label in LANES:
        items = [e for e in WORK if e['lane'] == slug]
        if items:
            out.append({'slug': slug, 'label': label, 'entries': items})
    return out


def _validate():
    known = {slug for group in SKILL_GROUPS for slug, _ in group['skills']}
    lane_slugs = {slug for slug, _ in LANES}
    precisions = {'month', 'year', 'approx'}

    for entry in WORK:
        unknown = set(entry['stack']) - known
        if unknown:
            raise ValueError(
                f"work entry {entry['slug']!r} references unknown skills: "
                f'{sorted(unknown)}'
            )
        if entry['lane'] not in lane_slugs:
            raise ValueError(
                f"work entry {entry['slug']!r} has unknown lane "
                f"{entry['lane']!r}"
            )
        if entry['precision'] not in precisions:
            raise ValueError(
                f"work entry {entry['slug']!r} has unknown precision "
                f"{entry['precision']!r}"
            )
        if entry['start'] < AXIS_START:
            raise ValueError(
                f"work entry {entry['slug']!r} starts before the axis does"
            )
        if entry['end'] is not None and entry['end'] < entry['start']:
            raise ValueError(
                f"work entry {entry['slug']!r} ends before it starts"
            )

    orphans = known - {slug for entry in WORK for slug in entry['stack']}
    if orphans:
        raise ValueError(
            f'these skills are in no work entry, so their chips would never '
            f'light up: {sorted(orphans)}'
        )


_validate()


# Two milestone labels closer than this (as a percentage of the axis) would
# overlap, so the second one is lifted onto its own line.
_MILESTONE_GAP_PCT = 16

# Inside this much of either end, a centred label would overflow the figure.
_MILESTONE_EDGE_PCT = 14


def _stack_milestones(marks):
    """Work out how each milestone label has to be placed.

    ``stacked`` lifts a label onto a second line when it would collide with the
    one before it. ``anchor`` keeps labels near either end from being clipped:
    a centred label at 4% of the axis hangs off the left edge.
    """
    out = []
    last_flat = None
    for mark in sorted(marks, key=lambda m: m['left_pct']):
        stacked = last_flat is not None and \
            mark['left_pct'] - last_flat < _MILESTONE_GAP_PCT
        if mark['left_pct'] < _MILESTONE_EDGE_PCT:
            anchor = 'start'
        elif mark['left_pct'] > 100 - _MILESTONE_EDGE_PCT:
            anchor = 'end'
        else:
            anchor = 'mid'
        out.append({**mark, 'stacked': stacked, 'anchor': anchor})
        if not stacked:
            last_flat = mark['left_pct']
    return out


def timeline():
    """Everything the timeline needs, with positions precomputed as percentages.

    Geometry belongs here rather than in the template: the axis span depends on
    today's date, and doing the arithmetic in Jinja would scatter it across
    three files.
    """
    start, end = AXIS_START, axis_end()
    span = end - start
    now = now_t()

    def pct(t):
        return (t - start) / span * 100

    def positioned(entry):
        stop = entry['end'] if entry['end'] is not None else now
        return {
            **entry,
            'left_pct': round(pct(entry['start']), 4),
            'width_pct': round(max(pct(stop) - pct(entry['start']), 0.6), 4),
            'ongoing': entry['end'] is None,
        }

    return {
        'axis_start': start,
        'axis_end': end,
        'axis_span': span,
        'now': now,
        'now_pct': round(pct(now), 4),
        'years': [
            {'year': y, 'left_pct': round(pct(float(y)), 4)}
            for y in range(int(start), int(end) + 1)
            if start <= y <= end
        ],
        'milestones': _stack_milestones(
            [{**m, 'left_pct': round(pct(m['at']), 4)} for m in MILESTONES]
        ),
        'lanes': [
            {**lane, 'entries': [positioned(e) for e in lane['entries']]}
            for lane in lanes()
        ],
        'rows': sum(len(lane['entries']) for lane in lanes()),
    }


# ── The show ──
# The work section is called like a show: scrolling advances the playhead cue
# by cue, holding on each one. Every number in the prose below is checked
# against WORK by _validate_acts(), so the story can't drift from the data.
ACTS = [
    {
        'cue': 'standby',
        'at': _t(2023, 3),
        'when': 'march 2023',
        'lines': [
            'i start on a marketplace that will take three years before a '
            'single person can use it.',
            'nothing else is running.',
        ],
        'expect': {'running': 1},
    },
    {
        'cue': 'cue 1',
        'at': _t(2023, 9),
        'when': 'late 2023',
        'lines': [
            'a second strand opens — school theatre. lights, sound, calling '
            'cues from the book.',
            'it matters later.',
        ],
        'expect': {'running': 2},
    },
    {
        'cue': 'cue 2',
        'at': _t(2024, 6),
        'when': '2024',
        'lines': [
            'six more start inside twelve months. apps, a chat client, a '
            'cluster in the house.',
            'the marketplace is still half-built underneath all of it.',
        ],
        'expect': {'running': 7},
    },
    {
        'cue': 'cue 3',
        'at': _t(2025, 3),
        'when': 'march 2025',
        'lines': [
            'every lane lit at once. eight things running, thirty-one '
            'technologies in play,',
            'and a hand-designed PCB on the bench.',
        ],
        'expect': {'running': 8, 'in_play': 31, 'lanes': 5},
    },
    {
        'cue': 'cue 4 — go',
        'at': _t(2026, 4),
        'when': 'april 2026',
        'climax': True,
        'lines': [
            'fifteen microservices. ICO registration. payments, identity, '
            'and three years of nerve.',
            'KidsHustle goes live on the App Store.',
        ],
        'expect': {'running': 7},
    },
    {
        'cue': 'curtain',
        'at': None,  # resolved to "now" at render time
        'when': 'now',
        'lines': [
            'seven still running. tech.eu ran the story in august; i was '
            'fourteen.',
            'standby for the next one.',
        ],
        'expect': {'running': 7},
    },
]


def acts():
    """The cue sheet, with the closing cue resolved to today."""
    return [
        {**act, 'at': act['at'] if act['at'] is not None else now_t()}
        for act in ACTS
    ]


def _state_at(t):
    """What is running, and which stack is in play, at one moment."""
    running = [
        e for e in WORK
        if e['start'] <= t and (e['end'] is None or e['end'] >= t)
    ]
    in_play = set()
    for entry in running:
        in_play |= set(entry['stack'])
    return running, in_play


def _validate_acts():
    """Keep the prose honest: every number an act claims must hold."""
    for act in acts():
        running, in_play = _state_at(act['at'])
        actual = {
            'running': len(running),
            'in_play': len(in_play),
            'lanes': len({e['lane'] for e in running}),
        }
        for key, claimed in act.get('expect', {}).items():
            if actual[key] != claimed:
                raise ValueError(
                    f"act {act['cue']!r} ({act['when']}) claims {key}="
                    f'{claimed}, but the data says {actual[key]}'
                )


_validate_acts()
