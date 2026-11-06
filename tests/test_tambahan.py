"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""
from crud.lexer import tokenize, TokenType as T
import pytest
from crud.lexer import LexError

def test_keyword_huruf_kecil_dan_campuran():
    for src in ["select", "Select", "SELECT"]:
        tok = tokenize(src)[0]
        assert tok.type == T.KEYWORD and tok.value == "SELECT"

def test_ident_berawalan_keyword_tetap_ident():
    for src in ["selection", "fromage"]:
        assert tokenize(src)[0].type == T.IDENT

def test_bug3_kutip_ganda_dalam_string_adalah_satu_karakter():
    strings = [t for t in tokenize("'O''Brien'") if t.type == T.STRING]
    assert len(strings) == 1
    assert strings[0].value == "O'Brien"

def test_bug3_string_tidak_ditutup_setelah_kutip_ganda():
    with pytest.raises(LexError):
        tokenize("'abc''")