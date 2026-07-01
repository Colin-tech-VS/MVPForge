(function () {
  const searchInput = document.getElementById('search-input');
  const grid = document.getElementById('mvp-grid');
  const emptyState = document.getElementById('search-empty');

  if (!searchInput || !grid) return;

  const cards = grid.querySelectorAll('.mvp-card');

  function filterCatalogue() {
    const query = searchInput.value.trim().toLowerCase();
    let visible = 0;

    cards.forEach((card) => {
      const title = (card.dataset.title || '').toLowerCase();
      const tagline = (card.dataset.tagline || '').toLowerCase();
      const category = (card.dataset.category || '').toLowerCase();
      const match = !query || title.includes(query) || tagline.includes(query) || category.includes(query);
      card.classList.toggle('hidden', !match);
      if (match) visible++;
    });

    if (emptyState) {
      emptyState.classList.toggle('hidden', visible > 0 || !query);
      grid.classList.toggle('hidden', visible === 0 && query);
    }
  }

  searchInput.addEventListener('input', filterCatalogue);
  document.querySelector('.search-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    filterCatalogue();
    document.getElementById('catalogue')?.scrollIntoView({ behavior: 'smooth' });
  });
})();
