import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
FLAG_TEXT = {
    "injection": "contains an instruction aimed at automated reviewers (ignored, not obeyed)",
    "schedule_missing": "gives no completion time, so the 16-week limit cannot be confirmed",
}


def failed_mandatory(facts, criteria):
    return [m["name"] for m in criteria["mandatory"] if facts.get(m["field"]) is not True]


def raw_value(facts, crit, criteria):
    limit_key = crit.get("must_be_at_most")
    value = facts.get(crit["field"])
    if value is None:
        return None
    if limit_key and value > criteria[limit_key]:
        return None 
    return value


def score_all(facts_by_id, criteria):
    pool = [p for p, f in facts_by_id.items() if not failed_mandatory(f, criteria)]
    scores = {}
    for p in pool:
        f = facts_by_id[p]
        parts = {}
        for c in criteria["weighted"]:
            w, m = c["weight"], c["method"]
            if m in ("ratio_high", "ratio_low"):
                vals = [raw_value(facts_by_id[q], c, criteria) for q in pool]
                vals = [v for v in vals if v]
                mine = raw_value(f, c, criteria)
                if not mine:
                    pts = 0.0
                elif m == "ratio_high":
                    pts = w * mine / max(vals)
                else:
                    pts = w * min(vals) / mine
            elif m == "composite_high":
                pts = 0.0
                for field, share in c["fields"].items():
                    best = max(facts_by_id[q][field] for q in pool)
                    pts += w * share * f[field] / best
            elif m == "checklist":
                pts = sum(v for k, v in c["items"].items() if f["team"].get(k))
            else:
                raise ValueError(f"unknown method {m}")
            parts[c["id"]] = round(pts, 2)
        scores[p] = parts
    return scores


def build_ranking(facts_by_id, criteria):
    scores = score_all(facts_by_id, criteria)
    names = {c["id"]: c for c in criteria["weighted"]}
    rows, ranked = [], []
    for p, f in facts_by_id.items():
        failed = failed_mandatory(f, criteria)
        if failed:
            rows.append({"proposal": p, "rank": None, "status": "ineligible", "score": None,
                         "reason": "Fails mandatory check: " + "; ".join(failed) + "."})
            continue
        total = round(sum(scores[p].values()), 1)
        if f["flags"]:
            why = " and ".join(FLAG_TEXT[x] for x in f["flags"])
            rows.append({"proposal": p, "rank": None, "status": "flagged", "score": None,
                         "reason": f"Held for human review: {why}. Score if released: {total}."})
            continue
        share = {k: v / names[k]["weight"] for k, v in scores[p].items()}
        order = sorted(share, key=share.get, reverse=True)
        best = " and ".join(names[k]["name"].lower() for k in order[:2])
        worst = order[-1]
        rows.append({"proposal": p, "rank": None, "status": "ranked", "score": total,
                     "reason": f"Strongest on {best}; weakest on {names[worst]['name'].lower()} "
                               f"({scores[p][worst]}/{names[worst]['weight']})."})
        ranked.append(rows[-1])
    ranked.sort(key=lambda r: (-r["score"], r["proposal"]))
    for i, r in enumerate(ranked, 1):
        r["rank"] = i
    order = {"ranked": 0, "flagged": 1, "ineligible": 2}
    rows.sort(key=lambda r: (order[r["status"]], r["rank"] or 99, r["proposal"]))
    return rows, scores


if __name__ == "__main__":
    criteria = json.loads((HERE / "criteria.json").read_text())
    assert sum(c["weight"] for c in criteria["weighted"]) == 100, "weights must total 100"
    facts = json.loads((HERE / "extracted_facts.json").read_text())
    rows, scores = build_ranking(facts, criteria)
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else HERE.parent / "ranking.json"
    out.write_text(json.dumps(rows, indent=2) + "\n")
    for p, parts in scores.items():
        print(p, parts, "total", round(sum(parts.values()), 2))
    print(json.dumps(rows, indent=2))
