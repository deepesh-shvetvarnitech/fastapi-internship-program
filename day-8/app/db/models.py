from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Department(Base):
    __tablename__ = "department"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )

    employees: Mapped[list["Employee"]] = relationship(
        back_populates="department"
    )


class Employee(Base):
    __tablename__ = "employes"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    department_id: Mapped[int] = mapped_column(
        ForeignKey("department.id"),
        nullable=False
    )

    department: Mapped["Department"] = relationship(
        back_populates="employees"
    )

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="employee"
    )


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employes.id"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    employee: Mapped["Employee"] = relationship(
        back_populates="tasks"
    )