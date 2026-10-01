from sqlalchemy.orm import Session

from . import models
from .security import hash_password

DEFAULT_ROLES = ["Safety Officer", "First Aider"]


def seed_data(db: Session):
    # Seed roles
    for role_name in DEFAULT_ROLES:
        exists = db.query(models.Role).filter(models.Role.name == role_name).first()
        if not exists:
            db.add(models.Role(name=role_name))
    db.commit()

    # Seed default admin user (CHANGE THIS PASSWORD after first login)
    admin_exists = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin_exists:
        admin = models.User(
            username="admin",
            hashed_password=hash_password("admin123"),
            is_admin=True,
        )
        db.add(admin)
        db.commit()
        print("Seeded default admin user -> username: admin / password: admin123")
        print("CHANGE THIS PASSWORD before real use.")
