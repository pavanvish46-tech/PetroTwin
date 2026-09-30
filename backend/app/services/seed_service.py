from sqlalchemy.orm import Session
from backend.app.core.security import hash_password
from backend.app.db.session import SessionLocal
from backend.app.models.models import User

DEMO_USERS = [
    ("admin", "admin@sih26120.local", "Admin@26120", "national_admin"),
    ("engineer", "engineer@sih26120.local", "Engineer@26120", "engineer"),
    ("operator", "operator@sih26120.local", "Operator@26120", "operator"),
]

def seed_database():
    db: Session = SessionLocal()
    try:
        for username, email, password, role in DEMO_USERS:
            existing = db.query(User).filter(User.username == username).first()
            if not existing:
                db.add(User(username=username, email=email, password_hash=hash_password(password), role=role))
        db.commit()
    finally:
        db.close()
