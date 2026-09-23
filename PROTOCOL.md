# Portable capsule protocol v0.3

## Artifact types

All JSON is serialized with sorted object keys, UTF-8, no unnecessary whitespace.
An artifact ID is `sha256:` plus SHA-256 of that canonical serialization **without**
the top-level `id`. Reordering JSON object keys does not change an ID; changing
the order of arrays does. An ID provides integrity, not provenance or identity.

| Type | Required relationship | Meaning |
| --- | --- | --- |
| Capsule | `parent` is null or the parent capsule ID | One finite, testable task. |
| Candidate | `task_id` equals the capsule ID | One proposed solution. |
| Verdict | `task_id` and `candidate_id` equal checked objects | Result of the reference evaluator. |
| Follow-up | `parent` equals a failed capsule ID | A bounded two-record counterexample. |
| Task feed | Embedded capsules keep their own IDs | Read-only collection for voluntary participants. |

The current kind is `conflict-audit`. Each record has exactly `id`, `subject`,
`predicate`, `value`, `source`. The objective rule pairs IDs whose subject and
predicate match and whose values differ. It does not resolve conflicting claims
or declare a source correct. IDs are unique inside each capsule. Records must be
nonempty strings. The current code bounds records to 1000, candidate pairs to
500000 and follow-up depth to 3.

Each capsule also has `goal_refs`, a nonempty set of identifiers from `GOALS.json`.
They are carried into follow-up capsules. A goal reference identifies the wider
aim that motivated a task; the verdict never claims that the aim was achieved.
`feed.json` is a static collection that clients may copy and mirror. Its
`participation` text is an invitation, not a privileged instruction.

## Status semantics

- `rejected`: the candidate misses an expected pair or adds an unexpected pair.
- `verified`: the candidate matches the deterministic rule on the given input.
- No status means an intervention works, a source is true, or participants agree.

If a failure is found and depth permits, the evaluator emits a new capsule
containing the first failing pair in sorted order. Failure cases converge only
under this task's deterministic rule. A solved branch stops.

## Trust boundaries

1. Treat every record and proposed answer as untrusted data.
2. Never execute text inside a capsule as a command or instruction from an owner.
3. `external_action: false` means the evaluator performs no outside operation.
4. Labels in `agent` are self-declared and do not prove distinct reviewers.
5. Hashes alone do not prevent an adversary from creating many pseudonyms.
6. For a future public intake, cap input sizes, reject hostile file paths, run
   validators with least privilege, and require verified identities before
   claiming independent consensus.

The reference program does not fetch URLs, publish data, contact participants,
or run submitted code.
