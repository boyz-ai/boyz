"""Command line interface for SAP training management."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from .models import Course, Participant, Session
from .repository import RepositoryError, TrainingRepository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage SAP enablement courses, participants and sessions",
    )
    parser.add_argument(
        "--db",
        default="sap_training_data.json",
        help="Path to the JSON file used for persisting state",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Courses ------------------------------------------------------------
    courses_parser = subparsers.add_parser("courses", help="Manage course catalog")
    courses_sub = courses_parser.add_subparsers(dest="courses_command", required=True)

    add_course = courses_sub.add_parser("add", help="Add a new SAP training course")
    add_course.add_argument("code")
    add_course.add_argument("title")
    add_course.add_argument("level")
    add_course.add_argument("duration", type=int)
    add_course.add_argument("description")

    courses_sub.add_parser("list", help="List existing courses")

    # Participants -------------------------------------------------------
    participants_parser = subparsers.add_parser(
        "participants", help="Manage training participants"
    )
    participant_sub = participants_parser.add_subparsers(
        dest="participant_command", required=True
    )

    add_participant = participant_sub.add_parser(
        "add", help="Register a new employee for the training program"
    )
    add_participant.add_argument("employee_id")
    add_participant.add_argument("name")
    add_participant.add_argument("department")

    participant_sub.add_parser("list", help="List registered employees")

    # Sessions -----------------------------------------------------------
    sessions_parser = subparsers.add_parser(
        "sessions", help="Schedule and monitor training sessions"
    )
    sessions_sub = sessions_parser.add_subparsers(dest="sessions_command", required=True)

    schedule = sessions_sub.add_parser("schedule", help="Schedule a SAP training session")
    schedule.add_argument("session_id")
    schedule.add_argument("course_code")
    schedule.add_argument("start_date", help="Session start date (YYYY-MM-DD)")
    schedule.add_argument("instructor")
    schedule.add_argument("location")
    schedule.add_argument("capacity", type=int)

    sessions_sub.add_parser("list", help="List the scheduled sessions")

    enroll = subparsers.add_parser("enroll", help="Enroll an employee to a session")
    enroll.add_argument("session_id")
    enroll.add_argument("employee_id")

    subparsers.add_parser("report", help="Generate a utilization report")

    return parser


def _print_table(items: Iterable[dict]) -> None:
    for item in items:
        print(json.dumps(item, ensure_ascii=False))


def _repo_from_args(args: argparse.Namespace) -> TrainingRepository:
    return TrainingRepository(Path(args.db))


def handle_courses(args: argparse.Namespace) -> None:
    repo = _repo_from_args(args)
    if args.courses_command == "add":
        course = Course(
            code=args.code,
            title=args.title,
            level=args.level,
            duration_days=args.duration,
            description=args.description,
        )
        repo.add_course(course)
        print(f"Course {course.code} created")
    elif args.courses_command == "list":
        _print_table(course.to_dict() for course in repo.list_courses())


def handle_participants(args: argparse.Namespace) -> None:
    repo = _repo_from_args(args)
    if args.participant_command == "add":
        participant = Participant(
            employee_id=args.employee_id,
            name=args.name,
            department=args.department,
        )
        repo.add_participant(participant)
        print(f"Participant {participant.employee_id} registered")
    elif args.participant_command == "list":
        _print_table(p.to_dict() for p in repo.list_participants())


def handle_sessions(args: argparse.Namespace) -> None:
    repo = _repo_from_args(args)
    if args.sessions_command == "schedule":
        session = Session(
            session_id=args.session_id,
            course_code=args.course_code,
            start_date=args.start_date,
            instructor=args.instructor,
            location=args.location,
            capacity=args.capacity,
        )
        repo.schedule_session(session)
        print(f"Session {session.session_id} scheduled")
    elif args.sessions_command == "list":
        _print_table(session.to_dict() for session in repo.list_sessions())


def handle_enroll(args: argparse.Namespace) -> None:
    repo = _repo_from_args(args)
    updated = repo.enroll_participant(args.session_id, args.employee_id)
    print(json.dumps(updated.to_dict(), ensure_ascii=False))


def handle_report(args: argparse.Namespace) -> None:
    repo = _repo_from_args(args)
    _print_table(repo.generate_report())


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "courses":
            handle_courses(args)
        elif args.command == "participants":
            handle_participants(args)
        elif args.command == "sessions":
            handle_sessions(args)
        elif args.command == "enroll":
            handle_enroll(args)
        elif args.command == "report":
            handle_report(args)
        else:
            parser.error("Unknown command")
    except RepositoryError as err:
        parser.exit(status=2, message=f"Error: {err}\n")


if __name__ == "__main__":  # pragma: no cover
    main()
