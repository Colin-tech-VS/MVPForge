"""Transfert de propriété d'un dépôt GitHub via l'API.

Le vendeur fournit l'URL du dépôt + un token GitHub disposant du droit admin
sur ce dépôt (Personal Access Token, scope `repo`). L'app déclenche alors le
transfert vers le compte de l'acheteur. À défaut, le transfert reste manuel
(guidé par la checklist de passation).
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

_REPO_RE = re.compile(r"github\.com[/:]([\w.-]+)/([\w.-]+?)(?:\.git)?/?$")


def github_transfer_available() -> bool:
    """Le mécanisme existe toujours ; l'activation dépend du token vendeur."""
    return True


def parse_repo(repo_url: str) -> tuple[str, str] | None:
    if not repo_url:
        return None
    match = _REPO_RE.search(repo_url.strip())
    if not match:
        return None
    return match.group(1), match.group(2)


def transfer_repo(repo_url: str, new_owner: str, token: str) -> tuple[bool, str]:
    parsed = parse_repo(repo_url)
    if not parsed:
        return False, "URL de dépôt GitHub invalide."
    owner, repo = parsed

    req = urllib.request.Request(
        f"https://api.github.com/repos/{owner}/{repo}/transfer",
        data=json.dumps({"new_owner": new_owner}).encode(),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "MVPForge",
        },
    )
    try:
        urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = json.loads(exc.read().decode()).get("message", "")
        except Exception:
            pass
        if exc.code in (401, 403):
            return False, "Token GitHub refusé ou droits insuffisants sur le dépôt."
        if exc.code == 404:
            return False, "Dépôt introuvable (ou token sans accès)."
        return False, f"Échec du transfert GitHub : {detail or exc.code}."
    except Exception:
        return False, "Impossible de contacter GitHub. Réessayez plus tard."

    return True, (
        f"Transfert du dépôt {owner}/{repo} vers « {new_owner} » initié. "
        "L'acheteur doit accepter l'invitation GitHub."
    )
