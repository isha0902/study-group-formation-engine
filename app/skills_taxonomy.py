"""
Skills taxonomy for the Study-Group Formation Engine.

Represents skills as a graph: each skill maps to a list of closely
related skills. Used for computing skill overlap (Jaccard similarity)
and complementarity (whether two skills span different branches).
"""

SKILLS_TAXONOMY = {
    # --- Programming & Software Dev ---
    "Python": ["Data Analysis", "Machine Learning", "Web Development"],
    "Java": ["Algorithms & Data Structures", "Software Testing"],
    "C++": ["Algorithms & Data Structures", "Operating Systems"],
    "Web Development": ["Python", "Frontend", "Backend"],
    "Frontend": ["Web Development", "React"],
    "Backend": ["Web Development", "SQL / Databases"],
    "React": ["Frontend", "Web Development"],
    "Version Control": ["Software Testing", "Web Development"],
    "Software Testing": ["Java", "Version Control"],

    # --- Data & ML ---
    "Data Analysis": ["Python", "Data Visualization", "Statistics & Probability"],
    "Data Visualization": ["Data Analysis", "SQL / Databases"],
    "Machine Learning": ["Python", "Statistics & Probability", "Deep Learning / NLP"],
    "Deep Learning / NLP": ["Machine Learning", "Statistics & Probability"],
    "SQL / Databases": ["Backend", "Data Visualization"],

    # --- Math & Theory ---
    "Linear Algebra": ["Machine Learning", "Statistics & Probability"],
    "Statistics & Probability": ["Data Analysis", "Machine Learning", "Linear Algebra"],
    "Algorithms & Data Structures": ["Java", "C++", "Theory of Computation"],
    "Theory of Computation": ["Algorithms & Data Structures"],

    # --- Systems ---
    "Operating Systems": ["C++", "Computer Networks"],
    "Computer Networks": ["Operating Systems", "Distributed Systems"],
    "Distributed Systems": ["Computer Networks", "Backend"],
}


def are_skills_related(skill_a: str, skill_b: str) -> bool:
    """
    Check if two skills are directly related in the taxonomy.
    Returns False if either skill isn't in the taxonomy at all.
    """
    if skill_a not in SKILLS_TAXONOMY or skill_b not in SKILLS_TAXONOMY:
        return False
    return skill_b in SKILLS_TAXONOMY[skill_a] or skill_a in SKILLS_TAXONOMY[skill_b]


def get_all_skills() -> list:
    """Return a list of every skill name in the taxonomy."""
    return list(SKILLS_TAXONOMY.keys())

