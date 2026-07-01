-- MVPForge — schéma PostgreSQL (Supabase)
-- Le schéma est aussi créé automatiquement au boot via SQLAlchemy (db.create_all).
-- Exécuter ce fichier dans Supabase → SQL Editor si vous préférez initialiser à la main.

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(120),
    phone VARCHAR(30),
    company VARCHAR(120),
    website VARCHAR(500),
    location VARCHAR(120),
    bio TEXT,
    password_hash VARCHAR(255),
    external_id VARCHAR(255) UNIQUE,
    auth_provider VARCHAR(20) NOT NULL DEFAULT 'local',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
CREATE INDEX IF NOT EXISTS ix_users_external_id ON users (external_id);

CREATE TABLE IF NOT EXISTS mvp_projects (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users (id),
    title VARCHAR(120) NOT NULL,
    tagline VARCHAR(255) NOT NULL,
    description TEXT,
    price INTEGER NOT NULL,
    category VARCHAR(80) NOT NULL,
    stack VARCHAR(500) NOT NULL DEFAULT '',
    color VARCHAR(7) NOT NULL DEFAULT '#1A6B52',
    status VARCHAR(20) NOT NULL DEFAULT 'published',
    buyer_id VARCHAR(36) REFERENCES users (id),
    sold_at TIMESTAMP WITH TIME ZONE,
    is_online BOOLEAN NOT NULL DEFAULT FALSE,
    monthly_visitors INTEGER,
    monthly_revenue INTEGER,
    launch_date DATE,
    site_url VARCHAR(500),
    github_url VARCHAR(500),
    monetization VARCHAR(500) DEFAULT '',
    traffic_source TEXT,
    strengths TEXT,
    weaknesses TEXT,
    resale_reason TEXT,
    page_views INTEGER,
    sessions_count INTEGER,
    bounce_rate DOUBLE PRECISION,
    avg_duration VARCHAR(20),
    profile_views INTEGER,
    engagement_count INTEGER,
    conversion_count INTEGER,
    conversion_rate DOUBLE PRECISION,
    analytics_period_days INTEGER,
    analytics_extra TEXT,
    listing_fee_paid BOOLEAN NOT NULL DEFAULT FALSE,
    listing_fee_paid_at TIMESTAMP WITH TIME ZONE,
    listing_fee_amount_cents INTEGER,
    stripe_checkout_session_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_mvp_projects_user_id ON mvp_projects (user_id);
CREATE INDEX IF NOT EXISTS ix_mvp_projects_category ON mvp_projects (category);
CREATE INDEX IF NOT EXISTS ix_mvp_projects_status ON mvp_projects (status);
CREATE INDEX IF NOT EXISTS ix_mvp_projects_buyer_id ON mvp_projects (buyer_id);

CREATE TABLE IF NOT EXISTS mvp_images (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL REFERENCES mvp_projects (id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_mvp_images_project_id ON mvp_images (project_id);

CREATE TABLE IF NOT EXISTS mvp_purchases (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL REFERENCES mvp_projects (id),
    buyer_id VARCHAR(36) NOT NULL REFERENCES users (id),
    amount_cents INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    stripe_checkout_session_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    paid_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS ix_mvp_purchases_project_id ON mvp_purchases (project_id);
CREATE INDEX IF NOT EXISTS ix_mvp_purchases_buyer_id ON mvp_purchases (buyer_id);
CREATE INDEX IF NOT EXISTS ix_mvp_purchases_status ON mvp_purchases (status);
