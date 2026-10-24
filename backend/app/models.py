from datetime import date

from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    personnel = relationship("Personnel", back_populates="role")


class Personnel(Base):
    __tablename__ = "personnel"

    id = Column(Integer, primary_key=True, index=True)

    # Name
    first_name = Column(String, nullable=False)
    middle_initial = Column(String(1), nullable=True)
    last_name = Column(String, nullable=False)
    extension = Column(String(10), nullable=True)  # Jr., Sr., III, ...

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    # Contact
    contact_number = Column(String, nullable=True)
    email = Column(String, nullable=True)

    # Credentials / training
    control_number = Column(String, unique=True, index=True, nullable=True)
    certificate_number = Column(String, nullable=True)
    date_of_training = Column(Date, nullable=True)
    training_valid_until = Column(Date, nullable=True)

    notes = Column(Text, nullable=True)

    # Soft-delete flag: people with project history are deactivated, not deleted
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    role = relationship("Role", back_populates="personnel")
    assignments = relationship("Assignment", back_populates="personnel")

    # ----- Computed (not stored) -----
    @property
    def full_name(self) -> str:
        middle = f" {self.middle_initial}." if self.middle_initial else ""
        ext = f" {self.extension}" if self.extension else ""
        return f"{self.first_name}{middle} {self.last_name}{ext}"

    @property
    def availability_status(self) -> str:
        """Engaged while any of their projects is still current, else Available."""
        if any(a.project.is_current for a in self.assignments):
            return "Engaged"
        return "Available"

    @property
    def projects(self) -> list[dict]:
        """Project history, newest first (previous, current, ...)."""
        history = []
        for a in sorted(
            self.assignments, key=lambda a: a.project.start_date, reverse=True
        ):
            p = a.project
            history.append(
                {
                    "assignment_id": a.id,
                    "project_id": p.id,
                    "project_name": p.name,
                    "project_status": p.status,
                    "start_date": p.start_date,
                    "end_date": p.end_date,
                    "role": a.role.name,
                    "is_current": p.is_current,
                    "is_override": a.is_override,
                }
            )
        return history


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    start_date = Column(Date, nullable=False)
    duration_days = Column(Integer, nullable=True)
    end_date = Column(Date, nullable=True)
    # Ongoing | Completed
    status = Column(String, nullable=False, default="Ongoing")

    assignments = relationship(
        "Assignment", back_populates="project", cascade="all, delete-orphan"
    )

    @property
    def is_current(self) -> bool:
        """A project keeps its people engaged while it is Ongoing AND
        its End Date hasn't passed yet (no End Date = no cutoff)."""
        if self.status != "Ongoing":
            return False
        return self.end_date is None or self.end_date >= date.today()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    personnel_id = Column(Integer, ForeignKey("personnel.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    is_override = Column(Boolean, default=False)
    override_reason = Column(Text, nullable=True)
    override_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="assignments")
    personnel = relationship("Personnel", back_populates="assignments")
    role = relationship("Role")
