# Al Rawda Center Implementation Plan

## Project Overview

The website is a modern grocery showcase for Al Rawda Center. It helps local customers browse categories, view product details, and check store information while giving the manager a hidden dashboard to keep content current.

## Recommended Architecture

Use Django templates with PostgreSQL and Django authentication. This is the strongest fit for a content-managed grocery site because it is easier to maintain than a separate SPA, faster to launch, SEO-friendly, and well suited for manager CRUD workflows.

## Main Apps

- `apps.core`: site settings, homepage, about/contact, business hours, social links
- `apps.catalog`: categories, products, gallery images, public catalog views
- `apps.promotions`: homepage offers and scheduling
- `apps.dashboard`: hidden manager login and CRUD screens

## Database Tables

### `core_sitesettings`
- `id BIGSERIAL PRIMARY KEY`
- `store_name VARCHAR(150) NOT NULL`
- `tagline VARCHAR(255)`
- `about_text TEXT NOT NULL`
- `address TEXT NOT NULL`
- `primary_phone VARCHAR(30) NOT NULL`
- `secondary_phone VARCHAR(30)`
- `email VARCHAR(254)`
- `working_hours_summary VARCHAR(255)`
- `hero_title VARCHAR(150) NOT NULL`
- `hero_subtitle TEXT`
- `hero_cta_text VARCHAR(80)`
- `hero_cta_url VARCHAR(255)`
- `location_embed_url VARCHAR(500)`
- `is_active BOOLEAN NOT NULL DEFAULT TRUE`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`

### `core_businesshour`
- `id BIGSERIAL PRIMARY KEY`
- `site_settings_id BIGINT NOT NULL REFERENCES core_sitesettings(id) ON DELETE CASCADE`
- `day_of_week SMALLINT NOT NULL`
- `label VARCHAR(40) NOT NULL`
- `open_time TIME NULL`
- `close_time TIME NULL`
- `is_closed BOOLEAN NOT NULL DEFAULT FALSE`
- `sort_order SMALLINT NOT NULL DEFAULT 0`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`

Indexes and constraints:
- unique `(site_settings_id, day_of_week)`
- check day range `0..6`
- index `(site_settings_id, sort_order)`

### `core_sociallink`
- `id BIGSERIAL PRIMARY KEY`
- `site_settings_id BIGINT NOT NULL REFERENCES core_sitesettings(id) ON DELETE CASCADE`
- `platform VARCHAR(50) NOT NULL`
- `url VARCHAR(500) NOT NULL`
- `sort_order SMALLINT NOT NULL DEFAULT 0`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`

### `catalog_category`
- `id BIGSERIAL PRIMARY KEY`
- `name VARCHAR(120) NOT NULL`
- `slug VARCHAR(140) NOT NULL UNIQUE`
- `description TEXT`
- `display_order INTEGER NOT NULL DEFAULT 0`
- `is_active BOOLEAN NOT NULL DEFAULT TRUE`
- `cover_image VARCHAR(255)`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`

### `catalog_product`
- `id BIGSERIAL PRIMARY KEY`
- `category_id BIGINT NOT NULL REFERENCES catalog_category(id) ON DELETE RESTRICT`
- `name VARCHAR(150) NOT NULL`
- `slug VARCHAR(170) NOT NULL UNIQUE`
- `short_description VARCHAR(280)`
- `description TEXT`
- `price NUMERIC(10,2) NOT NULL`
- `unit_label VARCHAR(50) NOT NULL DEFAULT 'per item'`
- `is_available BOOLEAN NOT NULL DEFAULT TRUE`
- `is_featured BOOLEAN NOT NULL DEFAULT FALSE`
- `sku VARCHAR(50)`
- `primary_image VARCHAR(255)`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`

### `catalog_productimage`
- `id BIGSERIAL PRIMARY KEY`
- `product_id BIGINT NOT NULL REFERENCES catalog_product(id) ON DELETE CASCADE`
- `image VARCHAR(255) NOT NULL`
- `alt_text VARCHAR(180)`
- `sort_order INTEGER NOT NULL DEFAULT 0`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`

### `promotions_promotion`
- `id BIGSERIAL PRIMARY KEY`
- `title VARCHAR(140) NOT NULL`
- `slug VARCHAR(160) NOT NULL UNIQUE`
- `subtitle VARCHAR(255)`
- `description TEXT`
- `badge_text VARCHAR(60)`
- `cta_text VARCHAR(60)`
- `cta_url VARCHAR(255)`
- `image VARCHAR(255)`
- `start_date DATE`
- `end_date DATE`
- `is_active BOOLEAN NOT NULL DEFAULT TRUE`
- `display_order INTEGER NOT NULL DEFAULT 0`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`

## ERD Description

- `SiteSettings 1 --- * BusinessHour`
- `SiteSettings 1 --- * SocialLink`
- `Category 1 --- * Product`
- `Product 1 --- * ProductImage`
- `Promotion` is standalone and rendered on the homepage
- `auth_user` provides manager authentication

## Security

- Django auth password hashing
- Staff-only hidden dashboard
- CSRF protection enabled
- ORM query safety against SQL injection
- Environment-based secrets and database credentials
- Upload validation handled in forms and by image fields

## Admin Panel Recommendation

Use a custom hidden dashboard for everyday content management, while also keeping Django admin enabled at `/django-admin/` for advanced support work.

## Routes

### Public
- `GET /`
- `GET /categories/<slug>/`
- `GET /products/<slug>/`
- `GET /about/`

### Private
- `GET|POST /<ADMIN_URL>login/`
- `POST /<ADMIN_URL>logout/`
- `GET /<ADMIN_URL>`
- `GET|POST /<ADMIN_URL>categories/`
- `GET|POST /<ADMIN_URL>products/`
- `GET|POST /<ADMIN_URL>promotions/`
- `GET|POST /<ADMIN_URL>settings/`

## Deployment Recommendation

- Gunicorn behind Nginx
- PostgreSQL managed separately
- Local media for development and S3-compatible storage in production
- `collectstatic` to a dedicated static directory
