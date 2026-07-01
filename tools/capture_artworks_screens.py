"""Capture public Artworks Digital screenshots for MVPForge seed assets."""
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parents[1] / "static" / "seed" / "artworks"
OUT.mkdir(parents=True, exist_ok=True)

SHOTS = [
    ("vitrine-home.png", "https://www.artworksdigital.fr/", 1440, 900),
    ("vitrine-marketplace.png", "https://www.artworksdigital.fr/marketplace", 1440, 1000),
    ("vitrine-portfolio.png", "https://www.artworksdigital.fr/portfolio/antoine-marelle", 1440, 1000),
    ("vitrine-galeries.png", "https://www.artworksdigital.fr/galeries", 1440, 900),
]

ADMIN_SNAPSHOT = Path(__file__).resolve().parent / "admin_analytics_snapshot.html"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="fr-FR",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        for name, url, width, height in SHOTS:
            print(f"Capturing {url} -> {name}")
            page.set_viewport_size({"width": width, "height": height})
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(2500)
            page.screenshot(path=str(OUT / name), full_page=False)
        if ADMIN_SNAPSHOT.exists():
            print(f"Capturing admin snapshot -> admin-analytics.png")
            page.set_viewport_size({"width": 1440, "height": 900})
            page.goto(ADMIN_SNAPSHOT.as_uri(), wait_until="load", timeout=30000)
            page.wait_for_timeout(500)
            page.screenshot(path=str(OUT / "admin-analytics.png"), full_page=False)
        browser.close()
    print("Done:", list(OUT.glob("*.png")))


if __name__ == "__main__":
    main()
