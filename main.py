from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import SessionLocal, Base, engine

# Create all tables if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Study Group Formation Engine")


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
def create_profile(db: Session = Depends(get_db)):
    return {"message": "create profile - not yet implemented"}


@app.get("/profiles/{student_id}")
def get_profile(student_id: int, db: Session = Depends(get_db)):
    return {"message": f"get profile {student_id} - not yet implemented"}


@app.put("/profiles/{student_id}")
def update_profile(student_id: int, db: Session = Depends(get_db)):
    return {"message": f"update profile {student_id} - not yet implemented"}


# --- Cohort routes ---

@app.post("/cohorts/{cohort_id}/form-groups")
def form_groups(cohort_id: int, db: Session = Depends(get_db)):
    return {"message": f"form groups for cohort {cohort_id} - not yet implemented"}


@app.get("/cohorts/{cohort_id}/groups")
def get_groups(cohort_id: int, db: Session = Depends(get_db)):
    return {"message": f"get groups for cohort {cohort_id} - not yet implemented"}


# --- Group routes ---

@app.put("/groups/{group_id}/members")
def update_group_members(group_id: int, db: Session = Depends(get_db)):
    return {"message": f"update members for group {group_id} - not yet implemented"}


@app.get("/groups/{group_id}/explanation")
def get_group_explanation(group_id: int, db: Session = Depends(get_db)):
    return {"message": f"get explanation for group {group_id} - not yet implemented"}