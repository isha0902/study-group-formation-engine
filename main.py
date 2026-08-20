from itertools import combinations

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.clustering import form_groups as build_groups
from app.models import Base, Group, SessionLocal, Student, engine
from app.scoring import fusion_score
from app.skills_taxonomy import get_all_skills

# Create all tables if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Study Group Formation Engine")


class ProfileCreateRequest(BaseModel):
    name: str
    cohort_id: int
    interests_text: str | None = None
    skills: list[str] = Field(default_factory=list)
    availability: list[str] = Field(default_factory=list)


class ProfileUpdateRequest(BaseModel):
    interests_text: str | None = None
    skills: list[str] | None = None
    availability: list[str] | None = None


class FormGroupsRequest(BaseModel):
    pass


class UpdateGroupMembersRequest(BaseModel):
    student_id: int
    target_group_id: int


def student_to_dict(student: Student) -> dict:
    return {
        "id": student.id,
        "name": student.name,
        "cohort_id": student.cohort_id,
        "interests_text": student.interests_text,
        "skills": student.skills or [],
        "availability": student.availability or [],
    }


def group_to_dict(group: Group) -> dict:
    return {
        "id": group.id,
        "cohort_id": group.cohort_id,
        "member_ids": group.member_ids or [],
        "formation_score": group.formation_score,
        "summary": group.summary,
    }


def average_group_fusion_score(students: list[dict]) -> float:
    if len(students) < 2:
        return 0.0

    scores = []
    for student_a, student_b in combinations(students, 2):
        scores.append(
            fusion_score(
                student_a.get("interests_text", "") or "",
                student_b.get("interests_text", "") or "",
                student_a.get("skills", []) or [],
                student_b.get("skills", []) or [],
            )
        )

    return round(sum(scores) / len(scores), 4) if scores else 0.0


def group_shared_skills(students: list[Student]) -> list[str]:
    if not students:
        return []

    shared = set(students[0].skills or [])
    for student in students[1:]:
        shared &= set(student.skills or [])
    return sorted(shared)


# --- Database dependency ---
# This gives each route its own database session, closed after the request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Profile routes ---

@app.post("/profiles")
def create_profile(payload: ProfileCreateRequest, db: Session = Depends(get_db)):
    allowed_skills = set(get_all_skills())
    invalid_skills = [skill for skill in payload.skills if skill not in allowed_skills]
    if invalid_skills:
        raise HTTPException(status_code=400, detail=f"Invalid skills: {', '.join(invalid_skills)}")

    student = Student(
        name=payload.name,
        cohort_id=payload.cohort_id,
        interests_text=payload.interests_text,
        skills=payload.skills,
        availability=payload.availability,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student_to_dict(student)


@app.get("/profiles/{student_id}")
def get_profile(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student_to_dict(student)


@app.put("/profiles/{student_id}")
def update_profile(student_id: int, payload: ProfileUpdateRequest, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    if payload.interests_text is not None:
        student.interests_text = payload.interests_text
    if payload.skills is not None:
        allowed_skills = set(get_all_skills())
        invalid_skills = [skill for skill in payload.skills if skill not in allowed_skills]
        if invalid_skills:
            raise HTTPException(status_code=400, detail=f"Invalid skills: {', '.join(invalid_skills)}")
        student.skills = payload.skills
    if payload.availability is not None:
        student.availability = payload.availability

    db.commit()
    db.refresh(student)
    return student_to_dict(student)


# --- Cohort routes ---

@app.post("/cohorts/{cohort_id}/form-groups")
def form_groups_route(cohort_id: int, db: Session = Depends(get_db)):
    students = db.query(Student).filter(Student.cohort_id == cohort_id).all()
    if len(students) < 2:
        raise HTTPException(status_code=400, detail="At least two students are required to form groups")

    student_dicts = [
        {
            "id": student.id,
            "interests_text": student.interests_text,
            "skills": student.skills or [],
            "availability": student.availability or [],
        }
        for student in students
    ]
    group_member_ids = build_groups(student_dicts)

    results = []
    for member_ids in group_member_ids:
        members = [student for student in students if student.id in member_ids]
        formation_score = average_group_fusion_score([
            {
                "interests_text": student.interests_text,
                "skills": student.skills or [],
            }
            for student in members
        ])
        group = Group(
            cohort_id=cohort_id,
            member_ids=member_ids,
            formation_score=formation_score,
            summary="",
        )
        db.add(group)
        db.flush()
        results.append({
            "id": group.id,
            "cohort_id": group.cohort_id,
            "member_ids": group.member_ids,
            "formation_score": group.formation_score,
            "summary": group.summary,
        })

    db.commit()
    return results


@app.get("/cohorts/{cohort_id}/groups")
def get_groups(cohort_id: int, db: Session = Depends(get_db)):
    groups = db.query(Group).filter(Group.cohort_id == cohort_id).all()
    return [group_to_dict(group) for group in groups]


# --- Group routes ---

@app.put("/groups/{group_id}/members")
def update_group_members(group_id: int, payload: UpdateGroupMembersRequest, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    target_group = db.query(Group).filter(Group.id == payload.target_group_id).first()
    student = db.query(Student).filter(Student.id == payload.student_id).first()

    if group is None or target_group is None or student is None:
        raise HTTPException(status_code=404, detail="Group or student not found")

    student_in_target = db.query(Student).filter(Student.id.in_(target_group.member_ids or [])).all()
    if not any(
        set(student.availability or []) & set(member.availability or [])
        for member in student_in_target
    ):
        raise HTTPException(status_code=400, detail="No schedule overlap with target group")

    if payload.student_id in (group.member_ids or []):
        group.member_ids = [member_id for member_id in (group.member_ids or []) if member_id != payload.student_id]

    if payload.student_id not in (target_group.member_ids or []):
        target_group.member_ids = [*(target_group.member_ids or []), payload.student_id]

    group_students = db.query(Student).filter(Student.id.in_(group.member_ids or [])).all() if group.member_ids else []
    target_students = db.query(Student).filter(Student.id.in_(target_group.member_ids or [])).all() if target_group.member_ids else []
    group.formation_score = average_group_fusion_score([
        {"interests_text": s.interests_text, "skills": s.skills or []} for s in group_students
    ])
    target_group.formation_score = average_group_fusion_score([
        {"interests_text": s.interests_text, "skills": s.skills or []} for s in target_students
    ])

    db.commit()
    db.refresh(group)
    db.refresh(target_group)
    return {"source_group": group_to_dict(group), "target_group": group_to_dict(target_group)}


@app.get("/groups/{group_id}/explanation")
def get_group_explanation(group_id: int, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    members = db.query(Student).filter(Student.id.in_(group.member_ids or [])).all()
    return {
        "group_id": group.id,
        "member_names": [member.name for member in members],
        "shared_skills": group_shared_skills(members),
        "avg_formation_score": group.formation_score,
    }