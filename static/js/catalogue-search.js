(function () {
  const root = document.querySelector('[data-catalogue-search]');
  const grid = document.getElementById('catalogue-grid');
  if (!root || !grid) return;

  const qInput = document.getElementById('catalogue-q');
  const categorySelect = document.getElementById('catalogue-category');
  const sortSelect = document.getElementById('catalogue-sort');
  const onlineCheck = document.getElementById('catalogue-online');
  const filtersToggle = document.getElementById('catalogue-filters-toggle');
  const filtersPanel = document.getElementById('catalogue-filters-panel');
  const filtersBadge = document.getElementById('catalogue-filters-badge');
  const countEl = document.getElementById('catalogue-count');
  const countLabel = document.getElementById('catalogue-count-label');
  const activeTags = document.getElementById('catalogue-active-tags');
  const resetBtn = document.getElementById('catalogue-reset');
  const emptyState = document.getElementById('catalogue-empty');
  const emptyReset = document.getElementById('catalogue-empty-reset');
  const pricePills = root.querySelectorAll('.catalogue-pill');
  const categoryChips = document.querySelectorAll('#category-chips .category-filter');

  const hasWraps = !!grid.dataset.categoryChips;
  const itemSelector = hasWraps ? '.category-mvp-wrap' : '.mvp-card-link';

  let items = Array.from(grid.querySelectorAll(itemSelector));
  let priceRange = '';
  let debounceTimer = null;
  let staggerIndex = 0;

  function getCardData(el) {
    const link = el.classList.contains('mvp-card-link') ? el : el.querySelector('.mvp-card-link');
    if (!link) return null;
    return {
      el,
      link,
      title: (link.dataset.title || '').toLowerCase(),
      tagline: (link.dataset.tagline || '').toLowerCase(),
      category: (link.dataset.category || '').toLowerCase(),
      price: parseInt(link.dataset.price || '0', 10) || 0,
      stack: (link.dataset.stack || '').toLowerCase(),
      online: link.dataset.online === '1',
      priceText: String(link.dataset.price || ''),
    };
  }

  const cards = items.map(getCardData).filter(Boolean);

  function parsePriceQuery(query) {
    const digits = query.replace(/\s/g, '').replace(/[€k]/gi, '');
    if (/^\d+$/.test(digits)) return parseInt(digits, 10);
    const kMatch = query.match(/(\d+(?:[.,]\d+)?)\s*k/i);
    if (kMatch) return Math.round(parseFloat(kMatch[1].replace(',', '.')) * 1000);
    return null;
  }

  function matchesQuery(card, query) {
    if (!query) return true;
    const q = query.toLowerCase().trim();
    const priceQuery = parsePriceQuery(q);

    if (priceQuery !== null) {
      const tolerance = Math.max(500, priceQuery * 0.05);
      if (Math.abs(card.price - priceQuery) <= tolerance) return true;
      if (card.priceText.includes(q.replace(/\s/g, ''))) return true;
    }

    return (
      card.title.includes(q) ||
      card.tagline.includes(q) ||
      card.category.includes(q) ||
      card.stack.includes(q) ||
      card.priceText.includes(q.replace(/\s/g, '')) ||
      formatPrice(card.price).includes(q)
    );
  }

  function formatPrice(n) {
    return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  }

  function inPriceRange(price) {
    if (!priceRange) return true;
    const [min, max] = priceRange.split('-').map(Number);
    return price >= min && price <= max;
  }

  function activeFilterCount() {
    let n = 0;
    if (categorySelect?.value) n++;
    if (priceRange) n++;
    if (onlineCheck?.checked) n++;
    if (sortSelect?.value && sortSelect.value !== 'default') n++;
    return n;
  }

  function updateBadge() {
    const n = activeFilterCount();
    if (!filtersBadge) return;
    filtersBadge.textContent = String(n);
    filtersBadge.classList.toggle('hidden', n === 0);
  }

  function syncChips(category) {
    categoryChips.forEach((chip) => {
      const cat = chip.dataset.category || '';
      chip.classList.toggle('is-active', cat === (category || ''));
    });
  }

  function buildTags(state) {
    if (!activeTags) return;
    activeTags.innerHTML = '';
    const tags = [];

    if (state.query) tags.push({ key: 'query', label: `« ${state.query} »` });
    if (state.category) tags.push({ key: 'category', label: state.category });
    if (state.priceRange) {
      const labels = {
        '0-15000': '< 15 k€',
        '15000-30000': '15 – 30 k€',
        '30000-50000': '30 – 50 k€',
        '50000-999999999': '50 k€ +',
      };
      tags.push({ key: 'price', label: labels[state.priceRange] || state.priceRange });
    }
    if (state.online) tags.push({ key: 'online', label: 'En ligne' });

    tags.forEach((tag) => {
      const span = document.createElement('span');
      span.className = 'catalogue-tag';
      span.innerHTML = `${tag.label}<button type="button" aria-label="Retirer le filtre">×</button>`;
      span.querySelector('button').addEventListener('click', () => removeTag(tag.key));
      activeTags.appendChild(span);
    });
  }

  function removeTag(key) {
    switch (key) {
      case 'query':
        if (qInput) qInput.value = '';
        break;
      case 'category':
        if (categorySelect) categorySelect.value = '';
        syncChips('');
        break;
      case 'price':
        priceRange = '';
        pricePills.forEach((p) => p.classList.toggle('is-active', !p.dataset.price));
        break;
      case 'online':
        if (onlineCheck) onlineCheck.checked = false;
        break;
    }
    applyFilters();
  }

  function getState() {
    return {
      query: (qInput?.value || '').trim(),
      category: categorySelect?.value || '',
      priceRange,
      online: !!onlineCheck?.checked,
      sort: sortSelect?.value || 'default',
    };
  }

  function sortCards(matched) {
    const sort = sortSelect?.value || 'default';
    if (sort === 'default') {
      matched.sort((a, b) => items.indexOf(a.el) - items.indexOf(b.el));
      return;
    }
    if (sort === 'price-asc') matched.sort((a, b) => a.price - b.price);
    else if (sort === 'price-desc') matched.sort((a, b) => b.price - a.price);
    else if (sort === 'name-asc') matched.sort((a, b) => a.title.localeCompare(b.title, 'fr'));
  }

  function applyFilters() {
    const state = getState();
    const matched = [];

    cards.forEach((card) => {
      const catOk = !state.category || card.category === state.category.toLowerCase();
      const priceOk = inPriceRange(card.price);
      const onlineOk = !state.online || card.online;
      const queryOk = matchesQuery(card, state.query);
      const ok = catOk && priceOk && onlineOk && queryOk;

      card.el.classList.toggle('is-filtered-out', !ok);
      if (ok) matched.push(card);
    });

    sortCards(matched);

    matched.forEach((card, i) => {
      grid.appendChild(card.el);
      card.el.classList.remove('is-anim-in');
      void card.el.offsetWidth;
      card.el.style.animationDelay = `${Math.min(i * 40, 320)}ms`;
      card.el.classList.add('is-anim-in');
    });

    const visible = matched.length;
    if (countEl) {
      countEl.textContent = String(visible);
      countEl.classList.remove('is-bump');
      void countEl.offsetWidth;
      countEl.classList.add('is-bump');
    }
    if (countLabel) {
      countLabel.textContent = visible <= 1 ? 'projet' : 'projets';
    }

    const hasFilters = state.query || state.category || state.priceRange || state.online ||
      (state.sort && state.sort !== 'default');

    resetBtn?.classList.toggle('hidden', !hasFilters);
    emptyState?.classList.toggle('hidden', visible > 0);
    grid.classList.toggle('hidden', visible === 0);

    buildTags(state);
    updateBadge();
    syncChips(state.category);
  }

  function resetAll() {
    if (qInput) qInput.value = '';
    if (categorySelect) categorySelect.value = '';
    if (sortSelect) sortSelect.value = 'default';
    if (onlineCheck) onlineCheck.checked = false;
    priceRange = '';
    pricePills.forEach((p) => p.classList.toggle('is-active', !p.dataset.price));
    syncChips('');
    applyFilters();
  }

  qInput?.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(applyFilters, 120);
  });

  categorySelect?.addEventListener('change', applyFilters);
  sortSelect?.addEventListener('change', applyFilters);
  onlineCheck?.addEventListener('change', applyFilters);

  pricePills.forEach((pill) => {
    pill.addEventListener('click', () => {
      priceRange = pill.dataset.price || '';
      pricePills.forEach((p) => p.classList.toggle('is-active', p === pill));
      applyFilters();
    });
  });

  filtersToggle?.addEventListener('click', () => {
    const open = filtersPanel?.hidden;
    if (filtersPanel) filtersPanel.hidden = !open;
    filtersToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  categoryChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      const cat = chip.dataset.category || '';
      if (categorySelect) categorySelect.value = cat;
      syncChips(cat);
      applyFilters();
    });
  });

  resetBtn?.addEventListener('click', resetAll);
  emptyReset?.addEventListener('click', resetAll);

  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      qInput?.focus();
    }
    if (e.key === 'Escape' && document.activeElement === qInput) {
      qInput.blur();
    }
  });

  applyFilters();
})();
