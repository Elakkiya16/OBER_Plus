"""
OBER's attainment computation, against the working store.

Verified against the OBER user guide's own CLO Report / PLO Report screens:

  component attainment (CLO c, component k)
      = total marks scored by all students for c in k
      / (mark allocation for c in k  x  number of students)

  CLO attainment (weighted average)
      = SUM over k of  component_attainment(c,k) x weightage(c,k)   / 100
        (the full weightage row is the denominator — a component with no marks
         uploaded contributes 0, exactly as the real CLO Report shows)

  Course attainment
      = SUM over c of  CLO_attainment(c) x CLO mark share(c)
        where mark share(c) = c's total allocated marks / grand total

  PLO attainment
      = simple average of the CLO attainments mapped to that PLO

Values are fractions 0-1 internally (matching OBER's report, which prints
0.36 style) and are converted to % only at the display/5R boundary.
"""


def component_attainment(course, offering_idx=None):
    """{clo_name: {component: fraction}} for the given offering (default: active)."""
    marks = course["marks"] if offering_idx is None else course["marks_by_offering"][offering_idx]
    n = len(course["roster"]) or 1
    out = {}
    for clo in course["clos"]:
        c = clo["name"]
        row = {}
        for comp_name, _total in course["components"]:
            alloc = course["mark_dist"].get(c, {}).get(comp_name, 0)
            if not alloc:
                row[comp_name] = None
                continue
            scored = sum(sm.get(comp_name, {}).get(c, 0.0) for sm in marks.values())
            row[comp_name] = round(scored / (alloc * n), 4) if alloc else None
        out[c] = row
    return out


def clo_attainment(course, offering_idx=None):
    """{clo_name: fraction} — OBER's weighted average across components."""
    comp_att = component_attainment(course, offering_idx)
    out = {}
    for clo in course["clos"]:
        c = clo["name"]
        weights = course["weightage"].get(c, {})
        total = 0.0
        for comp_name, w in weights.items():
            frac = comp_att[c].get(comp_name)
            total += (frac or 0.0) * w
        out[c] = round(total / 100.0, 4) if weights else 0.0
    return out


def clo_mark_share(course):
    """{clo_name: share 0-1} — each CLO's share of total allocated marks."""
    totals = {}
    grand = 0.0
    for c, allocs in course["mark_dist"].items():
        s = sum(allocs.values())
        totals[c] = s
        grand += s
    if not grand:
        return {c: 0.0 for c in totals}
    return {c: s / grand for c, s in totals.items()}


def course_attainment(course, offering_idx=None):
    """Fraction 0-1."""
    clo_att = clo_attainment(course, offering_idx)
    shares = clo_mark_share(course)
    return round(sum(clo_att.get(c, 0.0) * shares.get(c, 0.0) for c in clo_att), 4)


def plo_attainment(course, offering_idx=None):
    """{plo: fraction or None} — simple average of mapped CLO attainments."""
    from store import PLO_IDS
    clo_att = clo_attainment(course, offering_idx)
    out = {}
    for plo in PLO_IDS:
        mapped = [clo_att[c] for c, plos in course["mapping"].items()
                  if plo in plos and c in clo_att]
        out[plo] = round(sum(mapped) / len(mapped), 4) if mapped else 0.0
    return out


# --- validation helpers used by the entry screens ---------------------------

def weightage_row_totals(course):
    return {c["name"]: sum(course["weightage"].get(c["name"], {}).values())
            for c in course["clos"]}


def mark_column_totals(course):
    out = {}
    for comp_name, _total in course["components"]:
        out[comp_name] = sum(course["mark_dist"].get(c["name"], {}).get(comp_name, 0)
                             for c in course["clos"])
    return out


def student_component_total(course, user_id, comp_name, offering_idx=None):
    marks = course["marks"] if offering_idx is None else course["marks_by_offering"][offering_idx]
    return round(sum(marks.get(user_id, {}).get(comp_name, {}).values()), 1)
