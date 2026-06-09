#!/usr/bin/env python3
"""
FIRE-EVIDENCE -> native FHIR JSON Bundle serializer (base FHIR R5-oriented).

This version fixes the common HL7 FHIR Validator errors seen in the first
serialization attempt:
- removes non-FHIR fields such as ResearchStudy.enrollment, Group.actual, and
  Group.characteristic.description;
- uses valid absolute Bundle.fullUrl values instead of invalid urn:uuid labels;
- rewrites internal references to resolvable absolute URLs matching fullUrl;
- uses ResearchStudy.status='active' rather than the invalid publication-status
  code 'completed';
- adds generated XHTML narratives to reduce dom-6 narrative warnings;
- adds CodeableConcept text/codings for Evidence.variableDefinition.variableRole
  and conservative text-only statisticType values when base FHIR code certainty is low.

The output is intended for base FHIR validation first:
  java -jar validator_cli.jar output.json -version 5.0.0

EBMonFHIR profile validation may require adding exact meta.profile URLs and
adjusting codings to the chosen EBMonFHIR package/version.

V3 refinement: fixes terminology errors reported by HL7 Validator 6.9.9 for
base FHIR R5 validation: variable-role displays now use canonical display text,
and statisticType is emitted as text-only by default to avoid invalid statistic
code assertions.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import docx  # python-docx
except Exception:  # pragma: no cover
    docx = None

FHIR_BASE = "https://fire-evidence.example.org/fhir"


@dataclass
class Obj:
    """Generic container used to safely evaluate FIRE-EVIDENCE constructors."""
    _class_name: str
    _attrs: Dict[str, Any]

    def __getattr__(self, name: str) -> Any:
        return self._attrs.get(name)

    def get(self, name: str, default: Any = None) -> Any:
        return self._attrs.get(name, default)


def make_ctor(class_name: str):
    def ctor(**kwargs):
        return Obj(class_name, kwargs)
    return ctor


EVAL_ENV = {
    "ResearchStudy": make_ctor("ResearchStudy"),
    "Group": make_ctor("Group"),
    "Characteristic": make_ctor("Characteristic"),
    "Citation": make_ctor("Citation"),
    "PublicationForm": make_ctor("PublicationForm"),
    "Evidence": make_ctor("Evidence"),
    "VariableDefinition": make_ctor("VariableDefinition"),
    "Statistic": make_ctor("Statistic"),
    "SampleSize": make_ctor("SampleSize"),
    "EvidenceVariable": make_ctor("EvidenceVariable"),
    "ArtifactAssessment": make_ctor("ArtifactAssessment"),
    "None": None,
    "True": True,
    "False": False,
}

TOP_LEVEL_KEYS = [
    "research_study",
    "groups",
    "evidence_results",
    "artifact_assessments",
    "population",
    "intervention",
    "comparator",
    "outcome",
    "citation",
]


def read_input(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        if docx is None:
            raise RuntimeError("python-docx is required for .docx input: pip install python-docx")
        document = docx.Document(str(path))
        return "\n".join(p.text for p in document.paragraphs if p.text.strip())
    return path.read_text(encoding="utf-8")


def extract_assignment(text: str, key: str, next_keys: List[str]) -> Optional[str]:
    """Extract RHS after key= by balanced parentheses/brackets."""
    m = re.search(rf"\b{re.escape(key)}\s*=", text)
    if not m:
        return None
    i = m.end()
    n = len(text)
    while i < n and text[i].isspace():
        i += 1
    if text.startswith("None", i):
        return "None"
    expr_start = i
    opening = text[i] if i < n else ""
    if opening not in "([":
        ident_match = re.match(r"[A-Za-z_][A-Za-z0-9_]*\s*\(", text[i:])
        if ident_match:
            i = i + ident_match.group(0).rfind("(")
            opening = "("
        else:
            candidates = []
            for nk in next_keys:
                mm = re.search(rf"\b{re.escape(nk)}\s*=", text[i:])
                if mm:
                    candidates.append(i + mm.start())
            end = min(candidates) if candidates else n
            return text[i:end].strip()

    pairs = {"(": ")", "[": "]"}
    stack = [pairs[opening]]
    j = i + 1
    quote = None
    escape = False
    while j < n:
        ch = text[j]
        if quote:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                quote = None
        else:
            if ch in "'\"":
                quote = ch
            elif ch in pairs:
                stack.append(pairs[ch])
            elif stack and ch == stack[-1]:
                stack.pop()
                if not stack:
                    return text[expr_start:j + 1].strip()
        j += 1
    raise ValueError(f"Unbalanced expression for {key}")


def parse_intermediate(text: str) -> Dict[str, Any]:
    cleaned = re.sub(r"\s+", " ", text.replace("\u00a0", " ")).strip()
    data: Dict[str, Any] = {}
    for i, key in enumerate(TOP_LEVEL_KEYS):
        rhs = extract_assignment(cleaned, key, TOP_LEVEL_KEYS[i + 1:])
        if rhs is None:
            continue
        rhs = rhs.strip().rstrip(";")
        try:
            data[key] = eval(rhs, {"__builtins__": {}}, EVAL_ENV)
        except Exception as exc:
            raise ValueError(f"Could not parse assignment {key}=...\nRHS starts: {rhs[:400]}") from exc
    if "research_study" not in data:
        raise ValueError("No research_study=ResearchStudy(...) assignment found in input")
    return data


def text_or_none(value: Any) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def as_int(value: Any) -> Optional[int]:
    s = text_or_none(value)
    if not s:
        return None
    s = s.replace(",", "")
    m = re.search(r"-?\d+", s)
    return int(m.group()) if m else None


def as_float(value: Any) -> Optional[float]:
    s = text_or_none(value)
    if not s:
        return None
    s = s.replace(",", "").replace("%", "")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group()) if m else None


def safe_id(value: Any, fallback: str) -> str:
    s = text_or_none(value) or fallback
    s = re.sub(r"[^A-Za-z0-9\-.]", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or fallback


def machine_name(value: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]", " ", value or "Resource")
    parts = [p for p in s.split() if p]
    out = "".join(p[:1].upper() + p[1:] for p in parts)
    if not out or not out[0].isalpha():
        out = "FireEvidence" + out
    return out[:64]


def narrative(title: str) -> Dict[str, str]:
    txt = html.escape(title or "FIRE-EVIDENCE resource")
    return {
        "status": "generated",
        "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">{txt}</div>",
    }


def codeable(text: str, system: Optional[str] = None, code: Optional[str] = None, display: Optional[str] = None) -> Dict[str, Any]:
    cc: Dict[str, Any] = {"text": text}
    if code:
        coding: Dict[str, Any] = {"code": code, "display": display or text}
        if system:
            coding["system"] = system
        cc["coding"] = [coding]
    return cc


def note(text: str) -> Dict[str, str]:
    return {"text": text}


def fhir_url(resource_type: str, rid: str) -> str:
    return f"{FHIR_BASE}/{resource_type}/{rid}"


def rewrite_reference(ref: Optional[str], ref_map: Dict[str, str]) -> Optional[str]:
    if not ref:
        return None
    if ref.startswith("http://") or ref.startswith("https://") or ref.startswith("urn:"):
        return ref
    return ref_map.get(ref, ref)


VARIABLE_ROLE_SYSTEM = "http://terminology.hl7.org/CodeSystem/variable-role"
STATISTIC_TYPE_SYSTEM = "http://terminology.hl7.org/CodeSystem/statistic-type"


def variable_role_code(role: str) -> Dict[str, Any]:
    """Return a CodeableConcept for Evidence.variableDefinition.variableRole.

    The user-facing role label from FIRE-EVIDENCE is retained in CodeableConcept.text,
    while the coding display uses the canonical FHIR display required by the
    terminology server. This fixes validator errors such as:
      exposure -> display must be "exposure", not "intervention".
    """
    raw = role or "variable"
    r = raw.strip().lower().replace("_", "-").replace(" ", "-")
    mapping = {
        "population": ("population", "population"),
        "intervention": ("exposure", "exposure"),
        "exposure": ("exposure", "exposure"),
        "comparator": ("referenceExposure", "reference exposure"),
        "control": ("referenceExposure", "reference exposure"),
        "outcome": ("measuredVariable", "measured variable"),
        "measured-variable": ("measuredVariable", "measured variable"),
        "group": ("subpopulation", "subpopulation"),
        "subgroup": ("subpopulation", "subpopulation"),
        "covariate": ("covariate", "covariate"),
    }
    mapped = mapping.get(r)
    if not mapped:
        return {"text": raw}
    code, display = mapped
    return {
        "coding": [{
            "system": VARIABLE_ROLE_SYSTEM,
            "code": code,
            "display": display,
        }],
        "text": raw,
    }


def statistic_type_code(stype: str) -> Dict[str, Any]:
    """Return a conservative CodeableConcept for Evidence.statistic.statisticType.

    In the validation report, the code 'relative-RR' was rejected by the R5
    terminology package. To avoid asserting invalid terminology, V3 emits
    statisticType as text-only. This is valid base FHIR JSON and preserves the
    statistic label; EBMonFHIR/profile-level work can later add exact codes from
    the selected IG/package version.
    """
    raw = stype or "statistic"
    return {"text": raw}


def characteristic_to_group_char(ch: Obj) -> Dict[str, Any]:
    desc = text_or_none(ch.description) or "Characteristic"
    # FHIR Group.characteristic does not allow a free-text 'description' child.
    return {
        "code": codeable(desc),
        "valueBoolean": True,
        "exclude": False,
    }


def characteristic_to_ev_char(ch: Obj) -> Dict[str, Any]:
    desc = text_or_none(ch.description) or "Characteristic"
    return {
        "description": desc,
        "definitionCodeableConcept": codeable(desc),
        "exclude": False,
    }


def make_citation(cit: Optional[Obj], fallback_title: str) -> Dict[str, Any]:
    title = text_or_none(getattr(cit, "title", None)) if cit else None
    rid = safe_id(getattr(cit, "id", None), "citation1") if cit else "citation1"
    citation: Dict[str, Any] = {
        "resourceType": "Citation",
        "id": rid,
        "text": narrative(title or fallback_title),
        "status": "active",
        "title": title or fallback_title,
    }
    doi = text_or_none(getattr(cit, "doi", None)) if cit else None
    pmid = text_or_none(getattr(cit, "pmid", None)) if cit else None
    identifiers = []
    if doi:
        identifiers.append({"system": "https://doi.org", "value": doi})
    if pmid:
        identifiers.append({"system": "https://pubmed.ncbi.nlm.nih.gov", "value": pmid})
    if identifiers:
        citation["identifier"] = identifiers
    return citation


def make_group(g: Obj) -> Dict[str, Any]:
    gid = safe_id(g.id, "group")
    desc = text_or_none(g.description) or gid
    quantity = None
    chars = []
    for ch in (g.characteristics or []):
        chars.append(characteristic_to_group_char(ch))
        if quantity is None:
            quantity = as_int(ch.description)

    role = text_or_none(g.type)
    resource: Dict[str, Any] = {
        "resourceType": "Group",
        "id": gid,
        "text": narrative(desc),
        "type": "person",
        # R5 Group uses 'membership' rather than R4-style 'actual'.
        "membership": "definitional",
        "name": desc[:120],
        "description": desc,
    }
    if quantity is not None:
        resource["quantity"] = quantity
    if role:
        resource["code"] = codeable(role)
    if chars:
        resource["characteristic"] = chars
    return resource


def make_evidence_variable(ev: Obj) -> Dict[str, Any]:
    eid = safe_id(ev.id, "evidence-variable")
    desc = text_or_none(ev.description) or eid
    ev_type = text_or_none(ev.type)
    chars = [characteristic_to_ev_char(ch) for ch in (ev.characteristics or [])]
    if desc and not any(c.get("description") == desc for c in chars):
        chars.insert(0, {"description": desc, "definitionCodeableConcept": codeable(desc), "exclude": False})
    resource: Dict[str, Any] = {
        "resourceType": "EvidenceVariable",
        "id": eid,
        "text": narrative(desc),
        "status": "active",
        "name": machine_name(eid),
        "title": desc[:250],
        "description": desc,
    }
    if ev_type:
        resource["note"] = [note(f"FIRE-EVIDENCE variable role: {ev_type}")]
    if chars:
        resource["characteristic"] = chars
    return resource


def make_statistic(st: Obj) -> Dict[str, Any]:
    stat: Dict[str, Any] = {}
    desc = text_or_none(st.description)
    if desc:
        stat["description"] = desc
    stype = text_or_none(st.statisticType)
    if stype:
        stat["statisticType"] = statistic_type_code(stype)
    val = as_float(st.value)
    unit = text_or_none(st.unit)
    if val is not None:
        q: Dict[str, Any] = {"value": val}
        if unit:
            q["unit"] = unit
        stat["quantity"] = q
    event_rate = text_or_none(st.event_rate)
    if event_rate:
        stat.setdefault("attributeEstimate", []).append({"description": f"Event rate / interval information: {event_rate}"})
    ss = st.sample_size
    if isinstance(ss, Obj):
        sample: Dict[str, Any] = {}
        sdesc = text_or_none(ss.description)
        sval = as_int(ss.value)
        if sdesc:
            sample["description"] = sdesc
        if sval is not None:
            sample["numberOfParticipants"] = sval
        if sample:
            stat["sampleSize"] = sample
    return stat


def make_evidence(e: Obj, ref_map: Dict[str, str]) -> Dict[str, Any]:
    eid = safe_id(e.id, "evidence")
    title = text_or_none(e.title) or eid
    resource: Dict[str, Any] = {
        "resourceType": "Evidence",
        "id": eid,
        "text": narrative(title),
        "status": "active",
        "title": title,
        "description": text_or_none(e.description) or title,
    }
    var_defs = []
    for vd in (e.variable_definitions or []):
        role = text_or_none(vd.variableRole) or "variable"
        ref = rewrite_reference(text_or_none(vd.reference), ref_map)
        item: Dict[str, Any] = {
            "description": role,
            "variableRole": variable_role_code(role),
        }
        if ref:
            item["observed"] = {"reference": ref}
        var_defs.append(item)
    if var_defs:
        resource["variableDefinition"] = var_defs
    stats = [make_statistic(st) for st in (e.statistics or [])]
    stats = [s for s in stats if s]
    if stats:
        resource["statistic"] = stats
    gen = text_or_none(getattr(e, "generation_model", None))
    if gen:
        resource["note"] = [note(f"Generated by {gen}")]
    return resource


def make_research_study(rs: Obj, group_refs: List[str], citation_ref: Optional[str]) -> Dict[str, Any]:
    title = text_or_none(rs.title) or "Research study"
    desc_parts = []
    enrollment = as_int(rs.enrollment)
    if enrollment is not None:
        desc_parts.append(f"Enrollment: {enrollment} participants")
    for label, attr in [
        ("Study design", "study_design"),
        ("Setting", "setting"),
        ("Follow-up duration", "follow_up_duration"),
        ("Allocation concealment", "allocation_concealment"),
        ("Blinding", "blinding"),
        ("Intention-to-treat", "intention_to_treat"),
        ("Funding source", "funding_source"),
    ]:
        val = text_or_none(getattr(rs, attr, None))
        if val:
            desc_parts.append(f"{label}: {val}")
    resource: Dict[str, Any] = {
        "resourceType": "ResearchStudy",
        "id": safe_id(rs.id, "study1"),
        "text": narrative(title),
        # Base FHIR R5 ResearchStudy.status is bound to PublicationStatus.
        # 'completed' is not valid here, so use 'active' and preserve actual completion/follow-up in description.
        "status": "active",
        "title": title,
        "description": "; ".join(desc_parts) or title,
    }
    design = text_or_none(rs.study_design)
    if design:
        resource["studyDesign"] = [codeable(design)]
    if group_refs:
        resource["comparisonGroup"] = [
            {"linkId": ref.rstrip("/").split("/")[-1], "name": ref.rstrip("/").split("/")[-1], "observedGroup": {"reference": ref}}
            for ref in group_refs
        ]
    if citation_ref:
        resource["relatedArtifact"] = [{"type": "citation", "resourceReference": {"reference": citation_ref}}]
    return resource


def build_ref_map(resources: List[Dict[str, Any]]) -> Dict[str, str]:
    return {f"{r['resourceType']}/{r['id']}": fhir_url(r["resourceType"], r["id"]) for r in resources}


def convert(data: Dict[str, Any], source_name: str) -> Dict[str, Any]:
    rs: Obj = data["research_study"]
    title = text_or_none(rs.title) or source_name

    citation_obj = data.get("citation") or (rs.citations[0] if getattr(rs, "citations", None) else None)
    citation = make_citation(citation_obj, title)

    group_objs = data.get("groups") or getattr(rs, "groups", []) or []
    groups = [make_group(g) for g in group_objs]

    ev_resources: List[Dict[str, Any]] = []
    for key in ["population", "intervention", "comparator", "outcome"]:
        ev = data.get(key)
        if isinstance(ev, Obj):
            ev_resources.append(make_evidence_variable(ev))

    # Build a preliminary map so ResearchStudy and Evidence can use absolute, resolvable references.
    prelim_resources = groups + ev_resources + [citation]
    ref_map = build_ref_map(prelim_resources)
    group_refs = [ref_map[f"Group/{g['id']}"] for g in groups]
    citation_ref = ref_map[f"Citation/{citation['id']}"]

    research_study = make_research_study(rs, group_refs, citation_ref)
    # Add ResearchStudy itself after it is created.
    ref_map.update(build_ref_map([research_study]))

    evidence_resources = [make_evidence(e, ref_map) for e in (data.get("evidence_results") or [])]

    resources: List[Dict[str, Any]] = [research_study] + groups + ev_resources + evidence_resources + [citation]

    entries = []
    for r in resources:
        entries.append({
            "fullUrl": fhir_url(r["resourceType"], r["id"]),
            "resource": r,
        })

    bundle = {
        "resourceType": "Bundle",
        "id": safe_id(source_name, "fire-evidence-bundle"),
        "type": "collection",
        "entry": entries,
    }
    return bundle


def validate_basic(bundle: Dict[str, Any]) -> List[str]:
    """Lightweight pre-validator; not a substitute for HL7 validator_cli.jar."""
    issues = []
    if bundle.get("resourceType") != "Bundle":
        issues.append("Top-level resourceType is not Bundle")
    ids = set()
    full_urls = set()
    for entry in bundle.get("entry", []):
        full = entry.get("fullUrl")
        if not full or not (full.startswith("http://") or full.startswith("https://")):
            issues.append(f"Bundle entry fullUrl should be absolute HTTP(S) URL: {full}")
        if full in full_urls:
            issues.append(f"Duplicate fullUrl: {full}")
        full_urls.add(full)
        r = entry.get("resource", {})
        rt = r.get("resourceType")
        rid = r.get("id")
        if not rt or not rid:
            issues.append(f"Resource missing resourceType or id: {r}")
        key = f"{rt}/{rid}"
        if key in ids:
            issues.append(f"Duplicate resource identity: {key}")
        ids.add(key)
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Serialize FIRE-EVIDENCE outputs to base FHIR JSON Bundles")
    parser.add_argument("inputs", nargs="+", help="FIRE-EVIDENCE .docx or .txt files")
    parser.add_argument("--outdir", default=".", help="Output directory")
    args = parser.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    for inp in args.inputs:
        path = Path(inp)
        text = read_input(path)
        data = parse_intermediate(text)
        bundle = convert(data, path.stem)
        issues = validate_basic(bundle)
        out = outdir / f"{path.stem}_fhir_bundle.json"
        out.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {out}")
        if issues:
            print("Basic pre-validation issues:")
            for issue in issues:
                print(f"- {issue}")
        else:
            print("Basic pre-validation passed (JSON + Bundle/resource/id/fullUrl uniqueness).")


if __name__ == "__main__":
    main()
