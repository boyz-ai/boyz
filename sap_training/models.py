"""Data models for SAP training management."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List


def _sorted_enrollments(enrolled: List[str]) -> List[str]:
    return sorted(dict.fromkeys(enrolled))


@dataclass
class Course:
    code: str
    title: str
    level: str
    duration_days: int
    description: str

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["code"] = self.code.upper()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "Course":
        return cls(
            code=data["code"],
            title=data["title"],
            level=data.get("level", ""),
            duration_days=int(data.get("duration_days", 0)),
            description=data.get("description", ""),
        )


@dataclass
class Session:
    session_id: str
    course_code: str
    start_date: str
    instructor: str
    location: str
    capacity: int
    enrolled: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["session_id"] = self.session_id.upper()
        data["course_code"] = self.course_code.upper()
        data["enrolled"] = _sorted_enrollments(self.enrolled)
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "Session":
        return cls(
            session_id=data["session_id"],
            course_code=data["course_code"],
            start_date=data["start_date"],
            instructor=data.get("instructor", ""),
            location=data.get("location", ""),
            capacity=int(data.get("capacity", 0)),
            enrolled=list(data.get("enrolled", [])),
        )


@dataclass
class Participant:
    employee_id: str
    name: str
    department: str

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["employee_id"] = self.employee_id.upper()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "Participant":
        return cls(
            employee_id=data["employee_id"],
            name=data.get("name", ""),
            department=data.get("department", ""),
        )
