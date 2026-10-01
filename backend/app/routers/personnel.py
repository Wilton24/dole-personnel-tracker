from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user, require_admin
from ..utils import serialize_personnel

router = APIRouter(prefix="/personnel", tags=["personnel"])


@router.get("/", response_model=list[schemas.PersonnelOut])
def list_personnel(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    all_personnel = db.query(models.Personnel).all()
    return [serialize_personnel(db, p) for p in all_personnel]


@router.get("/{personnel_id}", response_model=schemas.PersonnelOut)
def get_personnel(personnel_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    person = db.query(models.Personnel).filter(models.Personnel.id == personnel_id).first()
    if not person:
        raise HTTPException(404, "Personnel not found")
    return serialize_personnel(db, person)


@router.post("/", response_model=schemas.PersonnelOut)
def create_personnel(
    payload: schemas.PersonnelCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    role = db.query(models.Role).filter(models.Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(400, "Invalid role_id")
    person = models.Personnel(**payload.model_dump())
    db.add(person)
    db.commit()
    db.refresh(person)
    return serialize_personnel(db, person)


@router.delete("/{personnel_id}")
def delete_personnel(
    personnel_id: int,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    person = db.query(models.Personnel).filter(models.Personnel.id == personnel_id).first()
    if not person:
        raise HTTPException(404, "Personnel not found")
    db.delete(person)
    db.commit()
    return {"detail": "Deleted"}
