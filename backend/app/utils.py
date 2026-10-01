from sqlalchemy.orm import Session

from . import models


def get_personnel_status(db: Session, personnel_id: int) -> str:
    """A personnel is 'Engaged' if they have an assignment on a project
    that is still Ongoing. Otherwise they're 'Available'."""
    active = (
        db.query(models.Assignment)
        .join(models.Project)
        .filter(
            models.Assignment.personnel_id == personnel_id,
            models.Project.status == "Ongoing",
        )
        .first()
    )
    return "Engaged" if active else "Available"


def serialize_personnel(db: Session, personnel: models.Personnel) -> dict:
    return {
        "id": personnel.id,
        "name": personnel.name,
        "contact_number": personnel.contact_number,
        "role": personnel.role,
        "status": get_personnel_status(db, personnel.id),
    }
