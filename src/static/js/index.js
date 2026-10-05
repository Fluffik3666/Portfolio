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
        if (currentSection === id) return;

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
                window.scrollTo(0, 0);

                // Show incoming
                incoming.classList.add('active');
                currentSection = id;
                animateSection(id);

                // Toggle back nav
                if (id === 'hero') {
                    backNav.classList.remove('visible');
                } else {
                    backNav.classList.add('visible');
                }
            }
        });
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
                animatePhotography();
                break;
            case 'tutoring':
                animateTutoring();
                break;
        }
    }

    function animateTutoring() {
        const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
        tl.fromTo('#tutoring .about-photo img', { opacity: 0, scale: 1.05 }, { opacity: 1, scale: 1, duration: 1.2 })
          .fromTo('#tutoring .about-heading', { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.8 }, '-=0.8')
          .fromTo('#tutoring .about-text p', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, stagger: 0.12 }, '-=0.4')
          .fromTo('#tutoring .tutoring-paths', { opacity: 0 }, { opacity: 1, duration: 0.4 }, '-=0.3')
          .fromTo('#tutoring .tutoring-paths li', { opacity: 0, x: -12 }, { opacity: 1, x: 0, duration: 0.4, stagger: 0.1 }, '-=0.2')
          .fromTo('#tutoring .about-links', { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.5 }, '-=0.1');
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
        );
    }

    // ── JS Masonry: absolute positioning, no reflow ──
    function getMasonryCols() {
        const w = window.innerWidth;
        if (w <= 380) return 1;
        if (w <= 640) return 2;
        if (w <= 900) return 2;
        return 3;
    }

    const GAP = 12;

    function populatePhotoGrid(grid, entries) {
        grid.innerHTML = '';
        grid.style.position = 'relative';

        const cols = getMasonryCols();
        const gridWidth = grid.clientWidth;
        const colWidth = (gridWidth - GAP * (cols - 1)) / cols;
        const colHeights = new Array(cols).fill(0);

        entries.forEach(entry => {
            const div = document.createElement('div');
            div.className = 'photo-item';
            div.style.position = 'absolute';
            div.style.width = colWidth + 'px';
            div.style.opacity = '0';

            const img = document.createElement('img');
            img.alt = entry.alt;
            img.src = entry.src;
            img.style.width = '100%';
            img.style.display = 'block';
            img.style.borderRadius = '4px';
            div.appendChild(img);
            grid.appendChild(div);

            // When image loads, calculate its position and fade in
            const place = () => {
                const shortest = colHeights.indexOf(Math.min(...colHeights));
                const x = shortest * (colWidth + GAP);
                const y = colHeights[shortest];

                const ratio = img.naturalHeight / (img.naturalWidth || 1);
                const itemHeight = colWidth * ratio;

                div.style.left = x + 'px';
                div.style.top = y + 'px';

                colHeights[shortest] += itemHeight + GAP;

                // Update grid container height
                grid.style.height = Math.max(...colHeights) + 'px';

                gsap.to(div, {
                    opacity: 1,
                    duration: 0.7,
                    ease: 'power2.out'
                });
            };

            if (img.complete && img.naturalHeight > 0) {
                place();
            } else {
                img.addEventListener('load', place, { once: true });
                img.addEventListener('error', () => { div.remove(); }, { once: true });
            }
        });

        photosLoaded = true;

        // Recalculate on resize
        let resizeTimer;
        const resizeHandler = () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => relayoutGrid(grid), 200);
        };
        window.addEventListener('resize', resizeHandler);
        grid._resizeHandler = resizeHandler;
    }

    // Relayout existing items on resize
    function relayoutGrid(grid) {
        const items = grid.querySelectorAll('.photo-item');
        if (!items.length) return;

        const cols = getMasonryCols();
        const gridWidth = grid.clientWidth;
        const colWidth = (gridWidth - GAP * (cols - 1)) / cols;
        const colHeights = new Array(cols).fill(0);

        items.forEach(div => {
            const img = div.querySelector('img');
            if (!img || !img.naturalHeight) return;

            div.style.width = colWidth + 'px';

            const shortest = colHeights.indexOf(Math.min(...colHeights));
            const x = shortest * (colWidth + GAP);
            const y = colHeights[shortest];

            const ratio = img.naturalHeight / (img.naturalWidth || 1);
            const itemHeight = colWidth * ratio;

            div.style.left = x + 'px';
            div.style.top = y + 'px';

            colHeights[shortest] += itemHeight + GAP;
        });

        grid.style.height = Math.max(...colHeights) + 'px';
    }

    // ── Fetch photos from Firebase Storage API ──
    let photosLoaded = false;
    async function fetchPhotos() {
        if (photosLoaded) return;
        const grid = document.getElementById('photo-grid');

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
    function setupLightbox() {
        const lightbox = document.createElement('div');
        lightbox.className = 'lightbox';
        lightbox.innerHTML = '<img src="" alt="Photo" />';
        document.body.appendChild(lightbox);

        const lbImg = lightbox.querySelector('img');

        document.addEventListener('click', (e) => {
            const photoImg = e.target.closest('.photo-item img');
            if (photoImg) {
                // Swap to high-quality version for lightbox
                const src = photoImg.src;
                lbImg.src = src.replace(/w=\d+/, 'w=1200').replace(/q=\d+/, 'q=95');
                lightbox.classList.add('open');
            }
        });

        lightbox.addEventListener('click', () => {
            lightbox.classList.remove('open');
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') lightbox.classList.remove('open');
        });
    }

    // ── Event listeners ──
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            if (!link.dataset.target) return;
            e.preventDefault();
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
