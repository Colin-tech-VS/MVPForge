# Supabase — MVPForge

## 1. Créer le projet

1. [supabase.com](https://supabase.com) → **New project**
2. Nom : `mvpforge` (ou `MVPForge`)
3. Région : **Frankfurt (eu-central-1)** (proche de Scalingo `osc-fr1`)
4. Mot de passe DB fort → à conserver

## 2. Initialiser le schéma

**Option A — automatique** : au premier démarrage sur Scalingo, l'app crée les tables via SQLAlchemy.

**Option B — manuelle** : Supabase Dashboard → **SQL Editor** → coller et exécuter `schema.sql`.

## 3. Récupérer les URLs

### Postgres (DATABASE_URL)

**Project Settings → Database → Connection string → URI**

Pooler (recommandé Scalingo) :

```
postgresql://postgres.<PROJECT_REF>:<PASSWORD>@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

Direct (migrations ponctuelles) :

```
postgresql://postgres:<PASSWORD>@db.<PROJECT_REF>.supabase.co:5432/postgres
```

### API (auth)

**Project Settings → API**

| Variable | Valeur |
|----------|--------|
| `SUPABASE_URL` | `https://<PROJECT_REF>.supabase.co` |
| `SUPABASE_KEY` | `anon` key (client) ou `service_role` (serveur) |

Pour MVPForge (inscription/connexion côté serveur), la **service role** ou **anon** fonctionne selon les RLS — par défaut le provider utilise la clé fournie dans `SUPABASE_KEY`.

## 4. Auth Supabase

Dashboard → **Authentication → Providers** :

- Email activé (défaut)
- Désactiver la confirmation e-mail en dev si besoin : **Authentication → Settings → Enable email confirmations** (off pour tests rapides)

Puis sur Scalingo :

```
AUTH_BACKEND=supabase
```

## 5. Variables Scalingo (récap)

```
DATABASE_URL=postgresql://postgres.<REF>:<PWD>@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://<REF>.supabase.co
SUPABASE_KEY=<clé>
AUTH_BACKEND=supabase
SECRET_KEY=<clé-flask>
SEED_CATALOG=1
```

## 6. CLI locale (optionnel)

```bash
npx supabase login
npx supabase link --project-ref <PROJECT_REF>
```

Fichier de référence schéma : [`schema.sql`](schema.sql)
