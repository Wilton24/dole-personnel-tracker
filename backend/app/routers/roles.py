from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import require_admin

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=list[schemas.RoleOut])
def list_roles(db: Session = Depends(get_db)):
    return db.query(models.Role).all()


@router.post("/", response_model=schemas.RoleOut)
def create_role(
    payload: schemas.RoleCreate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    existing = db.query(models.Role).filter(models.Role.name == payload.name).first()
    if existing:
        raise HTTPException(400, "Role already exists")
    role = models.Role(name=payload.name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role
