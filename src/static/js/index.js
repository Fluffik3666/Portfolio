// ── Portfolio ──
(function () {
    const sections = document.querySelectorAll('.section');
    const backNav = document.getElementById('back-nav');
    const navLinks = document.querySelectorAll('.nav-link');
    let currentSection = 'hero';

    // Honoured by the work section's interactions; the CSS media query covers
    // the transitions.
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'];

    // ── Language colors for GitHub ──
    const langColors = {
        JavaScript: '#f1e05a', Python: '#3572A5', Swift: '#F05138',
        HTML: '#e34c26', CSS: '#563d7c', TypeScript: '#3178c6',
        Shell: '#89e051', Go: '#00ADD8', Rust: '#dea584',
        Java: '#b07219', Ruby: '#701516', Kotlin: '#A97BFF',
        Dart: '#00B4AB', 'C++': '#f34b7d', C: '#555555',
        'Jupyter Notebook': '#DA5B0B', Dockerfile: '#384d54'
    };

    // ── Section navigation ──
    function showSection(id) {
        if (currentSection === id || falling) return;

        const outgoing = document.getElementById(currentSection);
        const incoming = document.getElementById(id);

        // Fade out current
        gsap.to(outgoing, {
            opacity: 0,
            duration: 0.4,
            ease: 'power2.in',
            onComplete() {
                outgoing.classList.remove('active');
                outgoing.style.opacity = '';
                arrive(id);
            }
        });
    }

    function arrive(id) {
        window.scrollTo(0, 0);
        document.getElementById(id).classList.add('active');
        currentSection = id;
        animateSection(id);

        // Toggle back nav
        if (id === 'hero') {
            backNav.classList.remove('visible');
        } else {
            backNav.classList.add('visible');
        }
    }

    // ── Animate each section on entry ──
    function animateSection(id) {
        const section = document.getElementById(id);

        switch (id) {
            case 'hero':
                animateHero();
                break;
            case 'about':
                animateAbout();
                break;
            case 'work':
                animateWork();
                break;
            case 'photography':
                fetchPhotos();
                if (gallery) gallery.enter();
                animatePhotography();
                break;
        }
    }

    // ── HERO animations ──
    function animateHero() {
        const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

        tl.fromTo('.hero-photo img',
            { opacity: 0, x: -40 },
            { opacity: 1, x: 0, duration: 1.2 }
        )
        .fromTo('.hero-greeting .line',
            { opacity: 0, y: 30 },
            { opacity: 1, y: 0, duration: 0.8, stagger: 0.15 },
            '-=0.7'
        )
        .fromTo('.nav-link',
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.6, stagger: 0.1 },
            '-=0.4'
        )
        .fromTo('.nav-book',
            { opacity: 0, y: 15 },
            { opacity: 1, y: 0, duration: 0.5 },
            '-=0.25'
        )
        .fromTo('.hero-press',
            { opacity: 0, y: 15 },
            { opacity: 1, y: 0, duration: 0.5, stagger: 0.1 },
            '-=0.2'
        );
    }

    // ── ABOUT animations ──
    function animateAbout() {
        const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

        tl.fromTo('.about-photo img',
            { opacity: 0, scale: 1.05 },
            { opacity: 1, scale: 1, duration: 1.2 }
        )
        .fromTo('.about-heading',
            { opacity: 0, y: 30 },
            { opacity: 1, y: 0, duration: 0.8 },
            '-=0.8'
        )
        .fromTo('.about-text p',
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.6, stagger: 0.12 },
            '-=0.4'
        )
        .fromTo('#about .featured-in',
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.5, stagger: 0.12 },
            '-=0.2'
        )
        .fromTo('.about-links',
            { opacity: 0, y: 15 },
            { opacity: 1, y: 0, duration: 0.5 },
            '-=0.2'
        );
    }

    // ── WORK animations ──
    // The section's opening lines animate in on arrival, the same as every
    // other section. Everything below the show is simply present -- the show
    // is the performance; the rest is a set you walk around.
    function animateWork() {
        if (reduceMotion) {
            remeasureTimeline();
            return;
        }

        gsap.timeline({ defaults: { ease: 'power3.out' } })
            .fromTo('.section--work .section-heading',
                { opacity: 0, y: 30 },
                { opacity: 1, y: 0, duration: 0.8 })
            .fromTo('.work-intro',
                { opacity: 0, y: 20 },
                { opacity: 1, y: 0, duration: 0.6 },
                '-=0.5');

        // The section was display:none while these were set up, so every
        // measurement taken then is stale until now.
        remeasureTimeline();
        refreshShow();
        replayShow();
    }

    // ── WORK: the show ──
    // Scroll drives the playhead, but not at a constant crawl. Each cue gets a
    // band of scroll: the playhead travels for the first part of the band and
    // then holds while you read. Move, hold, move, hold -- the rhythm a show is
    // actually called in.
    const CUE_TRAVEL = 0.45;

    let refreshShow = () => {};
    let replayShow = () => {};
    let remeasureTimeline = () => {};

    function initShow() {
        const show = document.getElementById('show');
        const stage = document.getElementById('stage');
        if (!show || !stage) return;

        const tl = document.getElementById('tl');
        const axisStart = parseFloat(tl.dataset.axisStart);
        const axisSpan = parseFloat(tl.dataset.axisSpan);
        const nowT = parseFloat(tl.dataset.now);

        const acts = Array.from(document.querySelectorAll('.act')).map(el => ({
            el,
            at: parseFloat(el.dataset.at),
            climax: el.classList.contains('act--climax'),
        }));
        if (!acts.length) return;

        const cueMarks = Array.from(document.querySelectorAll('.show-cue'));
        const rows = Array.from(stage.querySelectorAll('.stage-row')).map(el => ({
            el,
            start: parseFloat(el.dataset.start),
            end: el.dataset.end === '' ? null : parseFloat(el.dataset.end),
            fill: el.querySelector('.stage-bar-fill'),
            lane: el.closest('.stage-lane'),
            slug: el.dataset.slug,
        }));
        const lanes = Array.from(stage.querySelectorAll('.stage-lane'));
        const playhead = document.getElementById('stage-playhead');
        const whenEl = document.getElementById('show-when');
        const runningEl = document.getElementById('show-running');
        const playEl = document.getElementById('show-play');

        // Skills are credited to the span of the work that used them, so the
        // "in play" figure counts the stacks of whatever is running.
        const stacks = {};
        document.querySelectorAll('.chip[data-projects]').forEach(chip => {
            chip.dataset.projects.split(' ').filter(Boolean).forEach(slug => {
                (stacks[slug] = stacks[slug] || []).push(chip.dataset.skill);
            });
        });

        const easeInOut = k => (k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2);

        // ── scroll progress -> a moment in time, plus which cue is live ──
        function cueAt(progress) {
            const band = 1 / acts.length;
            const i = Math.min(acts.length - 1, Math.floor(progress / band));
            const local = Math.min((progress - i * band) / band, 1);
            const from = i === 0 ? axisStart : acts[i - 1].at;
            const travel = easeInOut(Math.min(local / CUE_TRAVEL, 1));
            return {
                index: i,
                local,
                landed: local >= CUE_TRAVEL,
                t: from + (acts[i].at - from) * travel,
            };
        }

        function paintStage(t) {
            playhead.style.left = `${((t - axisStart) / axisSpan) * 100}%`;

            let running = 0;
            const liveLanes = new Set();
            const inPlay = new Set();

            rows.forEach(row => {
                const stop = row.end === null ? nowT : row.end;
                const begun = t >= row.start;
                const drawn = begun
                    ? Math.min((t - row.start) / Math.max(stop - row.start, 1e-6), 1)
                    : 0;
                row.fill.style.setProperty('--draw', drawn.toFixed(4));

                const live = begun && t <= stop;
                row.el.classList.toggle('is-live', live);
                row.el.classList.toggle('is-past', begun && t > stop);
                if (live) {
                    running++;
                    liveLanes.add(row.lane);
                    (stacks[row.slug] || []).forEach(s => inPlay.add(s));
                }
            });

            lanes.forEach(l => l.classList.toggle('is-live', liveLanes.has(l)));

            const year = Math.floor(t + 1e-9);
            const month = Math.min(11, Math.max(0, Math.round((t - year) * 12)));
            whenEl.textContent = t >= nowT - 1e-6
                ? 'now'
                : `${MONTHS[month].toLowerCase()} ${year}`;
            runningEl.textContent = running;
            playEl.textContent = inPlay.size;
        }

        // ── GO ──
        // The climax lands once per pass. Flashing on every scroll tick would
        // make it a strobe rather than a moment.
        let fired = -1;
        function callCue(cue) {
            // A cue's words appear when the playhead lands on its moment, not
            // when it sets off towards it -- otherwise you read "eight running"
            // while the counter is still climbing through four.
            const spoken = cue.landed ? cue.index : Math.max(cue.index - 1, 0);
            acts.forEach((act, i) => act.el.classList.toggle('is-live', i === spoken));
            cueMarks.forEach((m, i) => m.classList.toggle('is-live', i === spoken));

            const isGo = acts[cue.index].climax && cue.landed;
            if (isGo && fired !== cue.index) {
                fired = cue.index;
                stage.classList.add('is-go');
                gsap.delayedCall(0.45, () => stage.classList.remove('is-go'));
            } else if (!isGo && fired === cue.index) {
                fired = -1;
            }
        }

        function render(progress) {
            const cue = cueAt(Math.min(Math.max(progress, 0), 1));
            paintStage(cue.t);
            callCue(cue);
        }

        if (reduceMotion || typeof ScrollTrigger === 'undefined') {
            // No sticky stage and no scrubbing: show every cue as prose with
            // the score drawn at today.
            acts.forEach(a => a.el.classList.add('is-live'));
            paintStage(nowT);
            return;
        }

        const trigger = ScrollTrigger.create({
            trigger: show,
            start: 'top top',
            end: 'bottom bottom',
            scrub: true,
            onUpdate: self => render(self.progress),
        });

        // The section is display:none until it is navigated to, so every
        // measurement ScrollTrigger took at load is wrong until then.
        refreshShow = () => { ScrollTrigger.refresh(); };
        replayShow = () => { fired = -1; render(trigger.progress || 0); };

        render(0);
    }

    // ── WORK: the timeline ──
    function initWork() {
        const root = document.getElementById('tl');
        if (!root) return;

        const axisStart = parseFloat(root.dataset.axisStart);
        const axisSpan = parseFloat(root.dataset.axisSpan);
        const nowT = parseFloat(root.dataset.now);

        const range = document.getElementById('tl-range');
        const playhead = document.getElementById('tl-playhead');
        const dateEl = document.getElementById('tl-date');
        const countEl = document.getElementById('tl-count');
        const stackLiveEl = document.getElementById('stack-live');
        const stackWhenEl = document.getElementById('stack-when');

        const rows = Array.from(root.querySelectorAll('.tl-row')).map(el => ({
            el,
            slug: el.dataset.slug,
            start: parseFloat(el.dataset.start),
            // Ongoing work has no end date; it runs to wherever "now" is.
            end: el.dataset.end === '' ? null : parseFloat(el.dataset.end),
            fill: el.querySelector('.tl-bar-fill'),
            bar: el.querySelector('.tl-bar'),
        }));
        // A chip is lit while any project using it is running at the playhead.
        // The CV has no per-skill adoption dates, so a tool is credited to the
        // span of the work that used it -- hence "in play", not "learned by".
        const chips = Array.from(document.querySelectorAll('.chip[data-projects]'))
            .map(el => ({ el, projects: el.dataset.projects.split(' ').filter(Boolean) }));
        const details = Array.from(document.querySelectorAll('.detail'));

        const RANGE_MAX = Number(range.max);
        const scrubSpan = nowT - axisStart;
        const toTime = v => axisStart + (v / RANGE_MAX) * scrubSpan;
        const toValue = t => Math.round(((t - axisStart) / scrubSpan) * RANGE_MAX);

        // ── Paint one moment in time ──
        function paint(t) {
            const pct = ((t - axisStart) / axisSpan) * 100;
            playhead.style.left =
                `calc(var(--name-col) + var(--gutter) + ${pct}% * var(--track-ratio, 1))`;

            let running = 0;
            const liveProjects = new Set();
            rows.forEach(row => {
                const stop = row.end === null ? nowT : row.end;
                const begun = t >= row.start;
                // How much of this span the playhead has passed: the bar draws
                // itself in behind the line rather than being there already.
                const drawn = begun
                    ? Math.min((t - row.start) / Math.max(stop - row.start, 1e-6), 1)
                    : 0;
                row.fill.style.setProperty('--draw', drawn.toFixed(4));
                if (row.bar) row.bar.style.setProperty('--tip', drawn >= 1 ? '1' : '0');

                const active = begun && t <= stop;
                row.el.classList.toggle('is-future', !begun);
                row.el.classList.toggle('is-past', begun && t > stop);
                if (active) {
                    running++;
                    liveProjects.add(row.slug);
                }
            });

            let lit = 0;
            chips.forEach(chip => {
                const on = chip.projects.some(slug => liveProjects.has(slug));
                chip.el.classList.toggle('is-live', on);
                if (on) lit++;
            });

            const year = Math.floor(t + 1e-9);
            const month = Math.min(11, Math.max(0, Math.round((t - year) * 12)));
            const atNow = t >= nowT - 1e-6;
            dateEl.textContent = atNow ? 'now' : `${MONTHS[month]} ${year}`;
            countEl.textContent = running;
            stackLiveEl.textContent = lit;
            stackWhenEl.textContent = atNow
                ? 'now'
                : `in ${MONTHS[month].slice(0, 3).toLowerCase()} ${year}`;
        }

        // The track is narrower than the figure, so a percentage of the track
        // is not a percentage of the row. Measure the ratio and let CSS do the
        // rest, so the playhead stays aligned through resizes.
        function measure() {
            const track = root.querySelector('.tl-track');
            const body = root.querySelector('.tl-body');
            if (!track || !body) return;
            root.style.setProperty(
                '--track-ratio',
                (track.offsetWidth / body.offsetWidth).toFixed(5)
            );
        }

        // ── Selection ──
        function select(slug) {
            details.forEach(d => {
                const on = d.dataset.detail === slug;
                d.hidden = !on;
                d.classList.toggle('is-active', on);
            });
            rows.forEach(r => r.el.classList.toggle('is-selected', r.slug === slug));

            const active = details.find(d => d.dataset.detail === slug);
            if (active && !reduceMotion) {
                gsap.fromTo(active,
                    { opacity: 0, y: 12 },
                    { opacity: 1, y: 0, duration: 0.45, ease: 'power2.out', overwrite: true }
                );
            }
        }

        root.addEventListener('click', e => {
            const trigger = e.target.closest('[data-select]');
            if (trigger) {
                select(trigger.dataset.select);
                return;
            }
            // Clicking a lane heading pushes the other lanes back, so you can
            // follow one strand without losing sight of the rest.
            const laneLabel = e.target.closest('.tl-lane-label');
            if (laneLabel) {
                const lane = laneLabel.parentElement;
                const alreadyOnly = !lane.classList.contains('is-muted') &&
                    root.querySelectorAll('.tl-lane.is-muted').length ===
                    root.querySelectorAll('.tl-lane').length - 1;
                root.querySelectorAll('.tl-lane').forEach(l => {
                    l.classList.toggle('is-muted', !alreadyOnly && l !== lane);
                });
            }
        });

        // ── Scrubbing ──
        range.addEventListener('input', () => {
            paint(toTime(Number(range.value)));
        });

        window.addEventListener('resize', () => {
            measure();
            paint(toTime(Number(range.value)));
        });

        // A milestone label is centred on its tick by default, but at narrow
        // widths a centred label runs off the figure or across a neighbouring
        // tick. The server picks a sensible default from the date alone; this
        // corrects it against the width the label actually renders at.
        function anchorMilestones() {
            const head = root.querySelector('.tl-milestones');
            if (!head) return;
            const headW = head.offsetWidth;
            if (!headW) return;

            root.querySelectorAll('.tl-ms').forEach(ms => {
                const label = ms.querySelector('.tl-ms-label');
                if (!label) return;
                const x = ms.offsetLeft;
                const w = label.offsetWidth;
                let anchor = 'mid';
                if (x - w / 2 < 0) anchor = 'start';
                else if (x + w / 2 > headW) anchor = 'end';
                ms.classList.toggle('tl-ms--start', anchor === 'start');
                ms.classList.toggle('tl-ms--mid', anchor === 'mid');
                ms.classList.toggle('tl-ms--end', anchor === 'end');
            });
        }

        // Widths are all zero until the section is shown, so animateWork
        // calls this again on entry.
        remeasureTimeline = () => {
            measure();
            anchorMilestones();
            paint(toTime(Number(range.value)));
        };

        measure();
        select(rows.length ? rows[0].slug : null);
        paint(nowT);
    }

    // ── PHOTOGRAPHY animations ──
    function animatePhotography() {
        const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

        tl.fromTo('.section--photography .section-heading',
            { opacity: 0, y: 30 },
            { opacity: 1, y: 0, duration: 0.8 }
        )
        .fromTo('.photography-subtitle',
            { opacity: 0, y: 15 },
            { opacity: 1, y: 0, duration: 0.5 },
            '-=0.4'
        )
        .fromTo('.photography-licence, .gallery-hint',
            { opacity: 0 },
            { opacity: 1, duration: 0.6 },
            '-=0.2'
        );
    }

    // ── PHOTOGRAPHY: the wall ──
    // The photographs hang on a grid that repeats in both directions, seen
    // through a fisheye: the lens swells whatever is in the middle and crowds
    // the rest towards the rim. You drag the wall about to look along it.
    const LENS_MAG = 1.35;      // how much bigger the centre is than the wall
    const FRICTION = 0.92;      // per frame, once a drag is let go
    let gallery = null;

    const clamp01 = v => Math.min(Math.max(v, 0), 1);
    const smoothstep = (a, b, v) => {
        const k = clamp01((v - a) / (b - a));
        return k * k * (3 - 2 * k);
    };

    function mountGallery(grid, items) {
        const tiles = items.map(el => ({ el }));
        if (!tiles.length) return;

        // Square-ish, then the last row topped up from the start so the wall
        // repeats without a gap in it.
        const cols = Math.max(4, Math.ceil(Math.sqrt(tiles.length * 1.15)));
        const rows = Math.ceil(tiles.length / cols);
        for (let i = tiles.length; i < cols * rows; i++) {
            const el = items[i % items.length].cloneNode(true);
            el.setAttribute('aria-hidden', 'true');
            el.querySelector('img').alt = '';
            grid.appendChild(el);
            tiles.push({ el });
        }
        tiles.forEach((t, i) => {
            t.col = i % cols;
            t.row = Math.floor(i / cols);
            const img = t.el.querySelector('img');
            if (img) img.draggable = false;
            // Hung by hand rather than by ruler: a small fixed offset each.
            t.nudgeX = Math.sin(i * 12.9898) * 0.07;
            t.nudgeY = Math.cos(i * 78.233) * 0.07;
        });

        let cell, size, lens, W, H, cx, cy;
        let camX = 0, camY = 0, vx = 0, vy = 0;
        let enteredAt = null;

        function measure() {
            cx = window.innerWidth / 2;
            cy = window.innerHeight / 2;
            cell = Math.max(190, Math.min(cx, cy) * 0.68);
            size = cell * 0.84;
            lens = Math.hypot(cx, cy) * 1.05;
            W = cols * cell;
            H = rows * cell;
            tiles.forEach(t => {
                // Alternate rows sit half a frame along, like a salon hang.
                t.wx = (t.col + (t.row % 2) * 0.5 + t.nudgeX) * cell;
                t.wy = (t.row + t.nudgeY) * cell;
                t.el.style.width = size + 'px';
                t.el.style.height = size + 'px';
            });
        }

        // Nearest copy of a wall coordinate to the camera.
        const wrap = (v, span) => v - span * Math.floor(v / span + 0.5);

        function render(now) {
            const since = enteredAt === null ? Infinity : (now - enteredAt) / 1000;
            tiles.forEach(t => {
                const qx = wrap(t.wx - camX, W);
                const qy = wrap(t.wy - camY, H);
                const r = Math.hypot(qx, qy);

                // tanh keeps the centre close to true scale and squeezes the
                // rest of the endless wall into the screen's radius.
                const th = Math.tanh(LENS_MAG * r / lens);
                const g = lens * th;
                const tangential = r > 1e-3 ? g / r : LENS_MAG;
                const radial = Math.max(0.06, LENS_MAG * (1 - th * th));
                let ux = r > 1e-3 ? qx / r : 0;
                let uy = r > 1e-3 ? qy / r : 0;

                // Fade out before the seam, where a tile jumps to its copy
                // on the far side of the wall.
                const seam = Math.max(Math.abs(qx) / (W / 2), Math.abs(qy) / (H / 2));
                let alpha = 1 - smoothstep(0.78, 0.97, seam);
                let reach = g;
                let grow = 1;

                // Arriving: the wall unwinds outwards from the middle, the
                // way the hero was wound in.
                if (since < 2) {
                    const local = clamp01((since - 0.4 * (g / lens)) / 1.2);
                    const e = 1 - Math.pow(1 - local, 3);
                    const twist = -2.4 * (1 - e) * (1 - e);
                    const c = Math.cos(twist), sn = Math.sin(twist);
                    [ux, uy] = [ux * c - uy * sn, ux * sn + uy * c];
                    reach *= e;
                    grow = e;
                    alpha *= Math.min(1, local * 3);
                }

                const sx = cx + ux * reach;
                const sy = cy + uy * reach;
                const phi = Math.atan2(uy, ux) * 180 / Math.PI;
                t.el.style.transform =
                    `translate(${sx - size / 2}px, ${sy - size / 2}px) ` +
                    `rotate(${phi}deg) scale(${radial * grow}, ${tangential * grow}) rotate(${-phi}deg)`;
                t.el.style.opacity = alpha.toFixed(3);
                t.el.style.visibility = alpha < 0.01 ? 'hidden' : '';
            });
        }

        let raf = 0;
        let last = 0;
        let dragging = false;
        let moved = 0;
        let px = 0, py = 0, pt = 0;

        const drifting = () => Math.abs(vx) > 0.02 || Math.abs(vy) > 0.02;
        const entering = now => enteredAt !== null && now - enteredAt < 2000;

        function tick(now) {
            raf = 0;
            const dt = last ? Math.min(now - last, 50) / 16.67 : 1;
            if (!dragging && drifting()) {
                camX += vx * dt;
                camY += vy * dt;
                const decay = Math.pow(FRICTION, dt);
                vx *= decay;
                vy *= decay;
            }
            render(now);
            if (currentSection === 'photography' && (dragging || drifting() || entering(now))) {
                last = now;
                raf = requestAnimationFrame(tick);
            } else {
                last = 0;
            }
        }
        const kick = () => { if (!raf) raf = requestAnimationFrame(tick); };

        grid.addEventListener('pointerdown', e => {
            if (e.button !== 0) return;
            dragging = true;
            moved = 0;
            vx = vy = 0;
            px = e.clientX; py = e.clientY; pt = e.timeStamp;
            grid.classList.add('is-dragging');
            kick();
        });

        // On the window rather than captured to the wall, so a click still
        // lands on the photograph and opens it.
        window.addEventListener('pointermove', e => {
            if (!dragging) return;
            const dx = e.clientX - px;
            const dy = e.clientY - py;
            const dt = Math.max(e.timeStamp - pt, 1) / 16.67;
            moved += Math.abs(dx) + Math.abs(dy);
            camX -= dx / LENS_MAG;
            camY -= dy / LENS_MAG;
            vx = 0.7 * (-dx / LENS_MAG / dt) + 0.3 * vx;
            vy = 0.7 * (-dy / LENS_MAG / dt) + 0.3 * vy;
            px = e.clientX; py = e.clientY; pt = e.timeStamp;
            kick();
        });

        const release = e => {
            if (!dragging) return;
            dragging = false;
            grid.classList.remove('is-dragging');
            // Held still before letting go means put down, not thrown.
            if (reduceMotion || e.timeStamp - pt > 80) vx = vy = 0;
            kick();
        };
        window.addEventListener('pointerup', release);
        window.addEventListener('pointercancel', release);

        // A drag that ends over a photograph isn't a request to open it.
        grid.addEventListener('click', e => {
            if (moved > 6) {
                e.stopPropagation();
                e.preventDefault();
            }
        }, true);

        grid.addEventListener('wheel', e => {
            e.preventDefault();
            const unit = e.deltaMode === 1 ? 16 : 1;
            camX += e.deltaX * unit / LENS_MAG;
            camY += e.deltaY * unit / LENS_MAG;
            vx = vy = 0;
            kick();
        }, { passive: false });

        const KEYS = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
        grid.addEventListener('keydown', e => {
            const k = KEYS[e.key];
            if (!k) return;
            e.preventDefault();
            // A push that coasts one frame's width before friction stops it.
            const push = cell * (1 - FRICTION);
            if (reduceMotion) {
                camX += k[0] * cell;
                camY += k[1] * cell;
            } else {
                vx = k[0] * push;
                vy = k[1] * push;
            }
            kick();
        });

        window.addEventListener('resize', () => {
            measure();
            kick();
        });

        measure();
        photosLoaded = true;

        gallery = {
            enter() {
                measure();
                vx = vy = 0;
                enteredAt = reduceMotion ? null : performance.now();
                kick();
            },
        };
        gallery.enter();
    }

    // Builds the nodes first, for the case where the markup didn't bring any.
    function populatePhotoGrid(grid, entries) {
        grid.innerHTML = '';
        const items = entries.map(entry => {
            const div = document.createElement('div');
            div.className = 'photo-item';

            const img = document.createElement('img');
            img.alt = entry.alt;
            img.src = entry.src;
            div.appendChild(img);
            grid.appendChild(div);
            return div;
        });
        mountGallery(grid, items);
    }

    // ── Fetch photos from Firebase Storage API ──
    let photosLoaded = false;
    async function fetchPhotos() {
        if (photosLoaded) return;
        const grid = document.getElementById('photo-grid');

        // The photos are rendered into the page now, so that they are in the
        // HTML a crawler reads rather than appearing only once this has run.
        // When they are there, all that is left to do is lay them out.
        const rendered = Array.from(grid.querySelectorAll('.photo-item'));
        if (rendered.length) {
            mountGallery(grid, rendered);
            return;
        }

        try {
            const res = await fetch('/api/images');
            if (!res.ok) throw new Error('API error');
            const data = await res.json();

            if (!data.images || data.images.length === 0) {
                await fetchPhotosByIncrement(grid);
                return;
            }

            populatePhotoGrid(grid, data.images.map(img => ({
                src: `/images/${img.id}?w=600&q=80`,
                alt: img.title
            })));
        } catch {
            await fetchPhotosByIncrement(grid);
        }
    }

    // Fallback: increment counter until 404
    async function fetchPhotosByIncrement(grid) {
        const ids = [];
        let id = 1;

        while (true) {
            try {
                const res = await fetch(`/images/${id}?w=1&q=10`, { method: 'HEAD' });
                if (!res.ok) break;
                ids.push(id);
                id++;
            } catch {
                break;
            }
        }

        if (ids.length === 0) {
            grid.innerHTML = '<p class="loading-repos">no photos found.</p>';
            return;
        }

        populatePhotoGrid(grid, ids.map(i => ({
            src: `/images/${i}?w=600&q=80`,
            alt: `Photo ${i}`
        })));
    }

    // ── GitHub repos ──
    async function fetchGitHubRepos() {
        const container = document.getElementById('github-repos');
        try {
            const res = await fetch('https://api.github.com/users/Fluffik3666/repos?sort=updated&per_page=30');
            if (!res.ok) throw new Error('GitHub API error');
            const repos = await res.json();

            // Filter out forks and empty repos, take top ones
            const filtered = repos
                .filter(r => !r.fork && r.description)
                .slice(0, 8);

            if (filtered.length === 0) {
                container.innerHTML = '<p class="loading-repos">no public repositories found.</p>';
                return;
            }

            container.innerHTML = filtered.map(repo => `
                <a href="${repo.html_url}" target="_blank" rel="noopener" class="repo-row">
                    <span class="repo-name">${repo.name}</span>
                    ${repo.description ? `<span class="repo-desc">${repo.description}</span>` : '<span class="repo-desc"></span>'}
                    <span class="repo-meta">
                        ${repo.language ? `<span class="repo-lang"><span class="lang-dot" style="background:${langColors[repo.language] || '#ccc'}"></span>${repo.language}</span>` : ''}
                        ${repo.stargazers_count > 0 ? `<span>${repo.stargazers_count} stars</span>` : ''}
                    </span>
                </a>
            `).join('');

        } catch (e) {
            // Show repos without descriptions too as fallback
            try {
                const res = await fetch('https://api.github.com/users/Fluffik3666/repos?sort=updated&per_page=12');
                const repos = await res.json();
                const filtered = repos.filter(r => !r.fork).slice(0, 8);

                container.innerHTML = filtered.map(repo => `
                    <a href="${repo.html_url}" target="_blank" rel="noopener" class="repo-row">
                        <span class="repo-name">${repo.name}</span>
                        ${repo.description ? `<span class="repo-desc">${repo.description}</span>` : '<span class="repo-desc"></span>'}
                        <span class="repo-meta">
                            ${repo.language ? `<span class="repo-lang"><span class="lang-dot" style="background:${langColors[repo.language] || '#ccc'}"></span>${repo.language}</span>` : ''}
                        </span>
                    </a>
                `).join('');
            } catch {
                container.innerHTML = '<p class="loading-repos">could not load repositories.</p>';
            }
        }
    }

    // ── Lightbox ──
    // Opens straight away on the copy the wall already has, flown up from
    // where it hung, and develops it into the full-size print as that comes
    // in -- the way a print comes up in the tray. The black hole on it counts
    // the download: its ring closes as the bytes arrive.
    const FULL_WIDTHS = [900, 1200, 1600];
    const fullCache = new Map();

    // As big as the screen allows, leaving room underneath for the caption.
    function fitFrame(ratio) {
        const phone = window.innerWidth <= 640;
        const maxW = window.innerWidth * (phone ? 0.94 : 0.9);
        const maxH = window.innerHeight * (phone ? 0.72 : 0.8);
        let w = maxW;
        let h = w / ratio;
        if (h > maxH) {
            h = maxH;
            w = h * ratio;
        }
        return { w, h };
    }

    // Only as many pixels as the frame will show, from a few fixed widths so
    // the edge cache keeps hitting. q=85 is half the bytes of 95 and looks
    // the same on screen.
    function fullSrc(src, width) {
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        const w = FULL_WIDTHS.find(x => x >= width * dpr) || FULL_WIDTHS[FULL_WIDTHS.length - 1];
        return src.replace(/w=\d+/, `w=${w}`).replace(/q=\d+/, 'q=85');
    }

    // Fetched rather than set as a src, so the ring can show real progress.
    // Shared, so a prefetch on hover and the click that follows are one
    // download.
    function loadFull(url) {
        let entry = fullCache.get(url);
        if (entry) return entry;
        entry = { progress: 0, onprogress: null };
        const report = p => {
            entry.progress = p;
            if (entry.onprogress) entry.onprogress(p);
        };
        entry.promise = (async () => {
            const res = await fetch(url);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const total = Number(res.headers.get('Content-Length')) || 0;
            if (!total || !res.body) {
                report(-1);
                return URL.createObjectURL(await res.blob());
            }
            const reader = res.body.getReader();
            const chunks = [];
            let got = 0;
            for (;;) {
                const { done, value } = await reader.read();
                if (done) break;
                chunks.push(value);
                got += value.length;
                report(Math.min(got / total, 1));
            }
            const type = res.headers.get('Content-Type') || 'image/jpeg';
            return URL.createObjectURL(new Blob(chunks, { type }));
        })();
        entry.promise.then(() => report(1), () => fullCache.delete(url));
        fullCache.set(url, entry);
        return entry;
    }

    const ratioOf = img => (img.naturalWidth && img.naturalHeight
        ? img.naturalWidth / img.naturalHeight
        : 2 / 3);

    function setupLightbox() {
        const lightbox = document.createElement('div');
        lightbox.className = 'lightbox';
        lightbox.setAttribute('role', 'dialog');
        lightbox.setAttribute('aria-modal', 'true');
        lightbox.innerHTML = `
            <figure class="lb-frame">
                <img class="lb-low" alt="" />
                <img class="lb-high" alt="" />
                <div class="lb-loader" aria-hidden="true">
                    <svg class="lb-ring" viewBox="0 0 64 64">
                        <circle class="lb-ring-track" cx="32" cy="32" r="29" />
                        <circle class="lb-ring-bar" cx="32" cy="32" r="29" />
                    </svg>
                    <i class="bh-seed"><i class="bh-seed-disk"></i></i>
                    <span class="lb-loader-label">developing</span>
                </div>
            </figure>
            <p class="lb-caption"></p>`;
        document.body.appendChild(lightbox);

        const frame = lightbox.querySelector('.lb-frame');
        const low = lightbox.querySelector('.lb-low');
        const high = lightbox.querySelector('.lb-high');
        const ring = lightbox.querySelector('.lb-ring');
        const bar = lightbox.querySelector('.lb-ring-bar');
        const caption = lightbox.querySelector('.lb-caption');
        const RING = 2 * Math.PI * 29;
        let current = 0;

        // The developing: blur and grey lift as the download comes in.
        function setProgress(p) {
            const spinning = p < 0;
            ring.classList.toggle('is-spinning', spinning);
            if (spinning) return;
            bar.style.strokeDashoffset = (RING * (1 - p)).toFixed(2);
            low.style.filter =
                `blur(${(10 - 7 * p).toFixed(1)}px) grayscale(${(1 - 0.6 * p).toFixed(2)}) ` +
                `brightness(${(0.6 + 0.3 * p).toFixed(2)})`;
        }

        function open(photoImg) {
            const token = ++current;
            const { w, h } = fitFrame(ratioOf(photoImg));
            frame.style.width = `${w}px`;
            frame.style.height = `${h}px`;

            lightbox.classList.remove('is-ready');
            low.style.filter = '';
            low.src = photoImg.currentSrc || photoImg.src;
            high.removeAttribute('src');
            high.alt = photoImg.alt;
            caption.textContent = photoImg.alt;
            setProgress(0);
            lightbox.classList.add('open');

            // Fly up from where it hung on the wall.
            const from = photoImg.getBoundingClientRect();
            const to = frame.getBoundingClientRect();
            if (!reduceMotion && from.width && to.width) {
                gsap.fromTo(frame, {
                    x: from.left + from.width / 2 - (to.left + to.width / 2),
                    y: from.top + from.height / 2 - (to.top + to.height / 2),
                    scaleX: from.width / to.width,
                    scaleY: from.height / to.height,
                }, {
                    x: 0, y: 0, scaleX: 1, scaleY: 1,
                    duration: 0.6,
                    ease: 'power3.out',
                    overwrite: true,
                });
            }

            const entry = loadFull(fullSrc(low.src, w));
            entry.onprogress = p => { if (token === current) setProgress(p); };
            setProgress(entry.progress);

            const reveal = () => {
                if (token !== current) return;
                low.style.filter = '';
                lightbox.classList.add('is-ready');
            };
            entry.promise.then(async url => {
                if (token !== current) return;
                high.src = url;
                // Decoded before it's shown, so it fades in whole.
                try { await high.decode(); } catch { /* shown regardless */ }
                reveal();
            // If the full size can't be had, the wall's copy is still a
            // photograph: stop developing and show that.
            }, reveal);
        }

        function close() {
            if (!lightbox.classList.contains('open')) return;
            current++;
            lightbox.classList.remove('open');
        }

        document.addEventListener('click', (e) => {
            const photoImg = e.target.closest('.photo-item img');
            if (photoImg) open(photoImg);
        });

        // A pointer resting on a photograph is likely to click it: start
        // fetching then, so the click often lands on a finished download.
        let hoverTimer;
        document.addEventListener('pointerover', (e) => {
            if (e.pointerType !== 'mouse' || e.buttons) return;
            const img = e.target.closest('.photo-item img');
            clearTimeout(hoverTimer);
            if (!img) return;
            hoverTimer = setTimeout(() => {
                loadFull(fullSrc(img.currentSrc || img.src, fitFrame(ratioOf(img)).w));
            }, 140);
        });

        lightbox.addEventListener('click', close);

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') close();
        });
    }

    // ── PHOTOGRAPHY: the way in ──
    // The photography link ends in a small black hole. Clicked, the link
    // shakes, the hole comes away from it and opens out over the page, and
    // the hero is pulled into it piece by piece -- each letter and each band
    // of the photo stretched along the pull as it spirals down. The horizon
    // then grows past the edges of the screen, and the wall unwinds out of
    // the dark on the other side.
    const HOLE = {
        tremble: 0.8,     // the link shakes on its own
        open: 0.55,       // the hole leaves the link...
        settle: 1.9,      // ...and has drifted to the middle
        pull: 0.95,       // the nearest piece lets go
        spread: 1.25,     // the furthest lets go this much later
        fall: 1.5,        // how long each piece takes to go under
        engulf: 3.5,      // the horizon starts to fill the screen
        swallow: 0.7,
    };
    let falling = false;

    // Each letter in its own box, so each can take its own path in.
    function splitLetters(el) {
        const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        const nodes = [];
        while (walker.nextNode()) nodes.push(walker.currentNode);
        const letters = [];
        nodes.forEach(node => {
            const frag = document.createDocumentFragment();
            for (const ch of node.textContent) {
                if (/\s/.test(ch)) {
                    frag.appendChild(document.createTextNode(ch));
                    continue;
                }
                const span = document.createElement('span');
                span.className = 'bh-ch';
                span.textContent = ch;
                frag.appendChild(span);
                letters.push(span);
            }
            node.replaceWith(frag);
        });
        return letters;
    }

    // The photo, cut into bands laid exactly over it.
    function slicePhoto(img, bands) {
        const r = img.getBoundingClientRect();
        if (!r.width) return [];
        const strips = [];
        for (let i = 0; i < bands; i++) {
            const strip = document.createElement('img');
            strip.src = img.currentSrc || img.src;
            strip.alt = '';
            strip.className = 'bh-strip';
            const mid = (i + 0.5) / bands * 100;
            Object.assign(strip.style, {
                left: `${r.left}px`,
                top: `${r.top}px`,
                width: `${r.width}px`,
                height: `${r.height}px`,
                // Each band overlaps its neighbours, so pulling them a little
                // apart smears the picture rather than opening a gap in it.
                clipPath: `inset(${Math.max(i - 0.6, 0) / bands * 100}% 0 ` +
                    `${Math.max(bands - i - 1.6, 0) / bands * 100}% 0)`,
                transformOrigin: `50% ${mid}%`,
            });
            document.body.appendChild(strip);
            strips.push({
                el: strip,
                x: r.left + r.width / 2,
                y: r.top + r.height * (i + 0.5) / bands,
                // Turning or shrinking each band about its own middle would
                // open gaps between them; held level and full size, the
                // bands smear into the hole as one picture.
                stretch: 1.2,
                squash: 0.3,
                spin: 0.15,
                hold: 3,
                blur: true,
            });
        }
        img.style.visibility = 'hidden';
        return strips;
    }

    // Disk, horizon and the light bent round it, in units of the horizon.
    function makeDisk(count) {
        return Array.from({ length: count }, () => {
            const u = 1.35 + 2.4 * Math.pow(Math.random(), 1.6);
            return {
                u,
                a: Math.random() * Math.PI * 2,
                w: 1.7 * Math.pow(u, -1.5),
                heat: (u - 1.35) / 2.4,
            };
        });
    }

    const TILT = -0.2;
    const FLAT = 0.24;

    function drawDisk(ctx, disk, x, y, R, t, side) {
        const c = Math.cos(TILT), s = Math.sin(TILT);
        ctx.lineCap = 'round';
        ctx.lineWidth = Math.max(0.7, R * 0.022);
        disk.forEach(p => {
            const a = p.a + p.w * t;
            // Far side of the disk is behind the horizon, near side in front.
            if ((Math.sin(a) < 0) !== (side === 'back')) return;
            const trail = 0.35 / p.u;
            const point = ang => {
                const dx = Math.cos(ang) * p.u * R;
                const dy = Math.sin(ang) * p.u * R * FLAT;
                return [x + dx * c - dy * s, y + dx * s + dy * c];
            };
            const [x1, y1] = point(a - trail);
            const [x2, y2] = point(a);
            // Brighter on the side coming towards you.
            const glow = (0.75 / p.u) * (1 + 0.6 * Math.cos(a));
            const g = 248 - 50 * p.heat;
            const b = 238 - 95 * p.heat;
            ctx.strokeStyle = `rgba(255, ${g | 0}, ${b | 0}, ${Math.min(glow, 1).toFixed(3)})`;
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
        });
    }

    function drawHole(ctx, disk, x, y, R, t) {
        if (R < 0.5) return;
        ctx.globalCompositeOperation = 'lighter';

        const halo = ctx.createRadialGradient(x, y, R, x, y, R * 4.5);
        halo.addColorStop(0, 'rgba(255, 236, 214, 0.16)');
        halo.addColorStop(1, 'rgba(255, 220, 190, 0)');
        ctx.fillStyle = halo;
        ctx.beginPath();
        ctx.arc(x, y, R * 4.5, 0, Math.PI * 2);
        ctx.fill();

        drawDisk(ctx, disk, x, y, R, t, 'back');

        // The far side of the disk, bent up over the top of the horizon.
        const lensed = ctx.createRadialGradient(x, y, R, x, y, R * 1.7);
        lensed.addColorStop(0, 'rgba(255, 244, 228, 0)');
        lensed.addColorStop(0.08, 'rgba(255, 244, 228, 0.6)');
        lensed.addColorStop(0.35, 'rgba(255, 222, 186, 0.16)');
        lensed.addColorStop(1, 'rgba(255, 210, 170, 0)');
        ctx.fillStyle = lensed;
        ctx.beginPath();
        ctx.arc(x, y, R * 1.7, 0, Math.PI * 2);
        ctx.fill();

        ctx.globalCompositeOperation = 'source-over';
        ctx.fillStyle = '#000';
        ctx.beginPath();
        ctx.arc(x, y, R, 0, Math.PI * 2);
        ctx.fill();

        ctx.globalCompositeOperation = 'lighter';
        ctx.strokeStyle = 'rgba(255, 248, 238, 0.9)';
        ctx.lineWidth = Math.max(1, R * 0.03);
        ctx.beginPath();
        ctx.arc(x, y, R * 1.03, 0, Math.PI * 2);
        ctx.stroke();

        drawDisk(ctx, disk, x, y, R, t, 'front');
        ctx.globalCompositeOperation = 'source-over';
    }

    // Where a piece is on its way down: wound round the hole, drawn towards
    // it, and stretched along the line of the pull.
    function fallTransform(piece, hx, hy, p) {
        const f = p * p;
        const turn = 2.4 * f;
        const dx = piece.x - hx;
        const dy = piece.y - hy;
        const c = Math.cos(turn), s = Math.sin(turn);
        const rx = (dx * c - dy * s) * (1 - f);
        const ry = (dx * s + dy * c) * (1 - f);
        const phi = Math.atan2(ry, rx) * 180 / Math.PI;
        const stretch = 1 + piece.stretch * f;
        const squash = 1 / (1 + (piece.squash ?? 1.5) * f);
        const shrink = 1 - 0.85 * Math.pow(p, piece.hold || 1.5);
        const spin = turn * (piece.spin ?? 1) * 180 / Math.PI;
        return `translate(${hx + rx - piece.x}px, ${hy + ry - piece.y}px) ` +
            `rotate(${phi}deg) scale(${stretch}, ${squash}) rotate(${-phi}deg) ` +
            `rotate(${spin}deg) scale(${shrink})`;
    }

    function fallIntoPhotography(link) {
        if (falling || currentSection !== 'hero') return;
        falling = true;

        const hero = document.getElementById('hero');
        hero.style.pointerEvents = 'none';

        // Pull the hero apart into pieces, remembering how to put it back.
        const saved = [];
        const pieces = [];
        hero.querySelectorAll(
            '.hero-greeting .line, .hero-nav .nav-link, .nav-book-note, .hero-press-label'
        ).forEach(el => {
            saved.push([el, el.innerHTML]);
            splitLetters(el).forEach(span => pieces.push({ el: span, stretch: 2.4 }));
        });
        hero.querySelectorAll('.hero-press-link').forEach(el => {
            pieces.push({ el, stretch: 2 });
        });
        pieces.forEach(piece => {
            const r = piece.el.getBoundingClientRect();
            piece.x = r.left + r.width / 2;
            piece.y = r.top + r.height / 2;
        });
        const heroImg = hero.querySelector('.hero-photo img');
        const strips = heroImg ? slicePhoto(heroImg, 22) : [];
        pieces.push(...strips);

        const seed = link.querySelector('.bh-seed');
        const seedBox = seed.getBoundingClientRect();
        const sx = seedBox.left + seedBox.width / 2;
        const sy = seedBox.top + seedBox.height / 2;
        const vw = window.innerWidth;
        const vh = window.innerHeight;
        const cx = vw / 2;
        const cy = vh / 2;
        const minDim = Math.min(vw, vh);

        // Nearest goes first: near the link, then outwards from the middle.
        const reach = p => Math.min(Math.hypot(p.x - sx, p.y - sy), Math.hypot(p.x - cx, p.y - cy));
        const farthest = Math.max(...pieces.map(reach), 1);
        pieces.forEach(p => {
            p.delay = HOLE.spread * Math.pow(reach(p) / farthest, 0.8);
            p.wobble = Math.random() * Math.PI * 2;
        });

        // Specks of dust off the page, falling in alongside.
        const dust = Array.from({ length: 140 }, () => ({
            x: Math.random() * vw,
            y: Math.random() * vh,
            delay: Math.random() * 1.7,
            fall: 1.1 + Math.random() * 0.6,
            glow: 0.15 + Math.random() * 0.45,
            stretch: 0,
        }));

        const canvas = document.createElement('canvas');
        canvas.className = 'bh-canvas';
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = vw * dpr;
        canvas.height = vh * dpr;
        document.body.appendChild(canvas);
        const ctx = canvas.getContext('2d');
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        const disk = makeDisk(420);
        const seedR = seedBox.width / 2;
        const R1 = minDim * 0.035;
        const R2 = minDim * 0.08;
        const Rend = Math.hypot(vw, vh) * 0.75;
        const end = HOLE.engulf + HOLE.swallow;
        const easeInOut = k => (k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2);
        let eaten = 0;
        const start = performance.now();

        function frame(now) {
            const T = (now - start) / 1000;

            // The link shakes, harder until the hole comes away.
            if (T < HOLE.tremble) {
                const amp = 0.6 + 3.2 * Math.pow(T / HOLE.tremble, 2);
                link.style.transform =
                    `translate(${(Math.random() - 0.5) * amp}px, ${(Math.random() - 0.5) * amp}px)`;
                seed.style.transform = `scale(${1 + 0.8 * T / HOLE.tremble})`;
            } else {
                link.style.transform = '';
            }
            if (T >= HOLE.open) seed.style.visibility = 'hidden';

            const drift = easeInOut(clamp01((T - HOLE.open) / (HOLE.settle - HOLE.open)));
            const hx = sx + (cx - sx) * drift;
            const hy = sy + (cy - sy) * drift;

            // The hole fattens on what it eats, then swallows the screen.
            let gone = 0;
            pieces.forEach(piece => {
                const p = clamp01((T - HOLE.pull - piece.delay) / HOLE.fall);
                if (p >= 1) {
                    gone++;
                    piece.el.style.visibility = 'hidden';
                    return;
                }
                if (p > 0) {
                    piece.el.style.transform = fallTransform(piece, hx, hy, p);
                    piece.el.style.opacity = (1 - smoothstep(0.8, 1, p)).toFixed(3);
                    if (piece.blur) piece.el.style.filter = `blur(${(p * p * 4).toFixed(2)}px)`;
                } else if (T > HOLE.pull) {
                    // Straining: leaning in and trembling before it lets go.
                    const strain = clamp01((T - HOLE.pull) / Math.max(piece.delay, 0.01));
                    const d = Math.hypot(hx - piece.x, hy - piece.y) || 1;
                    const lean = 5 * strain * strain;
                    const shake = 1.4 * strain * Math.sin(T * 60 + piece.wobble);
                    piece.el.style.transform = `translate(${(hx - piece.x) / d * lean + shake}px, ` +
                        `${(hy - piece.y) / d * lean - shake}px)`;
                }
            });
            eaten += (gone / pieces.length - eaten) * 0.08;

            const opened = (1 - Math.pow(1 - clamp01((T - HOLE.open) / (HOLE.settle - HOLE.open)), 3));
            let R = T < HOLE.open ? 0 : seedR + (R1 - seedR) * opened + (R2 - R1) * eaten;
            const swallow = clamp01((T - HOLE.engulf) / HOLE.swallow);
            R += (Rend - R) * Math.pow(swallow, 2.2);

            ctx.clearRect(0, 0, vw, vh);
            ctx.globalCompositeOperation = 'lighter';
            ctx.lineCap = 'round';
            dust.forEach(d => {
                const p = clamp01((T - HOLE.pull - d.delay) / d.fall);
                if (p <= 0 || p >= 1) return;
                const pos = q => {
                    const f = q * q;
                    const turn = 2.4 * f;
                    const dx = d.x - hx, dy = d.y - hy;
                    const c = Math.cos(turn), s = Math.sin(turn);
                    return [hx + (dx * c - dy * s) * (1 - f), hy + (dx * s + dy * c) * (1 - f)];
                };
                const [x1, y1] = pos(Math.max(0, p - 0.06));
                const [x2, y2] = pos(p);
                ctx.strokeStyle = `rgba(255, 240, 225, ${(d.glow * Math.sin(p * Math.PI)).toFixed(3)})`;
                ctx.lineWidth = 1.2;
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.stroke();
            });
            ctx.globalCompositeOperation = 'source-over';
            drawHole(ctx, disk, hx, hy, R, T * (1 + 1.5 * eaten));

            if (T < end) {
                requestAnimationFrame(frame);
                return;
            }

            // Through. The gallery comes up under the dark, which then lifts.
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, vw, vh);
            hero.classList.remove('active');
            saved.forEach(([el, html]) => { el.innerHTML = html; });
            pieces.forEach(piece => {
                piece.el.style.transform = '';
                piece.el.style.opacity = '';
                piece.el.style.visibility = '';
            });
            strips.forEach(strip => strip.el.remove());
            if (heroImg) heroImg.style.visibility = '';
            link.style.transform = '';
            hero.style.pointerEvents = '';
            arrive('photography');
            gsap.to(canvas, {
                opacity: 0,
                duration: 0.9,
                delay: 0.1,
                ease: 'power2.out',
                onComplete() {
                    canvas.remove();
                    falling = false;
                },
            });
        }
        requestAnimationFrame(frame);
    }

    // ── Event listeners ──
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            if (!link.dataset.target) return;
            e.preventDefault();
            if (link.dataset.target === 'photography' && !reduceMotion) {
                fallIntoPhotography(link);
                return;
            }
            showSection(link.dataset.target);
        });
    });

    backNav.addEventListener('click', (e) => {
        e.preventDefault();
        showSection('hero');
    });

    // ── Init ──
    document.addEventListener('DOMContentLoaded', () => {
        animateHero();
        if (typeof ScrollTrigger !== 'undefined') gsap.registerPlugin(ScrollTrigger);
        initWork();
        initShow();
        fetchGitHubRepos();
        setupLightbox();
    });
})();
