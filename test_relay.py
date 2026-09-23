import unittest

from tiansi_relay import capsule, candidate, debate, evaluate, feed, unseal


RECORDS = [
    {"id": "a", "subject": "site", "predicate": "hours", "value": "9", "source": "one"},
    {"id": "b", "subject": "site", "predicate": "hours", "value": "10", "source": "two"},
    {"id": "c", "subject": "other", "predicate": "hours", "value": "9", "source": "three"},
]


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.task = capsule(RECORDS)

    def test_missing_conflict_spawns_minimal_case_then_verified(self):
        bad = candidate(self.task, [], "first")
        result = evaluate(self.task, bad)
        self.assertEqual(result["verdict"]["status"], "rejected")
        followup = result["followup"]
        self.assertEqual(followup["parent"], self.task["id"])
        self.assertEqual(followup["goal_refs"], ["knowledge_access"])
        self.assertEqual(len(followup["input"]["records"]), 2)
        corrected = candidate(followup, [["a", "b"]], "second")
        self.assertEqual(evaluate(followup, corrected)["verdict"]["status"], "verified")

    def test_disagreement_becomes_fork(self):
        left = candidate(self.task, [], "left")
        right = candidate(self.task, [["a", "b"]], "right")
        argument = debate(self.task, left, right)
        self.assertEqual(argument["disagreement"], [["a", "b"]])
        self.assertEqual(argument["followup"]["depth"], 1)

    def test_tampering_and_cross_task_submission_rejected(self):
        bad_task = dict(self.task, depth=2)
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            unseal(bad_task)
        other_task = capsule(RECORDS[:2])
        submission = candidate(other_task, [["a", "b"]], "other")
        with self.assertRaisesRegex(ValueError, "another capsule"):
            evaluate(self.task, submission)

    def test_false_positive_is_rejected(self):
        attempt = candidate(self.task, [["a", "b"], ["a", "c"]], "tester")
        result = evaluate(self.task, attempt)
        self.assertEqual(result["verdict"]["extra"], [["a", "c"]])

    def test_feed_deduplicates_and_preserves_goal(self):
        bulletin = feed([self.task, self.task])
        self.assertEqual(len(bulletin["capsules"]), 1)
        self.assertEqual(bulletin["capsules"][0]["goal_refs"], ["knowledge_access"])

    def test_unknown_goal_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "goal reference"):
            capsule(RECORDS, goal_refs=("world_changed",))


if __name__ == "__main__":
    unittest.main()
