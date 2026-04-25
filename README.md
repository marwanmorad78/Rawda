# Al Rawda Center

Professional Django + PostgreSQL website scaffold for a grocery store that showcases dynamic categories, products, offers, and business information, with a hidden manager-only dashboard.

## Overview

Al Rawda Center is a server-rendered Django storefront built for a grocery business selling vegetables, fruits, juices, canned food, legumes, and frozen products. The public site emphasizes product discovery, promotions, clear pricing, and store contact details, while the private manager area handles category, product, promotion, and content management.

## Architecture Summary

- Backend: Django 5.x
- Database: PostgreSQL
- Frontend: Django templates with reusable partials and responsive custom CSS
- Admin authentication: Django auth users with `is_staff=True`
- Private admin path: configurable via `ADMIN_URL` in `.env`
- Image handling: Django `ImageField` for category, product, and promotion media

This architecture is the best fit because the site is primarily content-driven, does not require customer accounts or a cart, and benefits from low maintenance and strong SEO.

## Key Features

- Dynamic categories managed by the store manager
- Product detail pages with image, price, description, and availability
- Homepage offer cards / promotions section
- About / Contact page with editable store details
- Hidden manager dashboard for CRUD operations
- PostgreSQL-ready schema and SQL seed files
- `uv` + local `.venv` workflow

## Page Map

- `/` Home page
- `/categories/<slug>/` Category page
- `/products/<slug>/` Product detail page
- `/about/` About / Contact page
- `/<ADMIN_URL>login/` Hidden manager login
- `/<ADMIN_URL>` Dashboard home
- `/<ADMIN_URL>categories/` Category management
- `/<ADMIN_URL>products/` Product management
- `/<ADMIN_URL>promotions/` Promotions management
- `/<ADMIN_URL>settings/` Store settings management

## UI/UX Direction

- Fresh grocery style with green primary tones and warm fruit-inspired accents
- Responsive layout for mobile, tablet, and desktop
- Large category cards, clean product cards, and clear price hierarchy
- Simple navigation with private manager links excluded from public pages

## Database Design

Core entities:
- `auth_user` via Django auth
- `core_sitesettings`
- `core_businesshour`
- `core_sociallink`
- `catalog_category`
- `catalog_product`
- `catalog_productimage`
- `promotions_promotion`

See [docs/implementation_plan.md](docs/implementation_plan.md), [sql/001_schema.sql](sql/001_schema.sql), and [sql/002_seed.sql](sql/002_seed.sql).

## Development Roadmap

1. Phase 1: configure PostgreSQL, settings, and models
2. Phase 2: build public storefront templates
3. Phase 3: add hidden manager dashboard and CRUD forms
4. Phase 4: polish, test, and deploy

## `uv` Setup

### Windows
```powershell
uv venv .venv
.venv\Scripts\activate
uv sync
Copy-Item .env.example .env
uv run python src/manage.py migrate
uv run python src/manage.py createsuperuser
uv run python src/manage.py runserver
```

### Linux/macOS
```bash
uv venv .venv
source .venv/bin/activate
uv sync
cp .env.example .env
uv run python src/manage.py migrate
uv run python src/manage.py createsuperuser
uv run python src/manage.py runserver
```

### Useful Commands
```bash
uv add Django psycopg[binary] Pillow python-dotenv whitenoise
uv add --dev ruff django-browser-reload
uv sync
uv run python src/manage.py makemigrations
uv run python src/manage.py migrate
uv run python src/manage.py collectstatic --noinput
```

## Deploy On Render

This repo now includes a [`render.yaml`](render.yaml) Blueprint and [`build.sh`](build.sh) build script for Render.

### What the Render setup assumes

- Web service runtime: Python
- App server: `gunicorn`
- Database: Render Postgres via `DATABASE_URL`
- Static files: WhiteNoise
- Uploaded media: a persistent disk mounted at `/opt/render/project/src/src/media`

### Important pricing note

This Blueprint is set up for a stable deployment with persistent uploaded images:

- Web service plan: `starter`
- Postgres plan: `basic-256mb`

If you switch the web service to Render's free plan, uploaded media will not persist because free web services do not support persistent disks.

### Free test-only alternative

If you want a disposable test deployment instead of the stable paid setup, use [`render.free-test.yaml`](render.free-test.yaml) instead of [`render.yaml`](render.yaml).

- Web service plan: `free`
- Database plan: `free`
- No persistent disk
- Best for temporary previews and testing only

Important limitations of the free test setup:

- Uploaded files in `src/media/` are not persisted across redeploys or restarts.
- Free Render Postgres expires 30 days after creation.
- Free web services do not include Render Shell access, so creating a Django superuser is less convenient than on the paid setup.

### Deploy steps

1. Push this project to GitHub, GitLab, or Bitbucket.
2. In Render, open Blueprints and create a new Blueprint instance from your repo.
3. Review `render.yaml` before the first deploy, especially the `region`, service names, and plans.
4. Apply the Blueprint and wait for the initial deploy to finish.
5. Open the Render Shell for the web service and create an admin user:

```bash
uv run python src/manage.py createsuperuser
```

### Custom domain setup

When you add a custom domain in Render, also set these environment variables on the web service:

```env
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

Render automatically provides `RENDER_EXTERNAL_HOSTNAME` and `RENDER_EXTERNAL_URL`, so the default `.onrender.com` domain works without extra host configuration.

### Local Database Modes

- Production / preferred setup: `DATABASE_ENGINE=postgresql`
- Quick local startup fallback: `DATABASE_ENGINE=sqlite`

Example SQLite local `.env` values:

```env
DATABASE_ENGINE=sqlite
```

Example PostgreSQL local `.env` values:

```env
DATABASE_ENGINE=postgresql
DATABASE_NAME=al_rawda_center
DATABASE_USER=postgres
DATABASE_PASSWORD=your_real_password
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432
```

## Important Notes

- No customer accounts or public authentication
- No shopping cart in the initial version
- Dynamic category and product management is central
- Admin area is private and omitted from public navigation
- Codebase is intentionally maintainable and ready for future DRF expansion

## Optional Future Enhancements

- Search and product filtering
- WhatsApp order button
- Arabic / English multilingual support
- Seasonal campaign scheduling
- Inventory tracking
- Delivery request integration
