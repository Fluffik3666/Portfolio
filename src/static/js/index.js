// ── Portfolio ──
(function () {
    const sections = document.querySelectorAll('.section');
    const backNav = document.getElementById('back-nav');
    const navLinks = document.querySelectorAll('.nav-link');
    let currentSection = 'hero';

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
        .fromTo('.about-links',
            { opacity: 0, y: 15 },
            { opacity: 1, y: 0, duration: 0.5 },
            '-=0.2'
        );
    }

    // ── WORK animations ──
    function animateWork() {
        const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

        tl.fromTo('.section--work .section-heading',
            { opacity: 0, y: 30 },
            { opacity: 1, y: 0, duration: 0.8 }
        )
        .fromTo('.work-subheading',
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.5, stagger: 0.1 },
            '-=0.4'
        )
        .fromTo('.skill-tag',
            { opacity: 0, y: 15, scale: 0.95 },
            { opacity: 1, y: 0, scale: 1, duration: 0.4, stagger: 0.05, ease: 'back.out(1.4)' },
            '-=0.3'
        )
        .fromTo('.project-row',
            { opacity: 0, x: -15 },
            { opacity: 1, x: 0, duration: 0.4, stagger: 0.06 },
            '-=0.2'
        );

        // Animate repo rows if already loaded
        const repoRows = document.querySelectorAll('.repo-row');
        if (repoRows.length > 0) {
            gsap.fromTo(repoRows,
                { opacity: 0, x: -15 },
                { opacity: 1, x: 0, duration: 0.35, stagger: 0.05, delay: 0.5 }
            );
        }
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

    // ── TUTORING animations ──
    function animateTutoring() {
        const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
        tl.fromTo('#tutoring .about-photo img',
            { opacity: 0, scale: 1.05 },
            { opacity: 1, scale: 1, duration: 1.2 }
        )
        .fromTo('#tutoring .about-heading',
            { opacity: 0, y: 30 },
            { opacity: 1, y: 0, duration: 0.8 },
            '-=0.8'
        )
        .fromTo('#tutoring .about-text p',
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.6, stagger: 0.12 },
            '-=0.4'
        )
        .fromTo('#tutoring .about-links',
            { opacity: 0, y: 15 },
            { opacity: 1, y: 0, duration: 0.5 },
            '-=0.2'
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
        fetchGitHubRepos();
        setupLightbox();
    });
})();
