/* ============================================================
   PORTFÓLIO — Lidelmar Braga | script.js
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ── 1. INJETAR ESTILOS DINÂMICOS ────────────────────────────────────────
  const style = document.createElement('style');
  style.textContent = `
    /* Navbar: efeito glass ao rolar */
    header {
      position: sticky;
      top: 0;
      z-index: 1000;
      transition: padding 0.3s ease, background 0.3s ease, box-shadow 0.3s ease;
    }
    header.scrolled {
      padding-top: 6px !important;
      padding-bottom: 6px !important;
      background: rgba(15, 15, 25, 0.92) !important;
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      box-shadow: 0 4px 24px rgba(0,0,0,0.35);
    }

    /* Link ativo no nav */
    nav a {
      position: relative;
      transition: color 0.25s;
    }
    nav a::after {
      content: '';
      position: absolute;
      bottom: -3px;
      left: 0;
      width: 0;
      height: 2px;
      background: var(--accent, #58a6ff);
      border-radius: 2px;
      transition: width 0.3s ease;
    }
    nav a.active::after,
    nav a:hover::after { width: 100%; }
    nav a.active { color: var(--accent, #58a6ff); font-weight: 700; }

    /* Scroll reveal */
    .reveal {
      opacity: 0;
      transform: translateY(30px);
      transition: opacity 0.6s ease, transform 0.6s ease;
    }
    .reveal.visible {
      opacity: 1;
      transform: translateY(0);
    }

    /* Cursor personalizado (desktop) */
    .cursor-dot {
      width: 8px; height: 8px;
      background: var(--accent, #58a6ff);
      border-radius: 50%;
      position: fixed;
      pointer-events: none;
      z-index: 9999;
      transform: translate(-50%, -50%);
    }
    .cursor-ring {
      width: 36px; height: 36px;
      border: 2px solid var(--accent, #58a6ff);
      border-radius: 50%;
      position: fixed;
      pointer-events: none;
      z-index: 9998;
      transform: translate(-50%, -50%);
      opacity: 0.5;
      transition: width 0.3s, height 0.3s, opacity 0.3s;
    }

    /* Stats hero */
    .hero-stats {
      display: flex;
      gap: 1.2rem;
      margin-top: 2rem;
      flex-wrap: wrap;
    }
    .hero-stat {
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 12px;
      padding: 0.75rem 1.3rem;
      text-align: center;
      min-width: 88px;
      backdrop-filter: blur(6px);
    }
    .hero-stat-num {
      display: block;
      font-size: 1.8rem;
      font-weight: 800;
      color: var(--accent, #58a6ff);
      line-height: 1;
    }
    .hero-stat-label {
      font-size: 0.7rem;
      color: rgba(255,255,255,0.55);
      margin-top: 4px;
      display: block;
    }

    /* Cards tilt 3D */
    .card {
      will-change: transform;
      transform-style: preserve-3d;
      transition: box-shadow 0.3s ease;
      cursor: default;
    }
    .card:hover {
      box-shadow: 0 16px 40px rgba(88,166,255,0.15);
    }

    /* Barra de progresso de leitura */
    #read-progress {
      position: fixed;
      top: 0; left: 0;
      width: 0%;
      height: 3px;
      background: linear-gradient(90deg, var(--accent, #58a6ff), #a78bfa);
      z-index: 9999;
      transition: width 0.1s linear;
      border-radius: 0 2px 2px 0;
    }

    /* Botão voltar ao topo */
    #back-top {
      position: fixed;
      bottom: 2rem; right: 2rem;
      width: 46px; height: 46px;
      border-radius: 50%;
      border: none;
      background: var(--accent, #58a6ff);
      color: #000;
      font-size: 1.3rem;
      font-weight: 900;
      cursor: pointer;
      opacity: 0;
      transform: translateY(20px) scale(0.8);
      transition: opacity 0.3s ease, transform 0.3s ease, background 0.2s;
      box-shadow: 0 4px 20px rgba(88,166,255,0.45);
      z-index: 900;
    }
    #back-top.show {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
    #back-top:hover {
      background: #fff;
      transform: translateY(-4px) scale(1.06);
    }

    /* Typing cursor */
    .typing-cursor {
      display: inline-block;
      width: 2px;
      height: 1em;
      background: var(--accent, #58a6ff);
      margin-left: 2px;
      vertical-align: middle;
      animation: blink 0.8s step-end infinite;
    }
    @keyframes blink {
      0%, 100% { opacity: 1; }
      50%       { opacity: 0; }
    }

    /* Toast */
    #toast {
      position: fixed;
      bottom: 5.5rem; right: 2rem;
      background: rgba(20,20,35,0.95);
      color: #fff;
      border: 1px solid rgba(88,166,255,0.3);
      border-radius: 10px;
      padding: 0.75rem 1.2rem;
      font-size: 0.85rem;
      max-width: 240px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.4);
      opacity: 0;
      transform: translateX(20px);
      transition: opacity 0.4s ease, transform 0.4s ease;
      z-index: 800;
      pointer-events: none;
    }
    #toast.show {
      opacity: 1;
      transform: translateX(0);
    }
  `;
  document.head.appendChild(style);

  // ── 2. BARRA DE PROGRESSO DE LEITURA ────────────────────────────────────
  const progress = document.createElement('div');
  progress.id = 'read-progress';
  document.body.prepend(progress);

  window.addEventListener('scroll', () => {
    const max = document.body.scrollHeight - window.innerHeight;
    if (max > 0) progress.style.width = ((window.scrollY / max) * 100) + '%';
  });

  // ── 3. CURSOR PERSONALIZADO (apenas desktop) ────────────────────────────
  if (window.matchMedia('(pointer: fine)').matches) {
    const dot  = document.createElement('div');
    const ring = document.createElement('div');
    dot.className  = 'cursor-dot';
    ring.className = 'cursor-ring';
    document.body.append(dot, ring);

    let mx = 0, my = 0, rx = 0, ry = 0;
    document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });

    (function animateCursor() {
      dot.style.left  = mx + 'px';
      dot.style.top   = my + 'px';
      rx += (mx - rx) * 0.12;
      ry += (my - ry) * 0.12;
      ring.style.left = rx + 'px';
      ring.style.top  = ry + 'px';
      requestAnimationFrame(animateCursor);
    })();

    document.querySelectorAll('a, button, .card').forEach(el => {
      el.addEventListener('mouseenter', () => {
        ring.style.width   = '52px';
        ring.style.height  = '52px';
        ring.style.opacity = '0.8';
      });
      el.addEventListener('mouseleave', () => {
        ring.style.width   = '36px';
        ring.style.height  = '36px';
        ring.style.opacity = '0.5';
      });
    });
  }

  // ── 4. NAVBAR: glass scroll + link ativo ────────────────────────────────
  const header   = document.querySelector('header');
  const navLinks = document.querySelectorAll('nav a[href^="#"]');

  function updateNav() {
    header.classList.toggle('scrolled', window.scrollY > 50);
    let current = '';
    navLinks.forEach(a => {
      const id = a.getAttribute('href').slice(1);
      const el = document.getElementById(id);
      if (el && window.scrollY >= el.offsetTop - 140) current = id;
    });
    navLinks.forEach(a =>
      a.classList.toggle('active', a.getAttribute('href') === `#${current}`)
    );
  }
  window.addEventListener('scroll', updateNav);
  updateNav();

  // ── 5. SMOOTH SCROLL ────────────────────────────────────────────────────
  navLinks.forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const target = document.querySelector(link.getAttribute('href'));
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  // ── 6. TYPING EFFECT na hero ────────────────────────────────────────────
  const heroP = document.querySelector('.hero p');
  if (heroP) {
    const phrases = [
      'Construindo soluções web modernas e funcionais.',
      'Apaixonado por tecnologia e inovação.',
      'Transformando ideias em código real.',
      'Front-End com foco em experiência do usuário.',
    ];
    const cursor = document.createElement('span');
    cursor.className = 'typing-cursor';
    heroP.textContent = '';
    heroP.appendChild(cursor);

    let pi = 0, ci = 0, deleting = false;
    function type() {
      const phrase = phrases[pi];
      if (heroP.firstChild && heroP.firstChild !== cursor) heroP.firstChild.remove();
      heroP.prepend(document.createTextNode(
        deleting ? phrase.slice(0, ci - 1) : phrase.slice(0, ci + 1)
      ));
      ci = deleting ? ci - 1 : ci + 1;
      let delay = deleting ? 38 : 65;
      if (!deleting && ci === phrase.length) { delay = 2200; deleting = true; }
      else if (deleting && ci === 0) { deleting = false; pi = (pi + 1) % phrases.length; delay = 500; }
      setTimeout(type, delay);
    }
    setTimeout(type, 1000);
  }

  // ── 7. SCROLL REVEAL ────────────────────────────────────────────────────
  document.querySelectorAll('.card, .section h2, #sobre p, #formacao p, #contato p')
    .forEach((el, i) => {
      el.classList.add('reveal');
      el.style.transitionDelay = `${(i % 5) * 0.08}s`;
    });

  new IntersectionObserver((entries, obs) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); }
    });
  }, { threshold: 0.1 })
  .observe ? document.querySelectorAll('.reveal').forEach(el => {
    new IntersectionObserver((entries, obs) => {
      entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); }
      });
    }, { threshold: 0.1 }).observe(el);
  }) : null;

  // ── 8. TILT 3D NOS CARDS ────────────────────────────────────────────────
  document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mousemove', e => {
      const r = card.getBoundingClientRect();
      const x = (e.clientX - r.left  - r.width  / 2) / r.width;
      const y = (e.clientY - r.top   - r.height / 2) / r.height;
      card.style.transform  = `perspective(600px) rotateY(${x * 9}deg) rotateX(${-y * 9}deg) translateY(-5px)`;
      card.style.transition = 'transform 0.08s ease';
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform  = 'perspective(600px) rotateY(0) rotateX(0) translateY(0)';
      card.style.transition = 'transform 0.5s ease';
    });
  });

  // ── 9. STATS ANIMADOS na hero ───────────────────────────────────────────
  const heroContainer = document.querySelector('.hero .container');
  if (heroContainer) {
    const statsData = [
      { num: 3, label: 'Anos estudando' },
      { num: 8, label: 'Projetos'       },
      { num: 6, label: 'Certificados'   },
    ];
    const statsEl = document.createElement('div');
    statsEl.className = 'hero-stats';
    statsEl.innerHTML = statsData.map(s => `
      <div class="hero-stat">
        <span class="hero-stat-num" data-target="${s.num}">0</span>
        <span class="hero-stat-label">${s.label}</span>
      </div>`).join('');
    heroContainer.appendChild(statsEl);

    new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.querySelectorAll('.hero-stat-num').forEach(el => {
          const max = +el.dataset.target;
          let n = 0;
          const tick = setInterval(() => {
            n = Math.min(n + 1, max);
            el.textContent = n + (n === max ? '+' : '');
            if (n === max) clearInterval(tick);
          }, 80);
        });
        obs.unobserve(entry.target);
      });
    }, { threshold: 0.5 }).observe(statsEl);
  }

  // ── 10. BOTÃO VOLTAR AO TOPO ────────────────────────────────────────────
  const topBtn = document.createElement('button');
  topBtn.id = 'back-top';
  topBtn.innerHTML = '↑';
  topBtn.title = 'Voltar ao topo';
  document.body.appendChild(topBtn);

  window.addEventListener('scroll', () =>
    topBtn.classList.toggle('show', window.scrollY > 450)
  );
  topBtn.addEventListener('click', () =>
    window.scrollTo({ top: 0, behavior: 'smooth' })
  );

  // ── 11. TOAST DE BOAS-VINDAS ────────────────────────────────────────────
  const toast = document.createElement('div');
  toast.id = 'toast';
  toast.textContent = '👋 Bem-vindo(a) ao meu portfólio!';
  document.body.appendChild(toast);
  setTimeout(() => toast.classList.add('show'), 1400);
  setTimeout(() => toast.classList.remove('show'), 4800);

  // ── 12. CONSOLE GREETING para recrutadores ──────────────────────────────
  console.log('%c👨‍💻 Lidelmar Braga — Dev Front-End em formação', 'color:#58a6ff;font-size:14px;font-weight:bold');
  console.log('%c🔗 linkedin.com/in/lidelmarbg  |  github.com/lidelmar', 'color:#a78bfa;font-size:11px');

});