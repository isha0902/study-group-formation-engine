from app.scoring import semantic_similarity, skill_complementarity, fusion_score

# Test semantic similarity
print("Semantic similarity:")
print(semantic_similarity(
    "I love machine learning and building predictive models",
    "Interested in deep learning and AI applications"
))  # Should be high (0.7+)

print(semantic_similarity(
    "I enjoy frontend web development with React",
    "Interested in deep learning and AI applications"
))  # Should be lower

# Test skill complementarity
print("\nSkill complementarity:")
print(skill_complementarity(
    ["Python", "Machine Learning", "Statistics & Probability"],
    ["Frontend", "React", "Web Development"]
))  # Should be low (different branches, few relations)

print(skill_complementarity(
    ["Python", "Data Analysis"],
    ["Python", "Machine Learning"]
))  # Should be higher (shared Python, related skills)

# Test fusion score
print("\nFusion score:")
print(fusion_score(
    "I love building ML models",
    "Interested in data science and predictions",
    ["Python", "Machine Learning"],
    ["Python", "Data Analysis"]
))