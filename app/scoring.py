"""
Scoring functions for the Study-Group Formation Engine.

Two scoring methods:
- semantic_similarity: compares free-text interests using TF-IDF cosine similarity
- skill_complementarity: compares skill lists using Jaccard + taxonomy graph
Combined via fusion_score into a single compatibility float (0.0 - 1.0).
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine
from app.skills_taxonomy import are_skills_related


def semantic_similarity(text_a: str, text_b: str) -> float:
    """
    Compute semantic similarity between two interest/goal strings using TF-IDF.
    Returns a float between 0.0 (unrelated) and 1.0 (identical meaning).
    """
    if not text_a or not text_b:
        return 0.0

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
    score = sklearn_cosine(tfidf_matrix[0], tfidf_matrix[1])[0][0]
    return float(round(score, 4))


def skill_complementarity(skills_a: list, skills_b: list) -> float:
    """
    Score two students' skill lists on complementarity.

    Combines:
    - Jaccard similarity (shared foundation)
    - Complementarity bonus (related but non-identical skills from taxonomy)

    Returns a float between 0.0 and 1.0.
    """
    if not skills_a or not skills_b:
        return 0.0

    set_a = set(skills_a)
    set_b = set(skills_b)

    # Jaccard similarity: intersection / union
    intersection = set_a & set_b
    union = set_a | set_b
    jaccard = len(intersection) / len(union) if union else 0.0

    # Complementarity bonus: skills that are related but not identical
    related_pairs = 0
    non_overlapping_a = set_a - set_b
    non_overlapping_b = set_b - set_a

    for skill_a in non_overlapping_a:
        for skill_b in non_overlapping_b:
            if are_skills_related(skill_a, skill_b):
                related_pairs += 1

    # Normalize complementarity bonus by total possible cross-pairs
    max_pairs = len(non_overlapping_a) * len(non_overlapping_b)
    complementarity = related_pairs / max_pairs if max_pairs > 0 else 0.0

    # Weighted combination: 60% jaccard, 40% complementarity
    return round(0.6 * jaccard + 0.4 * complementarity, 4)


def fusion_score(
    text_a: str,
    text_b: str,
    skills_a: list,
    skills_b: list,
    semantic_weight: float = 0.5,
    skill_weight: float = 0.5,
) -> float:
    """
    Combine semantic similarity and skill complementarity into one score.
    Weights must sum to 1.0. Returns a float between 0.0 and 1.0.
    """
    sem_score = semantic_similarity(text_a, text_b)
    skill_score = skill_complementarity(skills_a, skills_b)
    return round(semantic_weight * sem_score + skill_weight * skill_score, 4)