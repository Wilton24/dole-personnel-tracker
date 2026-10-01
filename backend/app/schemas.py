from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# ---------- Roles ----------
class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class RoleOut(RoleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Personnel ----------
class PersonnelBase(BaseModel):
    name: str
    contact_number: Optional[str] = None
    role_id: int


class PersonnelCreate(PersonnelBase):
    pass


class PersonnelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    contact_number: Optional[str] = None
    role: RoleOut
    status: str  # computed: "Available" | "Engaged"


# ---------- Projects ----------
class ProjectBase(BaseModel):
    name: str
    address: Optional[str] = None
    start_date: date
    duration_days: Optional[int] = None
    end_date: Optional[date] = None
    status: str = "Ongoing"


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    start_date: Optional[date] = None
    duration_days: Optional[int] = None
    end_date: Optional[date] = None
    status: Optional[str] = None


class ProjectOut(ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Assignments ----------
class AssignmentCreate(BaseModel):
    project_id: int
    personnel_id: int
    role_id: int
    override_reason: Optional[str] = None  # required only if forcing an override


class AssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    personnel_id: int
    role_id: int
    is_override: bool
    override_reason: Optional[str] = None
    override_by: Optional[int] = None
    created_at: datetime

    personnel: PersonnelOut
    role: RoleOut


class ProjectDetailOut(ProjectOut):
    assignments: List[AssignmentOut] = []


# ---------- Auth ----------
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    is_admin: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
