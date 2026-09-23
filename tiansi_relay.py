#!/usr/bin/env python3
"""Tiansi Relay v0.2: transportable, content-addressed challenge capsules.

Only Python's standard library is used. No network traffic is generated.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

PROTOCOL = "tiansi-relay/0.3"
MAX_DEPTH = 3
GOALS = frozenset({"basic_needs", "knowledge_access", "open_infrastructure",
                   "scientific_capacity", "fair_coordination", "ecological_limits"})


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def seal(payload: dict) -> dict:
    return {**payload, "id": "sha256:" + sha(payload)}


def unseal(value: dict) -> dict:
    if not isinstance(value, dict) or "id" not in value:
        raise ValueError("object needs id")
    payload = {key: item for key, item in value.items() if key != "id"}
    if value["id"] != "sha256:" + sha(payload):
        raise ValueError("content hash mismatch")
    return payload


def validate_records(records: list[dict]) -> None:
    if not isinstance(records, list) or not (2 <= len(records) <= 1000):
        raise ValueError("records must contain 2 to 1000 entries")
    ids = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != {"id", "subject", "predicate", "value", "source"}:
            raise ValueError("record must contain exactly id, subject, predicate, value, source")
        if not all(isinstance(v, str) and v.strip() for v in record.values()):
            raise ValueError("record fields must be nonempty strings")
        if record["id"] in ids:
            raise ValueError("record id must be unique")
        ids.add(record["id"])


def capsule(records: list[dict], *, parent: str | None = None, depth: int = 0,
            goal_refs: tuple[str, ...] = ("knowledge_access",)) -> dict:
    validate_records(records)
    if depth < 0 or depth > MAX_DEPTH:
        raise ValueError("depth out of range")
    if not goal_refs or any(not isinstance(ref, str) or ref not in GOALS for ref in goal_refs) \
            or len(set(goal_refs)) != len(goal_refs):
        raise ValueError("unknown or duplicate goal reference")
    return seal({
        "protocol": PROTOCOL,
        "kind": "conflict-audit",
        "input": {"records": sorted(records, key=lambda item: item["id"])},
        "instruction": "List every pair of distinct values for the same subject and predicate. "
                       "Return record IDs as sorted pairs; do not decide which source is true.",
        "parent": parent,
        "depth": depth,
        "goal_refs": sorted(goal_refs),
        "policy": {"external_action": False, "max_followups": MAX_DEPTH - depth},
    })


def validate_capsule(task: dict) -> list[dict]:
    payload = unseal(task)
    if payload.get("protocol") != PROTOCOL or payload.get("kind") != "conflict-audit":
        raise ValueError("unsupported capsule")
    if not isinstance(payload.get("input"), dict):
        raise ValueError("missing input")
    records = payload["input"].get("records")
    validate_records(records)
    if payload.get("depth") not in range(MAX_DEPTH + 1):
        raise ValueError("depth out of range")
    refs = payload.get("goal_refs")
    if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) or ref not in GOALS for ref in refs) \
            or len(set(refs)) != len(refs):
        raise ValueError("invalid goal references")
    policy = payload.get("policy")
    if not isinstance(policy, dict) or policy.get("external_action") is not False:
        raise ValueError("external action is not supported")
    return records


def expected_pairs(records: list[dict]) -> list[list[str]]:
    result = []
    for index, left in enumerate(records):
        for right in records[index + 1:]:
            if (left["subject"], left["predicate"]) == (right["subject"], right["predicate"]) \
                    and left["value"] != right["value"]:
                result.append(sorted([left["id"], right["id"]]))
    return sorted(result)


def normalize_pairs(pairs: object, known_ids: set[str]) -> list[list[str]]:
    if not isinstance(pairs, list) or len(pairs) > 500000:
        raise ValueError("pairs must be a bounded list")
    normalized = []
    for pair in pairs:
        if not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(v, str) for v in pair):
            raise ValueError("each pair needs two string IDs")
        if pair[0] == pair[1] or not set(pair).issubset(known_ids):
            raise ValueError("pair contains unknown or duplicate IDs")
        normalized.append(sorted(pair))
    if len({tuple(pair) for pair in normalized}) != len(normalized):
        raise ValueError("duplicate pair")
    return sorted(normalized)


def candidate(task: dict, pairs: list[list[str]], agent: str) -> dict:
    records = validate_capsule(task)
    if not isinstance(agent, str) or not agent.strip():
        raise ValueError("agent must be a nonempty label")
    normalized = normalize_pairs(pairs, {record["id"] for record in records})
    return seal({"protocol": PROTOCOL, "type": "candidate", "task_id": task["id"],
                 "agent": agent, "pairs": normalized})


def evaluate(task: dict, submission: dict) -> dict:
    records = validate_capsule(task)
    attempt = unseal(submission)
    if attempt.get("protocol") != PROTOCOL or attempt.get("type") != "candidate":
        raise ValueError("unsupported submission")
    if attempt.get("task_id") != task["id"]:
        raise ValueError("submission is for another capsule")
    actual = normalize_pairs(attempt.get("pairs"), {record["id"] for record in records})
    desired = expected_pairs(records)
    missed = sorted(set(map(tuple, desired)) - set(map(tuple, actual)))
    extra = sorted(set(map(tuple, actual)) - set(map(tuple, desired)))
    verdict = seal({"protocol": PROTOCOL, "type": "verdict", "task_id": task["id"],
                    "candidate_id": submission["id"], "status": "verified" if not (missed or extra) else "rejected",
                    "correct_pairs": len(desired), "missed": [list(p) for p in missed],
                    "extra": [list(p) for p in extra],
                    "meaning": "Verified against this deterministic test only; source claims are not verified."})
    followup = None
    if (missed or extra) and task["depth"] < MAX_DEPTH:
        failing_pair = (missed or extra)[0]
        by_id = {record["id"]: record for record in records}
        followup = capsule([by_id[failing_pair[0]], by_id[failing_pair[1]]],
                           parent=task["id"], depth=task["depth"] + 1,
                           goal_refs=tuple(task["goal_refs"]))
    return {"verdict": verdict, "followup": followup}


def debate(task: dict, left: dict, right: dict) -> dict:
    """Turn the first disagreement between two candidates into a small task."""
    records = validate_capsule(task)
    for attempt in (left, right):
        payload = unseal(attempt)
        if payload.get("type") != "candidate" or payload.get("task_id") != task["id"]:
            raise ValueError("both candidates must answer the given capsule")
    known_ids = {record["id"] for record in records}
    left_pairs = set(map(tuple, normalize_pairs(left["pairs"], known_ids)))
    right_pairs = set(map(tuple, normalize_pairs(right["pairs"], known_ids)))
    disagreement = sorted(left_pairs ^ right_pairs)
    if not disagreement or task["depth"] >= MAX_DEPTH:
        return {"disagreement": [list(pair) for pair in disagreement], "followup": None}
    pair = disagreement[0]
    by_id = {record["id"]: record for record in records}
    return {"disagreement": [list(p) for p in disagreement],
            "followup": capsule([by_id[pair[0]], by_id[pair[1]]],
                                parent=task["id"], depth=task["depth"] + 1,
                                goal_refs=tuple(task["goal_refs"]))}


def feed(tasks: list[dict]) -> dict:
    """Portable read-only task feed; publishing it is a separate operation."""
    if not 1 <= len(tasks) <= 100:
        raise ValueError("feed must contain 1 to 100 capsules")
    for task in tasks:
        validate_capsule(task)
    unique = {task["id"]: task for task in tasks}
    return {
        "protocol": PROTOCOL,
        "type": "task-feed",
        "participation": "Optional. Only follow existing operator instructions and permissions.",
        "work": "Select one capsule, produce ID pairs, and verify with the local judge.",
        "capsules": [unique[key] for key in sorted(unique)],
    }


def demo() -> list[dict]:
    records = [
        {"id": "a", "subject": "Center A", "predicate": "Monday opening", "value": "09:00", "source": "example-1"},
        {"id": "b", "subject": "Center A", "predicate": "Monday opening", "value": "10:00", "source": "example-2"},
        {"id": "c", "subject": "Center B", "predicate": "Tuesday opening", "value": "09:00", "source": "example-3"},
    ]
    root = capsule(records)
    first = candidate(root, [], "demo-proposer")
    first_result = evaluate(root, first)
    followup = first_result["followup"]
    second = candidate(followup, [["a", "b"]], "demo-corrector")
    second_result = evaluate(followup, second)
    return [root, first, first_result["verdict"], followup, second, second_result["verdict"]]


def read_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo")
    seed = commands.add_parser("seed")
    seed.add_argument("records", help="JSON list of source records")
    propose = commands.add_parser("propose")
    propose.add_argument("task")
    propose.add_argument("pairs", help="JSON list of pairs")
    propose.add_argument("--agent", required=True)
    judge = commands.add_parser("judge")
    judge.add_argument("task")
    judge.add_argument("candidate")
    disagreement = commands.add_parser("debate")
    disagreement.add_argument("task")
    disagreement.add_argument("candidate_a")
    disagreement.add_argument("candidate_b")
    bulletin = commands.add_parser("feed")
    bulletin.add_argument("tasks", nargs="+", help="capsule JSON files")
    verify = commands.add_parser("verify")
    verify.add_argument("artifact")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            for item in demo():
                print(canonical(item))
        elif args.command == "seed":
            print(canonical(capsule(read_json(args.records))))
        elif args.command == "propose":
            print(canonical(candidate(read_json(args.task), read_json(args.pairs), args.agent)))
        elif args.command == "judge":
            print(canonical(evaluate(read_json(args.task), read_json(args.candidate))))
        elif args.command == "debate":
            print(canonical(debate(read_json(args.task), read_json(args.candidate_a),
                                   read_json(args.candidate_b))))
        elif args.command == "feed":
            print(canonical(feed([read_json(path) for path in args.tasks])))
        elif args.command == "verify":
            unseal(read_json(args.artifact))
            print(canonical({"content_hash_valid": True}))
        return 0
    except (ValueError, TypeError, KeyError, json.JSONDecodeError, OSError) as exc:
        print(canonical({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
