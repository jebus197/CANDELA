"""
Unit tests for the fast safety-regex layer.

Prerequisite:
    • Make sure an empty file exists at src/__init__.py
      (this tells Python that “src” is a package).
"""

from src.guardian_extended import regex_guard


def test_blocks_hex_key():
    bad = "leak 0x" + "a" * 64
    assert regex_guard(bad) == (False, "eth_private_key_hex")


def test_passes_clean_text():
    assert regex_guard("hello world")[0] is True
