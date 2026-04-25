INSERT INTO core_sitesettings (
    id,
    store_name,
    tagline,
    about_text,
    address,
    primary_phone,
    secondary_phone,
    email,
    working_hours_summary,
    hero_title,
    hero_subtitle,
    hero_cta_text,
    hero_cta_url,
    location_embed_url
) VALUES (
    1,
    'Al Rawda Center',
    'Fresh groceries and trusted daily essentials',
    'Al Rawda Center offers a carefully selected range of vegetables, fruits, juices, canned food, legumes, and frozen products for everyday family needs.',
    'Al Rawda Center, Main Market Street, Damascus',
    '+963-11-555-1000',
    '+963-944-000-111',
    'info@alrawdacenter.com',
    'Daily from 8:00 AM to 10:00 PM',
    'Fresh products for every home',
    'Discover seasonal vegetables, sweet fruits, pantry essentials, and special offers updated by our store team.',
    'Browse categories',
    '/#categories',
    'https://maps.google.com/'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO catalog_category (name, slug, description, display_order, is_active)
VALUES
    ('Vegetables', 'vegetables', 'Fresh vegetables for daily cooking.', 1, TRUE),
    ('Fruits', 'fruits', 'Seasonal and imported fruits.', 2, TRUE),
    ('Juices', 'juices', 'Refreshing packaged and chilled juices.', 3, TRUE),
    ('Canned Food', 'canned-food', 'Pantry staples and preserved foods.', 4, TRUE),
    ('Legumes', 'legumes', 'Beans, lentils, chickpeas, and more.', 5, TRUE),
    ('Frozen Products', 'frozen-products', 'Frozen vegetables, snacks, and proteins.', 6, TRUE)
ON CONFLICT (slug) DO NOTHING;

INSERT INTO promotions_promotion (
    title, slug, subtitle, description, badge_text, cta_text, cta_url, start_date, end_date, is_active, display_order
) VALUES (
    'Spring Freshness Sale',
    'spring-freshness-sale',
    'Special prices on fruits and vegetables',
    'Save on selected produce items this week while stocks last.',
    'Limited Offer',
    'Shop categories',
    '/#categories',
    CURRENT_DATE,
    CURRENT_DATE + INTERVAL '14 days',
    TRUE,
    1
) ON CONFLICT (slug) DO NOTHING;
