-- Built-in Django auth/session/contenttypes tables should be created via Django migrations.
-- Al Rawda Center application schema

CREATE TABLE IF NOT EXISTS core_sitesettings (
    id BIGSERIAL PRIMARY KEY,
    store_name VARCHAR(150) NOT NULL,
    tagline VARCHAR(255),
    about_text TEXT NOT NULL,
    address TEXT NOT NULL,
    primary_phone VARCHAR(30) NOT NULL,
    secondary_phone VARCHAR(30),
    email VARCHAR(254),
    working_hours_summary VARCHAR(255),
    hero_title VARCHAR(150) NOT NULL,
    hero_subtitle TEXT,
    hero_cta_text VARCHAR(80),
    hero_cta_url VARCHAR(255),
    location_embed_url VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS core_businesshour (
    id BIGSERIAL PRIMARY KEY,
    site_settings_id BIGINT NOT NULL REFERENCES core_sitesettings(id) ON DELETE CASCADE,
    day_of_week SMALLINT NOT NULL,
    label VARCHAR(40) NOT NULL,
    open_time TIME NULL,
    close_time TIME NULL,
    is_closed BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_businesshour_site_day UNIQUE (site_settings_id, day_of_week),
    CONSTRAINT chk_businesshour_day_range CHECK (day_of_week BETWEEN 0 AND 6)
);

CREATE TABLE IF NOT EXISTS core_sociallink (
    id BIGSERIAL PRIMARY KEY,
    site_settings_id BIGINT NOT NULL REFERENCES core_sitesettings(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    url VARCHAR(500) NOT NULL,
    sort_order SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS catalog_category (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    slug VARCHAR(140) NOT NULL UNIQUE,
    description TEXT,
    display_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    cover_image VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS catalog_product (
    id BIGSERIAL PRIMARY KEY,
    category_id BIGINT NOT NULL REFERENCES catalog_category(id) ON DELETE RESTRICT,
    name VARCHAR(150) NOT NULL,
    slug VARCHAR(170) NOT NULL UNIQUE,
    short_description VARCHAR(280),
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    unit_label VARCHAR(50) NOT NULL DEFAULT 'per item',
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    sku VARCHAR(50),
    primary_image VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_product_price_nonnegative CHECK (price >= 0)
);

CREATE TABLE IF NOT EXISTS catalog_productimage (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES catalog_product(id) ON DELETE CASCADE,
    image VARCHAR(255) NOT NULL,
    alt_text VARCHAR(180),
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS promotions_promotion (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(140) NOT NULL,
    slug VARCHAR(160) NOT NULL UNIQUE,
    subtitle VARCHAR(255),
    description TEXT,
    badge_text VARCHAR(60),
    cta_text VARCHAR(60),
    cta_url VARCHAR(255),
    image VARCHAR(255),
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_promotion_dates CHECK (
        end_date IS NULL OR start_date IS NULL OR end_date >= start_date
    )
);

CREATE INDEX IF NOT EXISTS idx_businesshour_site_sort
    ON core_businesshour (site_settings_id, sort_order);
CREATE INDEX IF NOT EXISTS idx_sociallink_site_sort
    ON core_sociallink (site_settings_id, sort_order);
CREATE INDEX IF NOT EXISTS idx_category_active_order
    ON catalog_category (is_active, display_order);
CREATE INDEX IF NOT EXISTS idx_product_category_available
    ON catalog_product (category_id, is_available);
CREATE INDEX IF NOT EXISTS idx_product_featured_available
    ON catalog_product (is_featured, is_available);
CREATE INDEX IF NOT EXISTS idx_productimage_product_sort
    ON catalog_productimage (product_id, sort_order);
CREATE INDEX IF NOT EXISTS idx_promotion_active_order
    ON promotions_promotion (is_active, display_order);
CREATE INDEX IF NOT EXISTS idx_promotion_dates
    ON promotions_promotion (start_date, end_date);
