#!/usr/bin/env python3
"""Basic PUBLIC-REPOSITORY safety scan (not a substitute for human review).

Scans text files for likely real emails, IPs, Tailscale domains, MACs,
private key material, credential assignments and accidental local env files.
It accepts only explicit documentation placeholders / synthetic test fixtures.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {'.git', '__pycache__', '.pytest_cache', 'node_modules'}
TEXT_EXTENSIONS = {'.md', '.mmd', '.py', '.ps1', '.sh', '.yml', '.yaml', '.example', '.txt', '.gitignore', '.gitattributes'}
EXPECTED_TEXT_NAMES = {'LICENSE', 'README.md', '.gitignore', '.gitattributes'}

PATTERNS = {
    'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
    'ipv4': re.compile(r'(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])'),
    'tailnet_dns': re.compile(r'\b[A-Za-z0-9][\w-]*\.[\w-]+\.ts\.net\b', re.I),
    'mac': re.compile(r'\b(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b'),
    'private_key': re.compile(r'-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----'),
    'auth_token': re.compile(r'\b(?:tskey-(?:auth|client|api)-)[A-Za-z0-9-]+\b'),
}

# Synthetic fixtures only; no actual user device information.
ALLOWED_EXAMPLE_IP = {'255.255.255.255'}
ALLOWED_EXAMPLE_MAC = {
    'aa:bb:cc:dd:ee:ff', 'AA-BB-CC-DD-EE-FF',
    '00:11:22:33:44:55',
}


def examine(path: Path) -> list[str]:
    errors: list[str] = []
    relative = path.relative_to(ROOT).as_posix()
    contents = path.read_text(encoding='utf-8')
    for lineno, line in enumerate(contents.splitlines(), 1):
        for kind, pattern in PATTERNS.items():
            for found in pattern.finditer(line):
                value = found.group(0)
                if kind == 'ipv4' and value in ALLOWED_EXAMPLE_IP:
                    continue
                if kind == 'mac' and relative in ('tests/test_wake_pc.py', 'tools/check_public_repo.py') and value in ALLOWED_EXAMPLE_MAC:
                    continue
                if kind == 'tailnet_dns' and 'YOUR_TAILNET.ts.net' in value:
                    continue
                errors.append(f'{relative}:{lineno}: possible private {kind} ({value if kind not in ("auth_token", "private_key") else "[REDACTED]"})')
        # Never include secrets as literal assignments in tracked text.
        match = re.search(r'^\s*(?:DB_PASSWORD|IMMICH_API_KEY|API_KEY|TAILSCALE_AUTH_KEY)\s*=\s*(.*?)\s*$', line)
        if match:
            value = match.group(1).strip().strip('\"\'')
            # only safely named placeholder tokens are allowed
            if not (value.startswith('REPLACE_WITH_') or value in ('', '${API_KEY}', '${DB_PASSWORD}')):
                errors.append(f'{relative}:{lineno}: non-placeholder secret assignment')
    return errors


def main() -> int:
    errors: list[str] = []
    for path in ROOT.rglob('*'):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if path.name == '.env' or path.name.endswith('.env.local') or path.name == 'wol.env' or path.name == 'docker-compose.yml':
            errors.append(f'{relative}: local configuration should not be committed')
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS or path.name in EXPECTED_TEXT_NAMES or path.name.startswith('.env.example'):
            errors.extend(examine(path))
        else:
            errors.append(f'{relative}: unrecognized/binary file, review before publication')
    if errors:
        print('Public repository check FAILED:')
        for error in errors:
            print(' -', error)
        return 1
    print('PASS: no obvious personal details or active secrets detected. Manual review still required.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
