#!/usr/bin/env python3
import secrets
import string
import argparse

SEPARATOR = "=" * 44

def build_charset():
    # All printable characters except whitespace
    return string.ascii_letters + string.digits + string.punctuation

def generate_password(length: int) -> str:
    if length < 32:
        raise ValueError("Minimal 32 karakter.")
    charset = build_charset()
    return ''.join(secrets.choice(charset) for _ in range(length))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Secure password generator (full printable, default 512 chars)"
    )
    parser.add_argument(
        "-l", "--length",
        type=int,
        default=44,
        help="Panjang password (default: 512)"
    )

    args = parser.parse_args()
    password = generate_password(args.length)

    print(SEPARATOR)
    print(password)
    print(SEPARATOR)
