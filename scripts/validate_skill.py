#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
REFERENCE = ROOT / "references" / "review-playbook.md"
RESEARCH = ROOT / "docs" / "research.md"
GITIGNORE = ROOT / ".gitignore"
VALIDATION_DOC = ROOT / "docs" / "validation.md"
SMOKE_SUMMARY = ROOT / "tests" / "smoke-summary.json"
EVAL_RESULTS = ROOT / "docs" / "eval-results.md"

REQUIRED_HEADINGS = [
    "# PR Review: Playwright TypeScript POM Frameworks",
    "## Goal",
    "## Use this skill when",
    "## Do not use this skill when",
    "## Review priorities",
    "## Must-check signals",
    "## Output format",
]

REQUIRED_TERMS = [
    "Component objects",
    "Business objects",
    "getByRole",
    "getByTestId",
    "waitForTimeout",
    "force: true",
    "web-first assertions",
    "schema validation",
    "base.extend",
    "playwright/.auth",
    "tsc --noEmit",
    "eslint-plugin-playwright",
    "no-floating-promises",
    "Prettier",
    "forbidOnly",
    "trace: 'on-first-retry'",
]

@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def load(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def frontmatter_ok(text: str) -> tuple[bool, str]:
    match = re.match(r"^---\n(?P<body>.*?)\n---\n", text, re.S)
    if not match:
        return False, "missing YAML frontmatter"
    body = match.group("body")
    has_name = re.search(r"^name:\s*pr-review-playwright-pom-typescript\s*$", body, re.M)
    has_description = re.search(r"^description:\s*\S", body, re.M)
    if not has_name:
        return False, "frontmatter name is missing or wrong"
    if not has_description:
        return False, "frontmatter description is missing"
    return True, "frontmatter has name and description"


def fence_balance(text: str) -> tuple[bool, str]:
    stack: list[str] = []
    fence_lines = 0
    for lineno, line in enumerate(text.splitlines(), start=1):
        match = re.match(r"^(`{3,}|~{3,})", line)
        if not match:
            continue
        marker = match.group(1)
        fence_lines += 1
        if stack and marker.startswith(stack[-1][0]) and len(marker) >= len(stack[-1]):
            stack.pop()
        else:
            stack.append(marker)
    if stack:
        return False, f"unclosed fence marker {stack[-1]!r}"
    return True, f"{fence_lines} fenced-code boundary lines are balanced"


def count_checklist_items(text: str) -> int:
    section_match = re.search(r"## Quick scan checklist\n(?P<section>.*?)(?:\n## |\Z)", text, re.S)
    if not section_match:
        return 0
    return len(re.findall(r"^\d+\.\s+", section_match.group("section"), re.M))


def count_review_signals(research: str) -> int:
    table_match = re.search(r"\| Category \| High-impact PR review signal \| Why it matters \|\n\|.*?\|\n(?P<body>.*?)(?:\n## |\Z)", research, re.S)
    if not table_match:
        return 0
    return len([line for line in table_match.group("body").splitlines() if line.startswith("|")])


def source_count(research: str) -> int:
    match = re.search(r"## Sources used\n(?P<section>.*?)(?:\n## |\Z)", research, re.S)
    if not match:
        return 0
    return len(re.findall(r"^\d+\.\s+", match.group("section"), re.M))


def main() -> int:
    skill = load(SKILL)
    reference = load(REFERENCE)
    research = load(RESEARCH)
    gitignore = load(GITIGNORE)
    combined_skill = skill + "\n" + reference
    checks: list[Check] = []

    ok, detail = frontmatter_ok(skill)
    checks.append(Check("Skill frontmatter", ok, detail))

    ok, detail = fence_balance(combined_skill)
    checks.append(Check("Markdown code fences", ok, detail))

    reference_exists = REFERENCE.exists()
    checks.append(Check("Reference playbook", reference_exists, "references/review-playbook.md exists" if reference_exists else "missing reference playbook"))

    missing_headings = [heading for heading in REQUIRED_HEADINGS if heading not in skill]
    checks.append(Check("Lean skill headings", not missing_headings, f"{len(REQUIRED_HEADINGS) - len(missing_headings)}/{len(REQUIRED_HEADINGS)} present"))

    missing_terms = [term for term in REQUIRED_TERMS if term not in combined_skill]
    checks.append(Check("Required review terms", not missing_terms, f"{len(REQUIRED_TERMS) - len(missing_terms)}/{len(REQUIRED_TERMS)} present across skill + reference"))

    checklist_items = count_checklist_items(combined_skill)
    checks.append(Check("Reference checklist size", checklist_items == 16, f"{checklist_items} checklist items"))

    signals = count_review_signals(research)
    checks.append(Check("Research signal table", signals >= 20, f"{signals} high-impact signals"))

    sources = source_count(research)
    checks.append(Check("Research source count", sources >= 12, f"{sources} sources"))

    ignored = "docs/research.md" in gitignore.splitlines()
    checks.append(Check("Research ignored", ignored, "docs/research.md present in .gitignore" if ignored else "docs/research.md missing from .gitignore"))

    eval_doc = EVAL_RESULTS.exists()
    checks.append(Check("Eval results document", eval_doc, "docs/eval-results.md exists" if eval_doc else "missing docs/eval-results.md"))

    no_todos = not re.search(r"\b(TODO|TBD|FIXME|placeholder)\b", combined_skill, re.I)
    checks.append(Check("No placeholders", no_todos, "no TODO/TBD/FIXME/placeholder tokens" if no_todos else "placeholder token found"))

    word_count = len(re.findall(r"\b[\w'-]+\b", skill))
    reference_words = len(re.findall(r"\b[\w'-]+\b", reference))
    headings = len(re.findall(r"^#{1,3}\s+", skill, re.M))
    reference_headings = len(re.findall(r"^#{1,3}\s+", reference, re.M))
    code_blocks = len(re.findall(r"^(?:`{3,}|~{3,})", combined_skill, re.M))
    severity_labels = len(re.findall(r"\*\*(Blocker|High|Medium|Low)\*\*", combined_skill))
    lean_enough = word_count <= 500
    checks.append(Check("Lean skill body", lean_enough, f"{word_count} words in SKILL.md"))

    smoke = None
    if SMOKE_SUMMARY.exists():
        smoke = json.loads(SMOKE_SUMMARY.read_text(encoding="utf-8"))


    eval_results = EVAL_RESULTS.read_text(encoding="utf-8") if EVAL_RESULTS.exists() else None
    passed = sum(1 for check in checks if check.passed)
    failed = len(checks) - passed

    lines = [
        "# Skill validation numbers",
        "",
        "Generated by `python scripts/validate_skill.py`.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Validation checks | {len(checks)} |",
        f"| Passed checks | {passed} |",
        f"| Failed checks | {failed} |",
        f"| Skill words | {word_count} |",
        f"| Reference words | {reference_words} |",
        f"| Skill headings | {headings} |",
        f"| Reference headings | {reference_headings} |",
        f"| Code block fence lines | {code_blocks} |",
        f"| Severity labels | {severity_labels} |",
        f"| Quick checklist items | {checklist_items} |",
        f"| Research sources | {sources} |",
        f"| Research high-impact signals | {signals} |",
        "",
        "## Checks",
        "",
        "| Check | Result | Detail |",
        "| --- | --- | --- |",
    ]
    for check in checks:
        result = "PASS" if check.passed else "FAIL"
        lines.append(f"| {check.name} | {result} | {check.detail} |")
    lines.append("")
    if smoke:
        lines.extend([
            "## Behavioral smoke test",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| Findings returned | {smoke['findings']} |",
            f"| Complete findings | {smoke['complete_findings']} |",
            f"| Incomplete findings | {smoke['incomplete_findings']} |",
            f"| Expected signals | {smoke['expected_signals']} |",
            f"| Covered signals | {smoke['covered_signals']} |",
            "",
            "| Expected signal | Covered |",
            "| --- | --- |",
        ])
        for name, covered in smoke["coverage"].items():
            result = "YES" if covered else "NO"
            lines.append(f"| {name} | {result} |")
        lines.append("")
    if eval_results:
        metric_names = [
            "Eval cases",
            "Positive trigger cases",
            "Negative trigger cases",
            "Trigger runs",
            "Trigger pass rate",
            "Outcome cases",
            "With-skill expected checks covered",
            "Without-skill expected checks covered",
            "Skill delta",
        ]
        lines.extend([
            "## Video-process eval results",
            "",
            "Detailed results: `docs/eval-results.md`.",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
        ])
        for metric_name in metric_names:
            match = re.search(rf"^\| {re.escape(metric_name)} \| (?P<value>.*?) \|$", eval_results, re.M)
            if match:
                lines.append(f"| {metric_name} | {match.group('value')} |")
        lines.append("")

    VALIDATION_DOC.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"checks={len(checks)} passed={passed} failed={failed}")
    print(f"skill_words={word_count} headings={headings} checklist_items={checklist_items}")
    print(f"research_sources={sources} research_signals={signals}")
    print(f"validation_doc={VALIDATION_DOC.relative_to(ROOT)}")

    if failed:
        for check in checks:
            if not check.passed:
                print(f"FAIL: {check.name}: {check.detail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
