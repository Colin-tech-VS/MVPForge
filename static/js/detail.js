(function () {
  const showcaseImg = document.getElementById("detail-showcase-img");
  const tabs = document.querySelectorAll(".detail-showcase-tab");
  const screens = document.querySelectorAll(".detail-screen");

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const src = tab.dataset.src;
      if (!src || !showcaseImg) return;
      showcaseImg.style.opacity = "0";
      window.setTimeout(() => {
        showcaseImg.src = src;
        showcaseImg.style.opacity = "1";
      }, 150);
      tabs.forEach((t) => {
        t.classList.remove("is-active");
        t.setAttribute("aria-selected", "false");
      });
      tab.classList.add("is-active");
      tab.setAttribute("aria-selected", "true");
    });
  });

  screens.forEach((screen) => {
    screen.addEventListener("click", () => {
      const src = screen.dataset.src;
      if (!src || !showcaseImg) return;
      showcaseImg.style.opacity = "0";
      window.setTimeout(() => {
        showcaseImg.src = src;
        showcaseImg.style.opacity = "1";
        showcaseImg.scrollIntoView({ behavior: "smooth", block: "center" });
      }, 150);
      screens.forEach((s) => s.classList.remove("is-featured"));
      screen.classList.add("is-featured");
      tabs.forEach((tab) => {
        const active = tab.dataset.src === src;
        tab.classList.toggle("is-active", active);
        tab.setAttribute("aria-selected", active ? "true" : "false");
      });
    });
  });
})();
