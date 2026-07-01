(function () {
  const header = document.getElementById('header');
  const nav = document.querySelector('.nav');
  const navToggle = document.querySelector('.nav-toggle');

  window.addEventListener('scroll', () => {
    header?.classList.toggle('scrolled', window.scrollY > 8);
  }, { passive: true });

  function closeNav() {
    if (!nav?.classList.contains('open')) return;
    nav.classList.remove('open');
    navToggle?.setAttribute('aria-expanded', 'false');
  }

  navToggle?.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });

  document.querySelectorAll('.nav-menu a').forEach((link) => {
    link.addEventListener('click', closeNav);
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeNav();
  });

  document.addEventListener('click', (e) => {
    if (nav?.classList.contains('open') && !nav.contains(e.target)) closeNav();
  });

  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', (e) => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  document.querySelectorAll('.home-hero .reveal, .page-header .reveal').forEach((el) => {
    el.classList.add('visible');
  });

  const revealEls = document.querySelectorAll(
    '.reveal:not(.visible)'
  );
  if (revealEls.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08, rootMargin: '0px 0px -24px 0px' }
    );
    revealEls.forEach((el) => observer.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add('visible'));
  }

  const TOAST_DURATION = 4500;

  function dismissToast(toast) {
    if (toast.classList.contains('toast-leaving')) return;
    toast.classList.add('toast-leaving');
    toast.addEventListener('animationend', () => {
      toast.remove();
      const container = document.getElementById('toast-container');
      if (container && !container.children.length) {
        container.remove();
      }
    }, { once: true });
  }

  document.querySelectorAll('.toast').forEach((toast) => {
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn?.addEventListener('click', () => dismissToast(toast));

    let timer;
    let remaining = TOAST_DURATION;
    let startedAt = Date.now();

    function scheduleDismiss() {
      startedAt = Date.now();
      timer = setTimeout(() => dismissToast(toast), remaining);
    }

    toast.addEventListener('mouseenter', () => {
      clearTimeout(timer);
      remaining -= Date.now() - startedAt;
    });

    toast.addEventListener('mouseleave', scheduleDismiss);
    scheduleDismiss();
  });
})();
