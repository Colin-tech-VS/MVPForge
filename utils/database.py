from sqlalchemy import inspect, text

from extensions import db

MVP_PROJECT_COLUMNS = {
    "is_online": "BOOLEAN DEFAULT 0",
    "monthly_visitors": "INTEGER",
    "monthly_revenue": "INTEGER",
    "launch_date": "DATE",
    "site_url": "VARCHAR(500)",
    "github_url": "VARCHAR(500)",
    "monetization": "VARCHAR(500)",
    "traffic_source": "TEXT",
    "strengths": "TEXT",
    "weaknesses": "TEXT",
    "resale_reason": "TEXT",
    "page_views": "INTEGER",
    "sessions_count": "INTEGER",
    "bounce_rate": "REAL",
    "avg_duration": "VARCHAR(20)",
    "profile_views": "INTEGER",
    "engagement_count": "INTEGER",
    "conversion_count": "INTEGER",
    "conversion_rate": "REAL",
    "analytics_period_days": "INTEGER",
    "analytics_extra": "TEXT",
    "listing_fee_paid": "BOOLEAN DEFAULT 0",
    "listing_fee_paid_at": "DATETIME",
    "listing_fee_amount_cents": "INTEGER",
    "stripe_checkout_session_id": "VARCHAR(255)",
    "buyer_id": "VARCHAR(36)",
    "sold_at": "DATETIME",
}


USER_COLUMNS = {
    "phone": "VARCHAR(30)",
    "company": "VARCHAR(120)",
    "website": "VARCHAR(500)",
    "location": "VARCHAR(120)",
    "bio": "TEXT",
    "updated_at": "DATETIME",
}


def _column_type(sqlite_type: str) -> str:
    if db.engine.dialect.name != "postgresql":
        return sqlite_type
    mapping = {
        "BOOLEAN DEFAULT 0": "BOOLEAN DEFAULT FALSE",
        "BOOLEAN DEFAULT 1": "BOOLEAN DEFAULT TRUE",
        "DATETIME": "TIMESTAMP WITH TIME ZONE",
        "REAL": "DOUBLE PRECISION",
    }
    return mapping.get(sqlite_type, sqlite_type)


def upgrade_database() -> None:
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    if "users" in tables:
        existing = {c["name"] for c in inspector.get_columns("users")}
        for col, col_type in USER_COLUMNS.items():
            if col not in existing:
                db.session.execute(
                    text(f"ALTER TABLE users ADD COLUMN {col} {_column_type(col_type)}")
                )
        db.session.commit()

    if "mvp_projects" in tables:
        existing = {c["name"] for c in inspector.get_columns("mvp_projects")}
        for col, col_type in MVP_PROJECT_COLUMNS.items():
            if col not in existing:
                db.session.execute(
                    text(
                        f"ALTER TABLE mvp_projects ADD COLUMN {col} {_column_type(col_type)}"
                    )
                )
        db.session.commit()

    db.create_all()
