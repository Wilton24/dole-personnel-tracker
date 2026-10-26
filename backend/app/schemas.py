from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------- Roles ----------
class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class RoleOut(RoleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Personnel ----------
class _PersonnelFields(BaseModel):
    """Shared cleanup: trim strings and treat blank strings as 'not provided'."""

    @field_validator("*", mode="before")
    @classmethod
    def blank_to_none(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v


class PersonnelBase(_PersonnelFields):
    first_name: str
    middle_initial: Optional[str] = Field(default=None, max_length=1)
    last_name: str
    extension: Optional[str] = Field(
        default=None, max_length=10)  # Jr., Sr., III
    role_id: int
    contact_number: Optional[str] = None
    email: Optional[str] = None
    control_number: Optional[str] = None
    certificate_number: Optional[str] = None
    date_of_training: Optional[date] = None
    training_valid_until: Optional[date] = None
    notes: Optional[str] = None
    is_active: bool = True

    @field_validator("middle_initial", mode="before")
    @classmethod
    def normalize_middle_initial(cls, v):
        # Accept "m", "M.", " m. " -> "M"
        if isinstance(v, str):
            v = v.strip().rstrip(".").strip().upper()
            return v or None
        return v


class PersonnelCreate(PersonnelBase):
    pass


class PersonnelUpdate(_PersonnelFields):
    first_name: Optional[str] = None
    middle_initial: Optional[str] = Field(default=None, max_length=1)
    last_name: Optional[str] = None
    extension: Optional[str] = Field(default=None, max_length=10)
    role_id: Optional[int] = None
    contact_number: Optional[str] = None
    email: Optional[str] = None
    control_number: Optional[str] = None
    certificate_number: Optional[str] = None
    date_of_training: Optional[date] = None
    training_valid_until: Optional[date] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("middle_initial", mode="before")
    @classmethod
    def normalize_middle_initial(cls, v):
        if isinstance(v, str):
            v = v.strip().rstrip(".").strip().upper()
            return v or None
        return v


class PersonnelProjectOut(BaseModel):
    """One row of a person's project history."""
    model_config = ConfigDict(from_attributes=True)
    assignment_id: int
    project_id: int
    project_name: str
    project_status: str  # stored status: Ongoing | Completed
    start_date: date
    end_date: Optional[date] = None
    role: str
    is_current: bool  # Ongoing AND end date not yet passed
    is_override: bool


class PersonnelBrief(BaseModel):
    """Lightweight version used when personnel is nested inside other responses."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    role: RoleOut


class PersonnelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    first_name: str
    middle_initial: Optional[str] = None
    last_name: str
    extension: Optional[str] = None
    full_name: str
    role: RoleOut
    contact_number: Optional[str] = None
    email: Optional[str] = None
    control_number: Optional[str] = None
    certificate_number: Optional[str] = None
    date_of_training: Optional[date] = None
    training_valid_until: Optional[date] = None
    notes: Optional[str] = None
    is_active: bool
    availability_status: str  # computed: "Available" | "Engaged"
    projects: List[PersonnelProjectOut] = []
    created_at: Optional[datetime] = None


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
    # required only if forcing an override
    override_reason: Optional[str] = None


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

    personnel: PersonnelBrief
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
