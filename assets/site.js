// Shared header, footer and binary-decode effect.
// Pages include <header data-site-header></header> and <footer data-site-footer></footer>.

const NAV = [
    { href: '/research', label: 'Research' },
    { href: '/people', label: 'People' },
    { href: '/news', label: 'News' },
    { href: '/contact', label: 'Contact' },
    { href: 'https://github.com/infoTheoryLab/', label: 'GitHub', external: true }
];

function renderHeader(el) {
    // Clean URLs: /research and /research.html both mark Research as current.
    const current = '/' + location.pathname.split('/').pop().replace(/\.html$/, '');
    const links = NAV.map(item => {
        const attrs = item.external
            ? ' target="_blank" rel="noopener"'
            : (item.href === current ? ' aria-current="page"' : '');
        return `<a href="${item.href}"${attrs}>${item.label}</a>`;
    }).join('');

    el.className = 'site-header';
    el.innerHTML = `
        <div class="wrap">
            <a class="wordmark" href="/"><span class="wordmark-accent">Information Theory</span> Lab <span class="wordmark-at">@ Harvard</span></a>
            <button class="nav-toggle" aria-label="Open menu" aria-expanded="false">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 7h18M3 12h18M3 17h18"/></svg>
            </button>
            <nav class="nav">${links}</nav>
        </div>`;

    const toggle = el.querySelector('.nav-toggle');
    const nav = el.querySelector('.nav');
    toggle.addEventListener('click', () => {
        const open = nav.classList.toggle('open');
        toggle.setAttribute('aria-expanded', open);
    });
}

function renderFooter(el) {
    el.className = 'site-footer';
    el.innerHTML = `
        <div class="wrap">
            <div class="cols">
                <div>
                    <div class="footer-title">The <span class="accent">Information Theory</span> Laboratory</div>
                    Harvard John A. Paulson School of Engineering and Applied Sciences<br>
                    Science &amp; Engineering Complex, 150 Western Ave, Allston, MA 02134
                </div>
                <ul>
                    <li><a href="/research">Research</a></li>
                    <li><a href="/people">People</a></li>
                    <li><a href="/news">News</a></li>
                </ul>
                <ul>
                    <li><a href="/contact">Contact</a></li>
                    <li><a href="https://github.com/infoTheoryLab/" target="_blank" rel="noopener">GitHub</a></li>
                </ul>
            </div>
            <div class="fineprint">&copy; ${new Date().getFullYear()} The Information Theory Laboratory, Harvard University</div>
        </div>`;
}

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function randomBits(n) {
    let s = '';
    for (let i = 0; i < n; i++) s += Math.random() < 0.5 ? '0' : '1';
    return s;
}

// Scramble an element's text into bits, then reveal it left to right.
// Spaces are preserved so word shapes stay recognizable while decoding.
function decode(el, { frames = 20, noiseFrames = 10, interval = 55 } = {}) {
    const text = el.dataset.text || el.textContent;
    el.dataset.text = text;
    if (reduceMotion) { el.textContent = text; return Promise.resolve(); }

    const noise = () => text.replace(/[^\s]/g, () => (Math.random() < 0.5 ? '0' : '1'));
    return new Promise(resolve => {
        let step = 0;
        const timer = setInterval(() => {
            if (step < noiseFrames) {
                el.textContent = noise();
            } else {
                const k = Math.floor(((step - noiseFrames) / (frames - noiseFrames)) * text.length);
                el.textContent = text.slice(0, k) + noise().slice(k);
            }
            if (++step > frames) {
                clearInterval(timer);
                el.textContent = text;
                resolve();
            }
        }, interval);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-site-header]').forEach(renderHeader);
    document.querySelectorAll('.wordmark-accent').forEach(el => decode(el, { interval: 50 }));
    document.querySelectorAll('[data-site-footer]').forEach(renderFooter);
});
