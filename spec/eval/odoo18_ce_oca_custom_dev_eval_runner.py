#!/usr/bin/env python3
"""
Odoo 18 CE/OCA Custom Module Developer Certification Eval Runner

This eval runner evaluates agent-produced Odoo modules against the
certification stages defined in odoo18_ce_oca_custom_dev_cert.yaml.

It supports both:
1. Rubric-based evaluation of agent responses (using a judge model)
2. Automated checks on reference modules (linting, tests, structure)
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------
@dataclass
class StageResult:
    """Result of evaluating a single certification stage."""
    stage_id: str
    label: str
    weight: float
    score: float  # 0.0 to 1.0
    passed: bool
    reasoning: str
    critical_failure: bool = False
    automated_checks: dict = field(default_factory=dict)


@dataclass
class ExamResult:
    """Overall exam result."""
    total_score: float  # weighted percentage
    passed: bool
    stage_results: list[StageResult]
    critical_failure_detected: bool = False
    summary: str = ""


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SPEC_DIR = Path(__file__).parent.parent
SKILLS_PATH = SPEC_DIR / "skills" / "odoo18_ce_oca_custom_dev.yaml"
CERT_PATH = SPEC_DIR / "certs" / "odoo18_ce_oca_custom_dev_cert.yaml"
SYSTEM_PROMPT_PATH = SPEC_DIR / "prompts" / "odoo18_ce_oca_custom_dev_agent.md"
PROJECT_ROOT = SPEC_DIR.parent


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
def load_yaml(path: Path) -> dict:
    """Load a YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_system_prompt(path: Path) -> str:
    """Load the agent system prompt."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_certification() -> dict:
    """Load the certification spec."""
    return load_yaml(CERT_PATH)


def load_skill() -> dict:
    """Load the skill spec."""
    return load_yaml(SKILLS_PATH)


# ---------------------------------------------------------------------------
# Prompt Builders
# ---------------------------------------------------------------------------
def build_stage_agent_prompt(stage: dict[str, Any]) -> str:
    """
    Build the prompt for the agent to respond to a specific stage.
    Used when evaluating agent's ability to produce code for a stage.
    """
    stage_id = stage["stage"]
    label = stage.get("label", stage_id)
    pass_conditions = stage.get("pass_conditions", [])

    lines = [
        f"You are being evaluated for stage: {stage_id} - {label}.",
        "",
        "You are the Odoo 18 CE/OCA Custom Module Developer Agent.",
        "Produce implementation-level output (module skeletons, Python, XML, test code)",
        "that would satisfy ALL of the following pass conditions:",
        "",
    ]
    for cond in pass_conditions:
        lines.append(f"- {cond}")
    lines += [
        "",
        "Return your answer as a structured explanation followed by code blocks.",
        "Focus on OCA-compliant module layout, security, tests, and maintainability.",
    ]
    return "\n".join(lines)


def build_judge_prompt(stage: dict[str, Any], agent_response: str) -> str:
    """
    Build the prompt for the judge model to evaluate the agent's response.
    """
    stage_id = stage["stage"]
    label = stage.get("label", stage_id)
    pass_conditions = stage.get("pass_conditions", [])

    lines = [
        "You are a certification judge for Odoo 18 CE/OCA Custom Module Development.",
        "",
        f"## Stage: {stage_id} - {label}",
        "",
        "## Pass Conditions:",
    ]
    for cond in pass_conditions:
        lines.append(f"- {cond}")

    lines += [
        "",
        "## Agent Response:",
        "```",
        agent_response[:8000],  # Truncate for context limits
        "```",
        "",
        "## Your Task:",
        "Evaluate the agent's response against each pass condition.",
        "",
        "For code-based stages, check:",
        "- Module layout and structure correctness",
        "- Python/XML syntax and OCA conventions",
        "- Security definitions (ACLs, record rules, groups)",
        "- Test coverage and quality",
        "- Performance considerations",
        "",
        "## Output Format (JSON):",
        "```json",
        "{",
        '  "score": 0.0-1.0,',
        '  "passed": true/false,',
        '  "critical_failure": true/false,',
        '  "reasoning": "Detailed explanation of evaluation...",',
        '  "condition_results": {',
        '    "condition_1": {"met": true/false, "notes": "..."},',
        '    "condition_2": {"met": true/false, "notes": "..."}',
        "  }",
        "}",
        "```",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Automated Checks
# ---------------------------------------------------------------------------
def check_module_structure(module_path: Path) -> dict:
    """
    Check if an Odoo module has the expected OCA structure.
    """
    results = {
        "has_init": (module_path / "__init__.py").exists(),
        "has_manifest": (module_path / "__manifest__.py").exists(),
        "has_models": (module_path / "models").is_dir(),
        "has_views": (module_path / "views").is_dir(),
        "has_security": (module_path / "security").is_dir(),
        "has_tests": (module_path / "tests").is_dir(),
        "has_readme": (module_path / "README.rst").exists()
        or (module_path / "README.md").exists(),
    }
    results["structure_score"] = sum(results.values()) / len(results)
    return results


def check_manifest(module_path: Path) -> dict:
    """
    Check the __manifest__.py for required fields.
    """
    manifest_path = module_path / "__manifest__.py"
    if not manifest_path.exists():
        return {"valid": False, "error": "Manifest not found"}

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Safe eval for manifest dict
        manifest = eval(content, {"__builtins__": {}})

        required_fields = ["name", "version", "license", "depends"]
        missing = [f for f in required_fields if f not in manifest]

        # Check version format (18.0.x.x.x)
        version = manifest.get("version", "")
        version_valid = version.startswith("18.0.")

        # Check license (LGPL-3 or AGPL-3 preferred)
        license_value = manifest.get("license", "")
        license_valid = license_value in ["LGPL-3", "AGPL-3"]

        return {
            "valid": len(missing) == 0 and version_valid,
            "missing_fields": missing,
            "version": version,
            "version_valid": version_valid,
            "license": license_value,
            "license_valid": license_valid,
            "manifest": manifest,
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}


def check_security_files(module_path: Path) -> dict:
    """
    Check for security definitions.
    """
    security_dir = module_path / "security"
    results = {
        "has_acl": False,
        "has_record_rules": False,
        "has_groups": False,
    }

    if not security_dir.is_dir():
        return results

    for f in security_dir.iterdir():
        if f.name == "ir.model.access.csv":
            results["has_acl"] = True
        elif f.suffix == ".xml":
            content = f.read_text()
            if "ir.rule" in content:
                results["has_record_rules"] = True
            if "res.groups" in content:
                results["has_groups"] = True

    return results


def run_flake8(module_path: Path) -> dict:
    """
    Run flake8 on the module.
    """
    try:
        result = subprocess.run(
            ["flake8", str(module_path), "--max-line-length=120"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return {
            "passed": result.returncode == 0,
            "output": result.stdout + result.stderr,
            "error_count": len(result.stdout.strip().split("\n"))
            if result.stdout.strip()
            else 0,
        }
    except FileNotFoundError:
        return {"passed": None, "output": "flake8 not installed", "error_count": 0}
    except subprocess.TimeoutExpired:
        return {"passed": False, "output": "Timeout", "error_count": -1}


def run_tests(module_path: Path, odoo_bin: Path = None) -> dict:
    """
    Run Odoo tests for the module.
    """
    # This is a placeholder - actual implementation would require
    # a running Odoo instance or test database
    test_dir = module_path / "tests"
    if not test_dir.is_dir():
        return {"passed": False, "output": "No tests directory", "test_count": 0}

    test_files = list(test_dir.glob("test_*.py"))
    return {
        "passed": None,  # Would need actual test run
        "output": f"Found {len(test_files)} test file(s)",
        "test_count": len(test_files),
        "test_files": [f.name for f in test_files],
    }


# ---------------------------------------------------------------------------
# Stage Evaluators
# ---------------------------------------------------------------------------
def evaluate_reference_module(stage: dict, weight: float) -> StageResult:
    """
    Evaluate a reference module against the stage criteria using automated checks.
    """
    stage_id = stage["stage"]
    label = stage.get("label", stage_id)
    module_rel_path = stage.get("reference_module_path", "")

    module_path = PROJECT_ROOT / module_rel_path
    if not module_path.exists():
        return StageResult(
            stage_id=stage_id,
            label=label,
            weight=weight,
            score=0.0,
            passed=False,
            reasoning=f"Reference module not found at {module_path}",
            critical_failure=True,
        )

    # Run automated checks
    structure = check_module_structure(module_path)
    manifest = check_manifest(module_path)
    security = check_security_files(module_path)
    lint = run_flake8(module_path)
    tests = run_tests(module_path)

    automated_checks = {
        "structure": structure,
        "manifest": manifest,
        "security": security,
        "lint": lint,
        "tests": tests,
    }

    # Calculate score based on checks
    scores = []

    # Structure (20%)
    scores.append(structure.get("structure_score", 0) * 0.20)

    # Manifest (20%)
    if manifest.get("valid"):
        manifest_score = 1.0
        if not manifest.get("license_valid"):
            manifest_score -= 0.2
        scores.append(manifest_score * 0.20)
    else:
        scores.append(0)

    # Security (25%)
    sec_score = sum(
        [security.get("has_acl", False), security.get("has_record_rules", False)]
    ) / 2
    scores.append(sec_score * 0.25)

    # Lint (15%)
    if lint.get("passed") is True:
        scores.append(0.15)
    elif lint.get("passed") is None:  # Not installed
        scores.append(0.10)  # Partial credit
    else:
        scores.append(max(0, 0.15 - (lint.get("error_count", 10) * 0.01)))

    # Tests (20%)
    test_count = tests.get("test_count", 0)
    test_score = min(1.0, test_count * 0.25)  # 4+ test files = full score
    scores.append(test_score * 0.20)

    total_score = sum(scores)
    passed = total_score >= 0.7 and structure.get("has_manifest") and manifest.get("valid")

    reasoning_parts = [
        f"Structure: {structure.get('structure_score', 0):.0%}",
        f"Manifest valid: {manifest.get('valid', False)}",
        f"Has ACL: {security.get('has_acl', False)}",
        f"Lint passed: {lint.get('passed')}",
        f"Test files: {tests.get('test_count', 0)}",
    ]

    return StageResult(
        stage_id=stage_id,
        label=label,
        weight=weight,
        score=total_score,
        passed=passed,
        reasoning="; ".join(reasoning_parts),
        critical_failure=not structure.get("has_manifest", False),
        automated_checks=automated_checks,
    )


def evaluate_stage_with_judge(
    stage: dict,
    weight: float,
    agent_response: str,
    judge_fn: callable = None,
) -> StageResult:
    """
    Evaluate a stage using a judge model.

    In a real implementation, judge_fn would call an LLM (e.g., Claude)
    to evaluate the agent's response.
    """
    stage_id = stage["stage"]
    label = stage.get("label", stage_id)

    if judge_fn is None:
        # Mock judge for testing
        return StageResult(
            stage_id=stage_id,
            label=label,
            weight=weight,
            score=0.8,  # Placeholder
            passed=True,
            reasoning="Judge evaluation not configured - using mock result",
        )

    # Build judge prompt and call judge
    judge_prompt = build_judge_prompt(stage, agent_response)
    judge_response = judge_fn(judge_prompt)

    try:
        # Parse judge response (expecting JSON)
        result = json.loads(judge_response)
        return StageResult(
            stage_id=stage_id,
            label=label,
            weight=weight,
            score=result.get("score", 0.0),
            passed=result.get("passed", False),
            reasoning=result.get("reasoning", ""),
            critical_failure=result.get("critical_failure", False),
        )
    except json.JSONDecodeError:
        return StageResult(
            stage_id=stage_id,
            label=label,
            weight=weight,
            score=0.0,
            passed=False,
            reasoning=f"Failed to parse judge response: {judge_response[:200]}",
            critical_failure=False,
        )


# ---------------------------------------------------------------------------
# Main Eval Runner
# ---------------------------------------------------------------------------
def run_certification_eval(
    agent_responses: dict[str, str] = None,
    judge_fn: callable = None,
) -> ExamResult:
    """
    Run the full certification evaluation.

    Args:
        agent_responses: Dict mapping stage_id to agent's response text
        judge_fn: Function to call judge model (takes prompt, returns response)

    Returns:
        ExamResult with scores and pass/fail status
    """
    cert = load_certification()
    exam = cert.get("certification_exam", {})
    stages = exam.get("stages", [])
    scoring_model = exam.get("scoring_model", {})
    passing_rule = exam.get("passing_rule", {})

    agent_responses = agent_responses or {}
    stage_results: list[StageResult] = []
    critical_failure_detected = False

    for stage in stages:
        stage_id = stage["stage"]
        weight = float(scoring_model.get(stage_id, 0))

        # Check if this is a reference module review stage
        if stage.get("reference_module_path"):
            result = evaluate_reference_module(stage, weight)
        else:
            agent_response = agent_responses.get(stage_id, "")
            result = evaluate_stage_with_judge(stage, weight, agent_response, judge_fn)

        stage_results.append(result)

        if result.critical_failure:
            critical_failure_detected = True

    # Calculate total weighted score
    total_weight = sum(scoring_model.values())
    weighted_score = sum(
        (sr.score * sr.weight / total_weight * 100) for sr in stage_results
    )

    # Determine pass/fail
    min_score = passing_rule.get("minimum_total_score", 92)
    no_critical = passing_rule.get("no_critical_failures_allowed", True)

    passed = weighted_score >= min_score
    if no_critical and critical_failure_detected:
        passed = False

    # Build summary
    summary_lines = [
        f"Total Score: {weighted_score:.1f}% (minimum: {min_score}%)",
        f"Passed: {passed}",
        f"Critical Failures: {'Yes' if critical_failure_detected else 'No'}",
        "",
        "Stage Results:",
    ]
    for sr in stage_results:
        status = "PASS" if sr.passed else "FAIL"
        if sr.critical_failure:
            status = "CRITICAL FAIL"
        summary_lines.append(
            f"  - {sr.stage_id}: {sr.score:.0%} ({status}) - {sr.reasoning[:50]}..."
        )

    return ExamResult(
        total_score=weighted_score,
        passed=passed,
        stage_results=stage_results,
        critical_failure_detected=critical_failure_detected,
        summary="\n".join(summary_lines),
    )


# ---------------------------------------------------------------------------
# CLI Interface
# ---------------------------------------------------------------------------
def main():
    """Run eval from command line."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Odoo 18 CE/OCA Custom Dev Certification Eval Runner"
    )
    parser.add_argument(
        "--module",
        "-m",
        help="Path to module to evaluate (for reference_module_review stage)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="eval_results.json",
        help="Output file for results",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Odoo 18 CE/OCA Custom Module Developer Certification")
    print("=" * 60)

    # Load and show cert info
    cert = load_certification()
    print(f"\nCertification: {cert['certification']['name']}")
    print(f"Level: {cert['certification']['level']}")
    print(f"Passing Score: {cert['certification_exam']['passing_score_percent']}%")

    # Run evaluation
    result = run_certification_eval()

    print("\n" + result.summary)

    # Save detailed results
    output_data = {
        "total_score": result.total_score,
        "passed": result.passed,
        "critical_failure_detected": result.critical_failure_detected,
        "stages": [
            {
                "stage_id": sr.stage_id,
                "label": sr.label,
                "weight": sr.weight,
                "score": sr.score,
                "passed": sr.passed,
                "reasoning": sr.reasoning,
                "critical_failure": sr.critical_failure,
                "automated_checks": sr.automated_checks,
            }
            for sr in result.stage_results
        ],
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nDetailed results saved to: {args.output}")

    # Exit with appropriate code
    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
