from sap_training import Course, Participant, Session, TrainingRepository
from sap_training.repository import RepositoryError


def create_repo(tmp_path):
    return TrainingRepository(tmp_path / "db.json")


def test_add_course_and_list(tmp_path):
    repo = create_repo(tmp_path)
    repo.add_course(
        Course(
            code="SD100",
            title="Sales & Distribution Fundamentals",
            level="Beginner",
            duration_days=3,
            description="Covers core SD configuration",
        )
    )

    courses = repo.list_courses()
    assert len(courses) == 1
    assert courses[0].code == "SD100"


def test_schedule_and_enroll(tmp_path):
    repo = create_repo(tmp_path)
    repo.add_course(
        Course(
            code="FI200",
            title="Finance Advanced",
            level="Advanced",
            duration_days=5,
            description="End-to-end SAP FI",
        )
    )
    repo.add_participant(
        Participant(employee_id="E001", name="Ada Lovelace", department="Finance")
    )
    repo.schedule_session(
        Session(
            session_id="FI200-01",
            course_code="FI200",
            start_date="2024-08-01",
            instructor="Grace Hopper",
            location="Istanbul",
            capacity=10,
        )
    )

    updated = repo.enroll_participant("FI200-01", "E001")
    assert updated.enrolled == ["E001"]


def test_enroll_capacity(tmp_path):
    repo = create_repo(tmp_path)
    repo.add_course(
        Course(
            code="MM150",
            title="Materials Management",
            level="Intermediate",
            duration_days=4,
            description="Procurement and inventory",
        )
    )
    repo.add_participant(Participant(employee_id="E010", name="A", department="Ops"))
    repo.add_participant(Participant(employee_id="E011", name="B", department="Ops"))

    repo.schedule_session(
        Session(
            session_id="MM150-01",
            course_code="MM150",
            start_date="2024-07-15",
            instructor="Instructor",
            location="Remote",
            capacity=1,
        )
    )
    repo.enroll_participant("MM150-01", "E010")
    try:
        repo.enroll_participant("MM150-01", "E011")
    except RepositoryError as exc:
        assert "capacity" in str(exc)
    else:
        raise AssertionError("Expected capacity error")


def test_report_contains_human_readable_information(tmp_path):
    repo = create_repo(tmp_path)
    repo.import_seed_data(
        courses=[
            Course(
                code="PP100",
                title="Production Planning",
                level="Intermediate",
                duration_days=2,
                description="",
            )
        ],
        participants=[
            Participant(employee_id="E001", name="Ada Lovelace", department="Ops"),
            Participant(employee_id="E002", name="Grace Hopper", department="Ops"),
        ],
        sessions=[
            Session(
                session_id="PP100-01",
                course_code="PP100",
                start_date="2024-09-01",
                instructor="Alan Turing",
                location="Ankara",
                capacity=15,
                enrolled=["E001", "E002"],
            )
        ],
    )

    report = repo.generate_report()
    assert report[0]["enrolled_count"] == "2"
    assert "Production Planning" in report[0]["course"]
