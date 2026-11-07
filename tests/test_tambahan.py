"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""

"""Test regresi untuk bug #1: keyword case-insensitive"""
import pytest
from crud.lexer import tokenize, LexError, TokenType as T
from crud.parser import parse_sql
from crud.pipeline import analyze_source

def one(sql):
    script = parse_sql(sql)
    assert script.errors == [], script.errors
    assert len(script.statements) == 1
    return script.statements[0]



# ---- Bug 1: keyword peka huruf besar/kecil (spesifikasi 2.2) ---------------

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

# ---- Bug 3: '' di dalam string memotong string (spesifikasi 2.4) ------------

def test_bug3_kutip_ganda_dalam_string_adalah_satu_karakter():
    strings = [t for t in tokenize("'O''Brien'") if t.type == T.STRING]
    assert len(strings) == 1
    assert strings[0].value == "O'Brien"

def test_bug3_string_tidak_ditutup_setelah_kutip_ganda():
    with pytest.raises(LexError):
        tokenize("'abc''")

# ---- TODO T3: komentar blok (spesifikasi 2.3) -------------------------------

def test_t3_komentar_blok_tidak_menghasilkan_token():
    toks = tokenize("/* baris satu\n   baris dua */ SELECT")
    assert [(t.value, t.line) for t in toks if t.type != T.EOF] == [("SELECT", 2)]


def test_t3_komentar_blok_tidak_ditutup_adalah_lexerror():
    with pytest.raises(LexError):
        tokenize("SELECT 1 /* belum ditutup")

# ---- Bug 4: AND dan OR di tingkat presedensi yang sama (spesifikasi 3.1) ----

def test_bug4_and_lebih_kuat_dari_or():
    where = one("SELECT x FROM t WHERE a = 1 OR b = 2 AND c = 3").where
    assert where.op == "OR"
    assert where.right.op == "AND"


def test_bug4_or_asosiatif_kiri_dan_and_tetap_lebih_kuat():
    where = one("SELECT x FROM t WHERE a = 1 OR b = 2 AND c = 3 OR d = 4").where
    assert where.op == "OR" and where.left.op == "OR"
    assert where.left.right.op == "AND"

# ---- Bug 5: error recovery membuang sisa file (spesifikasi 6) ---------------

def test_bug5_statement_valid_setelah_error_tetap_diproses():
    script = parse_sql("SELECT FROM a; SELECT x FROM b; UPDATE c SET y = 1;")
    assert len(script.errors) == 1
    assert [type(s).__name__ for s in script.statements] == ["Select", "Update"]


def test_bug5_dua_statement_rusak_menghasilkan_dua_error():
    script = parse_sql("SELECT FROM a; SELECT x FROM b; DELETE t; DELETE FROM c")
    assert len(script.errors) == 2
    assert [type(s).__name__ for s in script.statements] == ["Select", "Delete"]

# ---- Bug 6: LEFT OUTER JOIN ditolak (spesifikasi 3, aturan join) ------------

def test_bug6_left_outer_join_diterima():
    s = one("SELECT a.id FROM a LEFT OUTER JOIN b ON b.a_id = a.id")
    assert s.joins[0].kind == "LEFT"


def test_bug6_join_biasa_tetap_diterima():
    for jenis in ["JOIN", "INNER JOIN", "LEFT JOIN"]:
        one(f"SELECT a.id FROM a {jenis} b ON b.a_id = a.id")