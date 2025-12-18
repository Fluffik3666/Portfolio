// Profession animation
const professions = [
    'creators',
    'innovators',
    'dreamers',
    'builders',
    'artists',
    'thinkers',
    'makers',
    'visionaries'
];

let currentProfessionIndex = 0;
let professionInterval;

function animateProfession() {
    const professionElement = document.getElementById('professionText');
    if (!professionElement) return;

    // Fly out current profession
    professionElement.style.animation = 'flyOut 0.6s cubic-bezier(0.645, 0.045, 0.355, 1) forwards';

    setTimeout(() => {
        // Change profession
        currentProfessionIndex = (currentProfessionIndex + 1) % professions.length;
        professionElement.textContent = professions[currentProfessionIndex];

        // Fly in new profession
        professionElement.style.animation = 'flyIn 0.6s cubic-bezier(0.645, 0.045, 0.355, 1) forwards';
    }, 600);
}

// Start profession animation if on home page
if (document.getElementById('professionText')) {
    professionInterval = setInterval(animateProfession, 2000);
}

// Dreamy smooth scrolling (desktop only)
let isScrolling = false;
let targetScroll = window.pageYOffset;
let currentScroll = window.pageYOffset;
const scrollSpeed = 0.08; // Lower = slower/dreamier

// Check if device is mobile/touch
const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
                 ('ontouchstart' in window) ||
                 (navigator.maxTouchPoints > 0);

function dreamyScroll() {
    if (Math.abs(targetScroll - currentScroll) < 0.5) {
        currentScroll = targetScroll;
    } else {
        currentScroll += (targetScroll - currentScroll) * scrollSpeed;
    }

    window.scrollTo(0, currentScroll);

    if (isScrolling || currentScroll !== targetScroll) {
        requestAnimationFrame(dreamyScroll);
    }
}

// Only apply custom scrolling on desktop
if (!isMobile) {
    window.addEventListener('wheel', (e) => {
        e.preventDefault();
        targetScroll += e.deltaY;
        targetScroll = Math.max(0, Math.min(targetScroll, document.body.scrollHeight - window.innerHeight));

        if (!isScrolling) {
            isScrolling = true;
            requestAnimationFrame(dreamyScroll);
        }
    }, { passive: false });
}

// Navigation visibility on scroll
const nav = document.getElementById('mainNav');
const scrollIndicator = document.getElementById('scrollIndicator');
let lastScroll = 0;

function handleScroll() {
    const currentScrollPos = isMobile ? window.pageYOffset : (currentScroll || window.pageYOffset);

    // Show nav after scrolling past hero section
    if (nav && !nav.classList.contains('visible')) {
        if (currentScrollPos > window.innerHeight * 0.7) {
            nav.classList.add('visible');
        }
    }

    // Hide scroll indicator when scrolling starts
    if (scrollIndicator && currentScrollPos > 50) {
        scrollIndicator.classList.add('hidden');
    } else if (scrollIndicator && currentScrollPos <= 50) {
        scrollIndicator.classList.remove('hidden');
    }

    lastScroll = currentScrollPos;
}

// Scroll indicator click
if (scrollIndicator) {
    scrollIndicator.addEventListener('click', () => {
        if (isMobile) {
            window.scrollTo({ top: window.innerHeight, behavior: 'smooth' });
        } else {
            targetScroll = window.innerHeight;
        }
    });
}

// Throttle scroll events
let ticking = false;
window.addEventListener('scroll', () => {
    if (!ticking) {
        window.requestAnimationFrame(() => {
            handleScroll();
            ticking = false;
        });
        ticking = true;
    }
});

// Intersection Observer for scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
            setTimeout(() => {
                entry.target.classList.add('visible');
            }, index * 100);
        }
    });
}, observerOptions);

// Observe all elements with data-scroll attribute
document.querySelectorAll('[data-scroll]').forEach((el) => {
    observer.observe(el);
});

// Observe about section elements
document.querySelectorAll('.about-left, .about-right').forEach((el) => {
    observer.observe(el);
});

// Observe contact cards
document.querySelectorAll('.contact-card').forEach((el, index) => {
    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, index * 150);
            }
        });
    }, observerOptions);
    cardObserver.observe(el);
});

// Observe project and skill cards
document.querySelectorAll('.project-card, .skill-card').forEach((el, index) => {
    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, index * 100);
            }
        });
    }, observerOptions);
    cardObserver.observe(el);
});

// Dark mode toggle
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;
const body = document.body;

// Check for saved theme preference or default to light mode
const currentTheme = localStorage.getItem('theme') || 'light';
body.setAttribute('data-theme', currentTheme);

// Update icon based on theme
function updateThemeIcon() {
    const icon = themeToggle?.querySelector('.material-symbols-outlined');
    if (icon) {
        icon.textContent = body.getAttribute('data-theme') === 'dark' ? 'light_mode' : 'dark_mode';
    }
}

updateThemeIcon();

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const currentTheme = body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon();
    });
}

// Page transitions
const pageTransition = document.querySelector('.page-transition');

// Handle link clicks for smooth transitions
document.querySelectorAll('a[href^="/"], a[href^="./"], a[href^="../"]').forEach(link => {
    // Skip external links and anchors
    if (link.hostname !== window.location.hostname || link.getAttribute('href').startsWith('#')) {
        return;
    }

    link.addEventListener('click', (e) => {
        e.preventDefault();
        const href = link.getAttribute('href');

        // Trigger transition
        if (pageTransition) {
            pageTransition.classList.add('active');

            setTimeout(() => {
                window.location.href = href;
            }, 500);
        } else {
            window.location.href = href;
        }
    });
});

// Remove transition on page load
window.addEventListener('load', () => {
    if (pageTransition) {
        pageTransition.classList.remove('active');
    }
});

// Parallax effect for elements with data-scroll-speed
function handleParallax() {
    const scrolled = isMobile ? window.pageYOffset : (currentScroll || window.pageYOffset);

    document.querySelectorAll('[data-scroll-speed]').forEach((el) => {
        const speed = parseFloat(el.getAttribute('data-scroll-speed'));
        const yPos = -(scrolled * speed / 10);
        el.style.transform = `translateY(${yPos}px)`;
    });
}

window.addEventListener('scroll', handleParallax);

// Mobile menu toggle
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navLinks = document.querySelector('.nav-links');

if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        mobileMenuBtn.classList.toggle('active');
    });

    // Close menu when clicking a link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
            mobileMenuBtn.classList.remove('active');
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.nav-content')) {
            navLinks.classList.remove('active');
            mobileMenuBtn.classList.remove('active');
        }
    });
}

// Initial calls
handleScroll();
handleParallax();
