"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""

"""Test regresi untuk bug #1: keyword case-insensitive"""
from crud.lexer import tokenize, TokenType as T
import pytest
from crud.lexer import LexError
from crud.parser import parse_sql

def test_keyword_huruf_kecil_dan_campuran():
    for src in ["select", "Select", "SELECT"]:
        tok = tokenize(src)[0]
        assert tok.type == T.KEYWORD and tok.value == "SELECT"

def test_ident_berawalan_keyword_tetap_ident():
    for src in ["selection", "fromage"]:
        assert tokenize(src)[0].type == T.IDENT

"""Test regresi untuk bug #2: token operator terpanjang"""
def test_operator_terpanjang():
    for src in ["<>", "<=", ">=", "!="]:
        toks = tokenize(src)
        assert [t.value for t in toks[:-1]] == [src]

def test_not_equal_diparse():
    script = parse_sql("SELECT * FROM t WHERE a <> 1")
    assert script.errors == []

def test_bug3_kutip_ganda_dalam_string_adalah_satu_karakter():
    strings = [t for t in tokenize("'O''Brien'") if t.type == T.STRING]
    assert len(strings) == 1
    assert strings[0].value == "O'Brien"

def test_bug3_string_tidak_ditutup_setelah_kutip_ganda():
    with pytest.raises(LexError):
        tokenize("'abc''")