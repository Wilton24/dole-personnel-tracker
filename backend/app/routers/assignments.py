from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user
from ..utils import get_personnel_status

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.get("/", response_model=list[schemas.AssignmentOut])
def list_assignments(
    project_id: int | None = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = db.query(models.Assignment)
    if project_id is not None:
        query = query.filter(models.Assignment.project_id == project_id)
    return query.all()


@router.post("/", response_model=schemas.AssignmentOut)
def create_assignment(
    payload: schemas.AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = db.query(models.Project).filter(models.Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    personnel = (
        db.query(models.Personnel).filter(models.Personnel.id == payload.personnel_id).first()
    )
    if not personnel:
        raise HTTPException(404, "Personnel not found")

    role = db.query(models.Role).filter(models.Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(400, "Invalid role_id")

    # Prevent assigning the same person to the same project twice
    duplicate = (
        db.query(models.Assignment)
        .filter(
            models.Assignment.project_id == payload.project_id,
            models.Assignment.personnel_id == payload.personnel_id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(400, "This personnel is already assigned to this project")

    current_status = get_personnel_status(db, personnel.id)
    is_override = False

    if current_status == "Engaged":
        if not current_user.is_admin:
            raise HTTPException(
                409,
                f"{personnel.name} is already engaged on another ongoing project. "
                "Only an admin can override this.",
            )
        if not payload.override_reason or not payload.override_reason.strip():
            raise HTTPException(
                400,
                "An override reason is required to assign personnel who are already engaged.",
            )
        is_override = True

    assignment = models.Assignment(
        project_id=payload.project_id,
        personnel_id=payload.personnel_id,
        role_id=payload.role_id,
        is_override=is_override,
        override_reason=payload.override_reason if is_override else None,
        override_by=current_user.id if is_override else None,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.delete("/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(404, "Assignment not found")
    db.delete(assignment)
    db.commit()
    return {"detail": "Unassigned"}
