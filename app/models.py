from sqlalchemy import Column, Float, ForeignKey, Integer, JSON, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./studygroups.db"

engine = create_engine(
	SQLALCHEMY_DATABASE_URL,
	connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Cohort(Base):
	__tablename__ = "cohorts"

	id = Column(Integer, primary_key=True, index=True)
	course_name = Column(String, nullable=False)
	term = Column(String, nullable=False)


class Student(Base):
	__tablename__ = "students"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable=False)
	cohort_id = Column(Integer, ForeignKey("cohorts.id"), nullable=False)
	interests_text = Column(String, nullable=True)
	skills = Column(JSON, nullable=False, default=list)
	availability = Column(JSON, nullable=False, default=list)


class Group(Base):
	__tablename__ = "groups"

	id = Column(Integer, primary_key=True, index=True)
	cohort_id = Column(Integer, ForeignKey("cohorts.id"), nullable=False)
	member_ids = Column(JSON, nullable=False, default=list)
	formation_score = Column(Float, nullable=False, default=0.0)
	summary = Column(String, nullable=True)
def init_db():
	Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
	init_db()
