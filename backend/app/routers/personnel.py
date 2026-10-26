from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload, selectinload

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user, require_admin

router = APIRouter(prefix="/personnel", tags=["personnel"])

# Fields that exist as NOT NULL columns: can't be blanked out via update
NOT_NULLABLE = {"first_name", "last_name", "role_id", "is_active"}

# Load role + assignments (+ each assignment's project and role) up front in a
# fixed number of queries, instead of one lazy query per person (the N+1 problem).
LOAD_OPTIONS = (
    joinedload(models.Personnel.role),
    selectinload(models.Personnel.assignments).options(
        joinedload(models.Assignment.project),
        joinedload(models.Assignment.role),
    ),
)


def _get_or_404(db: Session, personnel_id: int) -> models.Personnel:
    person = (
        db.query(models.Personnel)
        .options(*LOAD_OPTIONS)
        .filter(models.Personnel.id == personnel_id)
        .first()
    )
    if not person:
        raise HTTPException(404, "Personnel not found")
    return person


def _ensure_control_number_free(
    db: Session, control_number: Optional[str], exclude_id: Optional[int] = None
):
    if not control_number:
        return
    query = db.query(models.Personnel).filter(
        models.Personnel.control_number == control_number
    )
    if exclude_id is not None:
        query = query.filter(models.Personnel.id != exclude_id)
    if query.first():
        raise HTTPException(
            409, f"Control number {control_number} is already used by another personnel"
        )


@router.get("/", response_model=list[schemas.PersonnelOut])
def list_personnel(
    search: Optional[str] = None,
    role_id: Optional[int] = None,
    availability: Optional[str] = None,  # "Available" | "Engaged"
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = db.query(models.Personnel).options(*LOAD_OPTIONS)

    if not include_inactive:
        query = query.filter(models.Personnel.is_active.is_(True))
    if role_id is not None:
        query = query.filter(models.Personnel.role_id == role_id)
    if search and search.strip():
        like = f"%{search.strip()}%"
        query = query.filter(
            or_(
                models.Personnel.first_name.ilike(like),
                models.Personnel.last_name.ilike(like),
                models.Personnel.control_number.ilike(like),
                models.Personnel.certificate_number.ilike(like),
            )
        )

    people = query.order_by(models.Personnel.last_name,
                            models.Personnel.first_name).all()

    # Availability is computed from project dates/status, so it's filtered in Python
    if availability:
        people = [p for p in people if p.availability_status == availability]
    return people


@router.get("/{personnel_id}", response_model=schemas.PersonnelOut)
def get_personnel(
    personnel_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
):
    return _get_or_404(db, personnel_id)


@router.post("/", response_model=schemas.PersonnelOut)
def create_personnel(
    payload: schemas.PersonnelCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    if not db.query(models.Role).filter(models.Role.id == payload.role_id).first():
        raise HTTPException(400, "Invalid role_id")
    _ensure_control_number_free(db, payload.control_number)

    person = models.Personnel(**payload.model_dump())
    db.add(person)
    db.commit()
    return _get_or_404(db, person.id)


@router.put("/{personnel_id}", response_model=schemas.PersonnelOut)
def update_personnel(
    personnel_id: int,
    payload: schemas.PersonnelUpdate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    person = _get_or_404(db, personnel_id)
    data = payload.model_dump(exclude_unset=True)

    for field in NOT_NULLABLE:
        if field in data and data[field] is None:
            raise HTTPException(422, f"{field} cannot be empty")

    if "role_id" in data and not db.query(models.Role).filter(
        models.Role.id == data["role_id"]
    ).first():
        raise HTTPException(400, "Invalid role_id")
    if "control_number" in data:
        _ensure_control_number_free(
            db, data["control_number"], exclude_id=person.id)

    for field, value in data.items():
        setattr(person, field, value)
    db.commit()
    return _get_or_404(db, personnel_id)


@router.delete("/{personnel_id}")
def delete_personnel(
    personnel_id: int,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    person = _get_or_404(db, personnel_id)
    if person.assignments:
        raise HTTPException(
            409,
            "This personnel has project history and can't be deleted. "
            "Set is_active to false to deactivate them instead.",
        )
    db.delete(person)
    db.commit()
    return {"detail": "Deleted"}
