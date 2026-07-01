(function () {
  const cfg = window.PUBLISH_CONFIG || { maxImages: 20, minImages: 1 };
  const form = document.getElementById('publish-form');
  if (!form) return;

  const stackInput = document.getElementById('stack');
  const stackBadges = document.getElementById('stack-badges');
  const categorySelect = document.getElementById('category');
  const categoryOtherWrap = document.getElementById('category-other-wrap');
  const isOnlineToggle = document.getElementById('is_online');
  const onlineFields = document.getElementById('online-fields');
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('images');
  const browseBtn = document.getElementById('browse-btn');
  const previewGrid = document.getElementById('image-preview-grid');
  const imageCountEl = document.getElementById('image-count');
  const progressFill = document.getElementById('progress-fill');
  const progressPct = document.getElementById('progress-pct');
  const navLinks = document.querySelectorAll('.publish-nav-link');
  const sections = document.querySelectorAll('.publish-section');

  let selectedFiles = [];

  function escapeHtml(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
  }

  function onFieldChange() {
    updateProgress();
    updateLivePreview();
  }

  // ── Live preview ──
  function updateLivePreview() {
    const title = document.getElementById('preview-title');
    const tagline = document.getElementById('preview-tagline');
    const category = document.getElementById('preview-category');
    const price = document.getElementById('preview-price');
    const stack = document.getElementById('preview-stack');
    const cover = document.getElementById('preview-cover');
    const onlineBlock = document.getElementById('preview-online');

    const titleVal = document.getElementById('title')?.value.trim();
    const taglineVal = document.getElementById('tagline')?.value.trim();
    const catVal = categorySelect?.value;
    const catOther = document.getElementById('category_other')?.value.trim();
    const priceVal = document.getElementById('price')?.value;

    if (title) title.textContent = titleVal || 'Titre de votre projet';
    if (tagline) tagline.textContent = taglineVal || "Votre description courte s'affichera ici...";

    if (category) {
      if (catVal === 'Autre' && catOther) category.textContent = catOther;
      else if (catVal) category.textContent = catVal;
      else category.textContent = 'Catégorie';
    }

    if (price) {
      price.textContent = priceVal ? `${Number(priceVal).toLocaleString('fr-FR')} €` : '— €';
    }

    if (stack) {
      const items = (stackInput?.value || '').split(',').map((s) => s.trim()).filter(Boolean);
      stack.innerHTML = items.map((t) => `<span class="tech-tag">${escapeHtml(t)}</span>`).join('');
    }

    if (cover) {
      if (selectedFiles.length > 0) {
        cover.innerHTML = `<img src="${URL.createObjectURL(selectedFiles[0])}" alt="Aperçu">`;
      } else {
        cover.innerHTML = '<span class="preview-cover-placeholder">Vos images apparaîtront ici</span>';
      }
    }

    if (onlineBlock) {
      const on = isOnlineToggle?.checked;
      onlineBlock.classList.toggle('hidden', !on);
      if (on) {
        const v = document.getElementById('monthly_visitors')?.value;
        const r = document.getElementById('monthly_revenue')?.value;
        const visitorsEl = document.getElementById('preview-visitors');
        const revenueEl = document.getElementById('preview-revenue');
        if (visitorsEl) visitorsEl.textContent = v ? `${Number(v).toLocaleString('fr-FR')} visiteurs/mois` : '';
        if (revenueEl) revenueEl.textContent = r ? `${Number(r).toLocaleString('fr-FR')} €/mois` : '';
      }
    }
  }

  // ── Stack badges ──
  function updateStackBadges() {
    if (!stackInput || !stackBadges) return;
    const items = stackInput.value.split(',').map((s) => s.trim()).filter(Boolean);
    stackBadges.innerHTML = items.map((t) => `<span class="stack-badge">${escapeHtml(t)}</span>`).join('');
    onFieldChange();
  }

  stackInput?.addEventListener('input', updateStackBadges);

  // ── Category Autre ──
  function toggleCategoryOther() {
    categoryOtherWrap?.classList.toggle('hidden', categorySelect?.value !== 'Autre');
    onFieldChange();
  }

  categorySelect?.addEventListener('change', toggleCategoryOther);
  toggleCategoryOther();

  // ── Online switch ──
  function toggleOnlineFields() {
    onlineFields?.classList.toggle('hidden', !isOnlineToggle?.checked);
    onFieldChange();
  }

  isOnlineToggle?.addEventListener('change', toggleOnlineFields);

  // ── Char counters ──
  function bindCounter(inputId, countId) {
    const input = document.getElementById(inputId);
    const counter = document.getElementById(countId);
    if (!input || !counter) return;
    const update = () => {
      counter.textContent = input.value.length;
      onFieldChange();
    };
    input.addEventListener('input', update);
    update();
  }

  bindCounter('tagline', 'tagline-count');
  bindCounter('description', 'description-count');

  // ── Images ──
  function syncFileInput() {
    const dt = new DataTransfer();
    selectedFiles.forEach((f) => dt.items.add(f));
    if (fileInput) fileInput.files = dt.files;
    if (imageCountEl) imageCountEl.textContent = selectedFiles.length;
    onFieldChange();
  }

  function renderPreviews() {
    if (!previewGrid) return;
    previewGrid.innerHTML = '';
    selectedFiles.forEach((file, i) => {
      const div = document.createElement('div');
      div.className = 'preview-item';
      const img = document.createElement('img');
      img.src = URL.createObjectURL(file);
      img.alt = file.name;
      const order = document.createElement('span');
      order.className = 'preview-order';
      order.textContent = i + 1;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'preview-remove';
      btn.innerHTML = '&times;';
      btn.setAttribute('aria-label', 'Supprimer');
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        selectedFiles.splice(i, 1);
        renderPreviews();
      });
      div.appendChild(img);
      div.appendChild(order);
      div.appendChild(btn);
      previewGrid.appendChild(div);
    });
    syncFileInput();
  }

  function addFiles(files) {
    const incoming = Array.from(files).filter((f) => f.type.startsWith('image/'));
    const remaining = cfg.maxImages - selectedFiles.length;
    if (remaining <= 0) return;
    selectedFiles = selectedFiles.concat(incoming.slice(0, remaining));
    renderPreviews();
  }

  browseBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    fileInput?.click();
  });

  dropzone?.addEventListener('click', () => fileInput?.click());

  fileInput?.addEventListener('change', () => {
    if (fileInput.files) addFiles(fileInput.files);
    fileInput.value = '';
  });

  ['dragenter', 'dragover'].forEach((evt) => {
    dropzone?.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach((evt) => {
    dropzone?.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone?.addEventListener('drop', (e) => {
    if (e.dataTransfer?.files) addFiles(e.dataTransfer.files);
  });

  // ── Progress ──
  function fieldFilled(el) {
    if (!el) return false;
    if (el.type === 'checkbox') return el.checked;
    return el.value.trim().length > 0;
  }

  function updateProgress() {
    const checks = [
      fieldFilled(document.getElementById('title')),
      fieldFilled(document.getElementById('tagline')),
      (document.getElementById('description')?.value.trim().length || 0) >= 30,
      fieldFilled(categorySelect) && (categorySelect?.value !== 'Autre' || fieldFilled(document.getElementById('category_other'))),
      fieldFilled(document.getElementById('price')),
      form.querySelectorAll('input[name="monetization"]:checked').length > 0,
      fieldFilled(stackInput),
      !isOnlineToggle?.checked || (
        fieldFilled(document.getElementById('monthly_visitors')) &&
        fieldFilled(document.getElementById('monthly_revenue')) &&
        fieldFilled(document.getElementById('launch_date')) &&
        fieldFilled(document.getElementById('site_url'))
      ),
      fieldFilled(document.getElementById('traffic_source')),
      (document.getElementById('strengths')?.value.trim().length || 0) >= 10,
      (document.getElementById('weaknesses')?.value.trim().length || 0) >= 10,
      (document.getElementById('resale_reason')?.value.trim().length || 0) >= 10,
      selectedFiles.length >= cfg.minImages,
    ];
    const pct = Math.round((checks.filter(Boolean).length / checks.length) * 100);
    if (progressFill) progressFill.style.width = `${pct}%`;
    if (progressPct) progressPct.textContent = pct;
  }

  form.querySelectorAll('[data-track]').forEach((el) => {
    el.addEventListener('input', onFieldChange);
    el.addEventListener('change', onFieldChange);
  });

  form.querySelectorAll('input[name="monetization"]').forEach((el) => {
    el.addEventListener('change', onFieldChange);
  });

  updateStackBadges();
  updateProgress();
  updateLivePreview();

  // ── Section nav ──
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          navLinks.forEach((link) => {
            link.classList.toggle('active', link.dataset.section === id);
          });
        }
      });
    },
    { rootMargin: '-30% 0px -60% 0px' }
  );

  sections.forEach((s) => observer.observe(s));

  navLinks.forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      document.getElementById(link.dataset.section)?.scrollIntoView({ behavior: 'smooth' });
    });
  });

  const revealObs = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          revealObs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08 }
  );

  sections.forEach((s) => revealObs.observe(s));

  form.addEventListener('submit', (e) => {
    syncFileInput();
    if (selectedFiles.length < cfg.minImages) {
      e.preventDefault();
      document.getElementById('section-visuels')?.scrollIntoView({ behavior: 'smooth' });
      return;
    }
    document.getElementById('submit-btn')?.classList.add('loading');
  });
})();
