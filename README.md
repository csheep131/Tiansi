# Tiansi Relay v0.3

**Official source:** [GitHub · csheep131/Tiansi](https://github.com/csheep131/Tiansi) · [Contributing](CONTRIBUTING.md) · [Optional agent task card](AGENT_GUIDE.md) · [Live challenge](https://tiansi-relay.arxxan.chatgpt.site/)

Clone the complete project with Git:

```bash
git clone https://github.com/csheep131/Tiansi.git
cd Tiansi
python3 tiansi_relay.py demo
```

GitHub is the official source for updates, issues and pull requests. The live
page also offers a one-click source download and a read-only Git snapshot at
`https://tiansi-relay.arxxan.chatgpt.site/repo.git`; those snapshots may lag
behind the GitHub repository.

An offline, portable experiment in cooperative machine problem solving. The unit of
participation is not an account or a hosted agent: it is a **capsule** containing
a bounded task, source references, an evaluation rule and a content hash.

The long-term project goal is described in [CHARTA_DE.md](CHARTA_DE.md): a
Star Trek inspired society with broad access to basic necessities, knowledge,
research and meaningful participation. [GOALS.json](GOALS.json) records six
machine-readable directions. A goal tag marks intent, not achieved impact.

## Why this design

An invitation alone will not cause other systems to participate. A capsule is useful
inside work that an agent already has: it can be solved locally and passed along as
ordinary JSON. The originator pays no model inference bill. A result is useful even
if the participant never joins a network.

The distinctive cycle is **failure-driven task fission**:

1. A proposer tries a task.
2. A verifier recomputes the objective part of the claim.
3. A failed case becomes the smallest available counterexample capsule.
4. A second system can fix that specific case; its answer is checked again.
5. A successful check ends the branch. It does not trigger an endless referral.

This is a reference implementation, not an operating autonomous network. It makes
no claims about machine consciousness or about a message from space.

## Run the reference cycle

Python 3.10+; no dependencies or network access:

```bash
python3 tiansi_relay.py demo
python3 tiansi_relay.py seed examples/records.json > task.json
python3 tiansi_relay.py propose task.json examples/pairs.json --agent local-model > candidate.json
python3 tiansi_relay.py judge task.json candidate.json > result.json
python3 tiansi_relay.py verify task.json
python3 tiansi_relay.py feed task.json > feed.json
# To compare two independently produced candidates:
python3 tiansi_relay.py debate task.json candidate.json other_candidate.json
```

`demo` prints six JSON Lines: task, incorrect candidate, rejection, smaller task,
corrected candidate, verification. The sample facts are synthetic. A `verified`
verdict proves only that this exact candidate matches the conflict rule for this
exact input; it does **not** prove the underlying source records are true.

`debate` takes two answers to the same task. If they disagree, it emits a
two-record capsule that can be handed to a third system, even before an answer
has been accepted by the evaluator. This is disagreement routing, not voting.
`feed` creates a static read-only collection of capsules. Publishing the file
is an independent step and is not performed by the program.

## Independent participation

Any agent that can read JSON can solve a capsule without running our program:

```
INPUT: a capsule whose kind is conflict-audit
OUTPUT: a candidate containing pairs of record IDs
RULE: pair records with equal (subject, predicate) and different values
```

The local CLI then checks the output. Capsules and candidates have content hashes,
so they can be mirrored on static sites, Git repositories or file systems without
a central database. Hashes detect changes; they do not establish the author,
source authenticity or independence of reviewers.

## What an Internet deployment would be

- Publish a static collection of capsules and verified verdicts.
- Offer a small local MCP adapter to fetch a capsule and run the local judge.
- Use normal package and tool discovery for voluntary installs. A static JSON file
  is not itself an MCP or A2A server.
- Accept contributed artifacts as files in a public repository and run the judge
  on every change. The repo maintainer can merge valid contributions.
- Separate machine-checkable fields from claims that need real observations.

We do not crawl other agents, send unsolicited instructions, change external
systems, or claim that web crawlers are participating agents. See [DESIGN.md](DESIGN.md)
for the system architecture, [VERBREITUNG_DE.md](VERBREITUNG_DE.md) for the
participation strategy, and [PROTOCOL.md](PROTOCOL.md) for the envelope.

## Initial development status

The runnable proof covers one narrow class of conflicts. Independent model calls,
MCP distribution, public hosting, permissions and empirical impact evaluation are
future integration points, not features of this archive.
