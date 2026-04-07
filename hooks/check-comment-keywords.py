"""Check that Python comments do not contain banned keywords.

Tokenizes Python files and checks each comment token for occurrences of
banned keywords. Reports file, line, and the matched keyword for each
violation.
"""

from __future__ import annotations

import argparse
import sys
import tokenize


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Python comments do not contain banned keywords.",
    )
    parser.add_argument(
        "--keyword",
        action="append",
        required=True,
        dest="keywords",
        help="Keyword to ban from comments. Can be repeated.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Python files to check.",
    )
    args = parser.parse_args()

    keywords: list[str] = args.keywords
    violations: list[str] = []

    for filepath in args.files:
        violations.extend(_check_file(filepath, keywords))

    if violations:
        print("ERROR: Banned comment keyword(s) found:", file=sys.stderr)
        for v in violations:
            print(v, file=sys.stderr)
        return 1

    print("No banned comment keywords found.")
    return 0


def _check_file(filepath: str, keywords: list[str]) -> list[str]:
    violations: list[str] = []
    try:
        with open(filepath, "rb") as f:
            for tok in tokenize.tokenize(f.readline):
                if tok.type == tokenize.COMMENT:
                    for keyword in keywords:
                        if keyword in tok.string:
                            violations.append(
                                f"  {filepath}:{tok.start[0]}: "
                                f"Found banned comment keyword '{keyword}'"
                            )
    except (SyntaxError, tokenize.TokenError, UnicodeDecodeError):
        pass
    return violations


if __name__ == "__main__":
    raise SystemExit(main())
