"""Persistence layer for SAP training data."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .models import Course, Participant, Session


class RepositoryError(RuntimeError):
    """Raised when repository operations fail."""


class TrainingRepository:
    """Simple JSON backed storage for SAP training programs."""

    def __init__(self, db_path: Path | str = "sap_training_data.json") -> None:
        self.db_path = Path(db_path)
        self._data = {"courses": [], "sessions": [], "participants": []}
        if self.db_path.exists():
            self._data.update(json.loads(self.db_path.read_text()))

    # ------------------------------------------------------------------
    # Helpers
    def _write(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False))

    def _find(self, collection: str, key: str, value: str) -> Optional[Dict]:
        value = value.upper()
        for item in self._data[collection]:
            if item[key].upper() == value:
                return item
        return None

    # ------------------------------------------------------------------
    # Courses
    def list_courses(self) -> List[Course]:
        return [Course.from_dict(item) for item in self._data["courses"]]

    def add_course(self, course: Course) -> Course:
        if self._find("courses", "code", course.code):
            raise RepositoryError(f"Course {course.code} already exists")
        self._data["courses"].append(course.to_dict())
        self._write()
        return course

    # ------------------------------------------------------------------
    # Participants
    def list_participants(self) -> List[Participant]:
        return [Participant.from_dict(item) for item in self._data["participants"]]

    def add_participant(self, participant: Participant) -> Participant:
        if self._find("participants", "employee_id", participant.employee_id):
            raise RepositoryError(f"Participant {participant.employee_id} already exists")
        self._data["participants"].append(participant.to_dict())
        self._write()
        return participant

    # ------------------------------------------------------------------
    # Sessions
    def list_sessions(self) -> List[Session]:
        return [Session.from_dict(item) for item in self._data["sessions"]]

    def schedule_session(self, session: Session) -> Session:
        if not self._find("courses", "code", session.course_code):
            raise RepositoryError(f"Course {session.course_code} does not exist")
        if self._find("sessions", "session_id", session.session_id):
            raise RepositoryError(f"Session {session.session_id} already exists")
        self._data["sessions"].append(session.to_dict())
        self._write()
        return session

    def enroll_participant(self, session_id: str, employee_id: str) -> Session:
        session = self._find("sessions", "session_id", session_id)
        if not session:
            raise RepositoryError(f"Session {session_id} not found")
        participant = self._find("participants", "employee_id", employee_id)
        if not participant:
            raise RepositoryError(f"Participant {employee_id} not found")
        enrolled: List[str] = session.setdefault("enrolled", [])
        employee_id = participant["employee_id"]
        if employee_id in enrolled:
            return Session.from_dict(session)
        if len(enrolled) >= int(session.get("capacity", 0)):
            raise RepositoryError(
                f"Session {session_id} is at capacity ({session['capacity']})"
            )
        enrolled.append(employee_id)
        enrolled.sort()
        self._write()
        return Session.from_dict(session)

    # ------------------------------------------------------------------
    def generate_report(self) -> List[Dict[str, str]]:
        participants = {p["employee_id"]: p for p in self._data["participants"]}
        courses = {c["code"]: c for c in self._data["courses"]}
        report: List[Dict[str, str]] = []
        for session in self._data["sessions"]:
            enrolled = session.get("enrolled", [])
            course = courses.get(session["course_code"], {})
            report.append(
                {
                    "session_id": session["session_id"],
                    "course": f"{session['course_code']} - {course.get('title', '')}",
                    "start_date": session["start_date"],
                    "location": session["location"],
                    "instructor": session["instructor"],
                    "capacity": str(session["capacity"]),
                    "enrolled_count": str(len(enrolled)),
                    "participants": ", ".join(
                        participants[emp]["name"] for emp in enrolled if emp in participants
                    ),
                }
            )
        return report

    def import_seed_data(
        self,
        courses: Iterable[Course],
        participants: Iterable[Participant],
        sessions: Iterable[Session],
    ) -> None:
        self._data["courses"] = [c.to_dict() for c in courses]
        self._data["participants"] = [p.to_dict() for p in participants]
        self._data["sessions"] = [s.to_dict() for s in sessions]
        self._write()
