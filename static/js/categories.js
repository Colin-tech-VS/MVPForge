(function () {
  const filters = document.querySelectorAll('.category-filter');
  const wraps = document.querySelectorAll('.category-mvp-wrap');

  if (!filters.length) return;

  filters.forEach((btn) => {
    btn.addEventListener('click', () => {
      const cat = btn.dataset.category;
      filters.forEach((f) => f.classList.toggle('active', f === btn));
      wraps.forEach((wrap) => {
        const match = cat === 'all' || wrap.dataset.category === cat;
        wrap.classList.toggle('hidden', !match);
      });
    });
  });
})();
