from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .audit import Finding, audit


def _sarif(findings: list[Finding]) -> dict:
    rules = sorted({finding.rule for finding in findings})
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": "BundleProof",
                "version": __version__,
                "rules": [{"id": rule, "shortDescription": {"text": rule}} for rule in rules],
            }},
            "results": [{
                "ruleId": item.rule,
                "level": item.level,
                "message": {"text": item.message},
                "locations": [{"physicalLocation": {"artifactLocation": {"uri": item.path}}}],
            } for item in findings],
        }],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bundleproof", description="Audit packaged desktop applications before release.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="audit an artifact directory or .app bundle")
    check.add_argument("path", type=Path)
    check.add_argument("--require", action="append", default=[], metavar="GLOB", help="required relative path or glob; repeatable")
    check.add_argument("--format", choices=("text", "json", "sarif"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    findings = audit(args.path, args.require)
    if args.format == "json":
        print(json.dumps([item.as_dict() for item in findings], indent=2))
    elif args.format == "sarif":
        print(json.dumps(_sarif(findings), indent=2))
    elif findings:
        for item in findings:
            print(f"{item.level.upper():7} {item.rule} {item.path}: {item.message}")
    else:
        print(f"PASS    {args.path}")
    return int(any(item.level == "error" for item in findings))


if __name__ == "__main__":
    raise SystemExit(main())

