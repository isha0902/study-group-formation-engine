"""Clustering helpers for forming study groups."""

from itertools import combinations

import community
import networkx as nx

from app.scoring import fusion_score


def have_schedule_overlap(availability_a: list, availability_b: list) -> bool:
	"""Return True when two availability lists share at least one time slot."""
	if not availability_a or not availability_b:
		return False

	return bool(set(availability_a) & set(availability_b))


def build_similarity_graph(students: list) -> nx.Graph:
	"""Build a weighted student similarity graph constrained by schedule overlap."""
	graph = nx.Graph()

	for student in students:
		graph.add_node(student["id"])

	for student_a, student_b in combinations(students, 2):
		if not have_schedule_overlap(student_a.get("availability", []), student_b.get("availability", [])):
			continue

		weight = fusion_score(
			student_a.get("interests_text", "") or "",
			student_b.get("interests_text", "") or "",
			student_a.get("skills", []) or [],
			student_b.get("skills", []) or [],
		)
		graph.add_edge(student_a["id"], student_b["id"], weight=weight)

	return graph


def form_groups(students: list, target_size: int = 5) -> list:
	"""Form study groups with Louvain community detection and singleton cleanup."""
	if not students:
		return []

	graph = build_similarity_graph(students)
	student_lookup = {student["id"]: student for student in students}

	if graph.number_of_nodes() == 0:
		return []

	try:
		partition = community.best_partition(graph, weight="weight")
	except Exception:
		partition = {node: index for index, node in enumerate(graph.nodes())}

	grouped_ids = {}
	for student_id, community_id in partition.items():
		grouped_ids.setdefault(community_id, []).append(student_id)

	groups = list(grouped_ids.values())

	def group_affinity(group_a: list, group_b: list) -> float:
		scores = []
		for student_id_a in group_a:
			for student_id_b in group_b:
				student_a = student_lookup[student_id_a]
				student_b = student_lookup[student_id_b]
				scores.append(
					fusion_score(
						student_a.get("interests_text", "") or "",
						student_b.get("interests_text", "") or "",
						student_a.get("skills", []) or [],
						student_b.get("skills", []) or [],
					)
				)

		return sum(scores) / len(scores) if scores else 0.0

	groups.sort(key=len, reverse=True)

	while len(groups) > 1 and any(len(group) < 2 for group in groups):
		orphan_index = min(
			(index for index, group in enumerate(groups) if len(group) < 2),
			key=lambda index: len(groups[index]),
		)
		orphan_group = groups.pop(orphan_index)

		best_target_index = None
		best_affinity = -1.0

		for index, candidate_group in enumerate(groups):
			affinity = group_affinity(orphan_group, candidate_group)
			if affinity > best_affinity:
				best_affinity = affinity
				best_target_index = index

		if best_target_index is None:
			groups.append(orphan_group)
			break

		groups[best_target_index].extend(orphan_group)
		groups.sort(key=len, reverse=True)

	return groups
