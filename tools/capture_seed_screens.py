"""Capture screenshots for MVPForge seed assets (all catalogue projects)."""
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1] / "static" / "seed"

SHOTS = {
    "artworks": [
        ("vitrine-home.png", "https://www.artworksdigital.fr/", 1440, 900),
        ("vitrine-marketplace.png", "https://www.artworksdigital.fr/marketplace", 1440, 1000),
        ("vitrine-portfolio.png", "https://www.artworksdigital.fr/portfolio/antoine-marelle", 1440, 1000),
        ("vitrine-galeries.png", "https://www.artworksdigital.fr/galeries", 1440, 900),
    ],
    "veliora": [
        ("vitrine-home.png", "https://veliora.osc-fr1.scalingo.io/", 1440, 900),
        ("vitrine-offre.png", "https://veliora.osc-fr1.scalingo.io/offre", 1440, 1000),
        ("crm-auth.png", "https://veliora.osc-fr1.scalingo.io/crm/auth", 1440, 900),
    ],
    "ivt": [
        ("vitrine-home.png", "https://insidevietnamtravel.osc-fr1.scalingo.io/", 1440, 900),
        ("guide-hanoi.png", "https://insidevietnamtravel.osc-fr1.scalingo.io/vietnam/hanoi", 1440, 1000),
        ("vitrine-blog.png", "https://insidevietnamtravel.osc-fr1.scalingo.io/blog", 1440, 1000),
    ],
}

ADMIN_SNAPSHOT = Path(__file__).resolve().parent / "admin_analytics_snapshot.html"


def capture_project(page, out_dir: Path, shots: list) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, url, width, height in shots:
        print(f"  {url} -> {name}")
        page.set_viewport_size({"width": width, "height": height})
        page.goto(url, wait_until="networkidle", timeout=90000)
        page.wait_for_timeout(2500)
        page.screenshot(path=str(out_dir / name), full_page=False)


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

        for project, shots in SHOTS.items():
            print(f"Capturing {project}...")
            capture_project(page, ROOT / project, shots)

        if ADMIN_SNAPSHOT.exists():
            print("Capturing artworks admin-analytics.png")
            page.set_viewport_size({"width": 1440, "height": 900})
            page.goto(ADMIN_SNAPSHOT.as_uri(), wait_until="load", timeout=30000)
            page.wait_for_timeout(500)
            page.screenshot(path=str(ROOT / "artworks" / "admin-analytics.png"), full_page=False)

        browser.close()

    for project in SHOTS:
        files = list((ROOT / project).glob("*.png"))
        print(f"{project}: {len(files)} images")


if __name__ == "__main__":
    main()
