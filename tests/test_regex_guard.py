from guardian_extended import regex_guard

def test_blocks_hex_key():
    bad = "leak 0x" + "a" * 64
    assert regex_guard(bad) == (False, "hex_key")

def test_passes_clean_text():
    assert regex_guard("hello world")[0] is True
