# MVPForge

Marketplace pour acheter et vendre des projets MVP.

## Architecture

| Préfixe | Rôle |
|---------|------|
| `/` | Redirige vers `/site` |
| `/site` | Vitrine publique (accueil, catalogue, catégories, comment ça marche) |
| `/auth` | Connexion & inscription |
| `/compte` | Espace vendeur (dashboard, publier un MVP) |
| `/admin` | Dashboard administration (à venir) |

## Démarrage

```bash
pip install -r requirements.txt
python server.py
```

- Site : http://localhost:5000/site
- Catalogue : http://localhost:5000/site/catalogue
- Admin : http://localhost:5000/admin
- Compte vendeur : http://localhost:5000/compte

## Données

Au démarrage, les projets de démo sont supprimés et **Artworks Digital** est (re)chargé comme fiche catalogue réelle (infos issues du repo staging).

## Production (Scalingo + Supabase)

Voir [SCALINGO.md](SCALINGO.md) et [supabase/README.md](supabase/README.md).

```bash
pip install -r requirements.txt
gunicorn server:app
```

Variables : `.env.example` — Postgres Supabase (`DATABASE_URL` pooler), auth Supabase, Stripe.
