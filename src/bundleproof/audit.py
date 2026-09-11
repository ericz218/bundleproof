from __future__ import annotations

import fnmatch
import os
import plistlib
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    rule: str
    level: str
    message: str
    path: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def _finding(rule: str, level: str, message: str, path: Path) -> Finding:
    return Finding(rule, level, message, str(path))


def _check_required(root: Path, patterns: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    candidates = [str(path.relative_to(root)) for path in root.rglob("*")]
    for pattern in patterns:
        if not any(fnmatch.fnmatch(candidate, pattern) for candidate in candidates):
            findings.append(_finding("BP001", "error", f"Required path is missing: {pattern}", root))
    return findings


def _check_empty_files(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in root.rglob("*"):
        if path.is_file() and not path.is_symlink() and path.stat().st_size == 0:
            findings.append(_finding("BP002", "warning", "File is empty", path))
    return findings


def _check_app(app: Path) -> list[Finding]:
    findings: list[Finding] = []
    plist_path = app / "Contents" / "Info.plist"
    if not plist_path.is_file():
        return [_finding("BP101", "error", "macOS app is missing Contents/Info.plist", plist_path)]

    try:
        with plist_path.open("rb") as stream:
            info = plistlib.load(stream)
    except (OSError, plistlib.InvalidFileException) as exc:
        return [_finding("BP102", "error", f"Info.plist is invalid: {exc}", plist_path)]

    executable_name = info.get("CFBundleExecutable")
    if not isinstance(executable_name, str) or not executable_name:
        findings.append(_finding("BP103", "error", "CFBundleExecutable is missing", plist_path))
    else:
        executable = app / "Contents" / "MacOS" / executable_name
        if not executable.is_file():
            findings.append(_finding("BP104", "error", "Declared bundle executable is missing", executable))
        elif not os.access(executable, os.X_OK):
            findings.append(_finding("BP105", "error", "Bundle executable is not executable", executable))

    if sys.platform == "darwin" and shutil.which("codesign"):
        result = subprocess.run(
            ["codesign", "--verify", "--deep", "--strict", str(app)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            detail = (result.stderr or result.stdout).strip().splitlines()
            message = "Bundle signature verification failed"
            if detail:
                message += f": {detail[-1]}"
            findings.append(_finding("BP106", "error", message, app))
    return findings


def audit(path: Path, required: list[str] | None = None) -> list[Finding]:
    if not path.exists():
        return [_finding("BP000", "error", "Artifact does not exist", path)]
    if not path.is_dir():
        return [_finding("BP000", "error", "Artifact must be a directory or .app bundle", path)]

    findings = _check_required(path, required or [])
    findings.extend(_check_empty_files(path))
    if path.suffix.lower() == ".app":
        findings.extend(_check_app(path))
    return findings

