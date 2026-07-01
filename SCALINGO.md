# Déploiement Scalingo — MVPForge

App unique : **mvpforge** (région `osc-fr1`), autodeploy depuis GitHub `Colin-tech-VS/MVPForge`.

## Prérequis

1. Repo GitHub poussé (branche `main`)
2. Projet Supabase créé — voir [supabase/README.md](supabase/README.md)
3. CLI Scalingo (optionnel) : [releases Scalingo](https://github.com/Scalingo/cli/releases)

## 1. Créer l'app Scalingo

```bash
scalingo --region osc-fr1 create mvpforge --remote scalingo
```

## 2. Lier GitHub (autodeploy)

GitHub doit déjà être connecté à Scalingo (`scalingo integrations`).

```bash
scalingo --region osc-fr1 --app mvpforge integration-link-create \
  --branch main \
  --auto-deploy \
  https://github.com/Colin-tech-VS/MVPForge
```

Vérifier :

```bash
scalingo --region osc-fr1 --app mvpforge integration-link
```

## 3. Variables d'environnement

```bash
scalingo --region osc-fr1 --app mvpforge env-set \
  SECRET_KEY="<générer-une-clé-forte>" \
  SEED_CATALOG=1 \
  AUTH_BACKEND=supabase \
  DATABASE_URL="postgresql://postgres.<REF>:<PASSWORD>@aws-0-eu-central-1.pooler.supabase.com:6543/postgres" \
  SUPABASE_URL="https://<REF>.supabase.co" \
  SUPABASE_KEY="<service-role-ou-anon-key>"
```

Optionnel (Stripe) :

```bash
scalingo --region osc-fr1 --app mvpforge env-set \
  STRIPE_SECRET_KEY="..." \
  STRIPE_PUBLISHABLE_KEY="..." \
  STRIPE_WEBHOOK_SECRET="..."
```

> Utilisez le **connection pooler** Supabase (port **6543**) sur Scalingo pour éviter l'épuisement des connexions Postgres.

## 4. Schéma base de données

Au premier boot, Flask exécute `upgrade_database()` + `db.create_all()`.

Vous pouvez aussi appliquer le schéma manuellement dans Supabase → SQL Editor :

`supabase/schema.sql`

## 5. Premier déploiement

Après `integration-link-create` avec `--auto-deploy`, chaque push sur `main` redéploie.

Déploiement manuel :

```bash
scalingo --region osc-fr1 --app mvpforge integration-link-manual-deploy main
```

## 6. Logs & vérif

```bash
scalingo --region osc-fr1 --app mvpforge logs -f
scalingo --region osc-fr1 --app mvpforge open
```

URL par défaut : `https://mvpforge.osc-fr1.scalingo.io`

## Fichiers de déploiement

| Fichier | Rôle |
|---------|------|
| `Procfile` | Gunicorn `server:app` |
| `runtime.txt` | Python 3.12.6 |
| `requirements.txt` | Flask + psycopg2 + gunicorn |

## Notes

- **Uploads images** : stockés sur le disque éphémère Scalingo (`instance/uploads/`). Les images seed du catalogue sont recopiées depuis `static/seed/` à chaque boot si `SEED_CATALOG=1`.
- **Auth locale vs Supabase** : en prod, `AUTH_BACKEND=supabase` est recommandé.
- **SQLite** : ne pas utiliser en production Scalingo (données perdues au redeploy).
