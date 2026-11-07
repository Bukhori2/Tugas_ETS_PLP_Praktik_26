"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""

"""Test regresi untuk bug #1: keyword case-insensitive"""
import pytest
from crud import ast_nodes as ast
from crud.analyzer import analyze_statement
from crud.lexer import tokenize, LexError, TokenType as T
from crud.parser import parse_sql
from crud.resolver import Resolver

def one(sql):
    script = parse_sql(sql)
    assert script.errors == [], script.errors
    assert len(script.statements) == 1
    return script.statements[0]

def resolve(sql):
    script = parse_sql(sql)
    assert script.errors == [], script.errors
    return script, Resolver().resolve_script(script)


def colrefs(node):
    return [n for n in ast.iter_nodes(node) if isinstance(n, ast.ColumnRef)]


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


# ---- Bug 7: pencarian alias dari scope terluar (spesifikasi 4.3) ------------

def test_bug7_alias_subquery_menutupi_alias_luar():
    script, diags = resolve(
        "SELECT x.id FROM pelanggan x WHERE x.id IN (SELECT x.pelanggan_id FROM pesanan x)")
    dalam = [c for c in colrefs(script) if c.name == "pelanggan_id"][0]
    assert dalam.resolved == "pesanan"
    assert diags == []


def test_bug7_subquery_tetap_bisa_merujuk_alias_luar():
    script, diags = resolve(
        "SELECT p.id FROM pelanggan p WHERE EXISTS "
        "(SELECT 1 FROM pesanan o WHERE o.pelanggan_id = p.id)")
    assert all(c.resolved for c in colrefs(script))
    assert diags == []

# ---- TODO T2: kolom tanpa qualifier (spesifikasi 4.3) -----------------------

def test_t2_kolom_satu_tabel_di_resolve():
    script, _ = resolve("SELECT nama FROM pelanggan")
    assert colrefs(script)[0].resolved == "pelanggan"


def test_t2_kolom_ambigu_menghasilkan_warning():
    script, diags = resolve("SELECT nama FROM pelanggan p, pesanan o")
    assert colrefs(script)[0].resolved is None
    assert [d.level for d in diags] == ["warning"]
    assert "ambigu tanpa skema" in diags[0].message

# ---- Bug 8: scope DELETE tidak di-pop (spesifikasi 4.5) ---------------------

def test_bug8_alias_delete_tidak_bocor_ke_statement_berikutnya():
    _, diags = resolve("DELETE FROM sesi s WHERE s.id = 1; SELECT s.id FROM pengguna u")
    assert [d.level for d in diags] == ["error"]
    assert "'s'" in diags[0].message


def test_bug8_alias_select_tidak_bocor_ke_statement_berikutnya():
    _, diags = resolve("SELECT p.id FROM pelanggan p; SELECT p.id FROM pesanan o")
    assert [d.level for d in diags] == ["error"]

# ---- Bug 9: subquery di UPDATE ditandai U (spesifikasi 5) -------------------

def test_bug9_subquery_di_update_dihitung_read():
    sql = "UPDATE a SET x = (SELECT y FROM b) WHERE z IN (SELECT q FROM c)"
    assert analyze_statement(one(sql)) == {"a": {"U"}, "b": {"R"}, "c": {"R"}}


def test_bug9_subquery_di_delete_tetap_read():
    sql = "DELETE FROM a WHERE x IN (SELECT y FROM b)"
    assert analyze_statement(one(sql)) == {"a": {"D"}, "b": {"R"}}


# ---- Lima test kasus tepi ---------------------------------------------------

def test_tepi1_komentar_blok_berisi_bintang():
    # Berisiko: pencari penutup yang naif berhenti di '*' pertama, atau menganggap '/*'
    # di dalam komentar membuka komentar bersarang.
    toks = tokenize("/* a * b ** / /* c */ SELECT")
    assert [t.value for t in toks if t.type != T.EOF] == ["SELECT"]


def test_tepi2_and_di_between_milik_between():
    # Berisiko: AND di BETWEEN bisa dikira AND logika (batas atas harus additive, bukan expr).
    where = one("SELECT x FROM t WHERE a BETWEEN 1 AND 5 AND b = 2").where
    assert where.op == "AND"
    assert isinstance(where.left, ast.Between)


def test_tepi3_not_lebih_lemah_dari_perbandingan():
    # Berisiko: NOT yang diikat terlalu kuat menjadi (NOT a) = 1.
    where = one("SELECT x FROM t WHERE NOT a = 1 AND b = 2").where
    assert where.op == "AND"
    assert where.left.op == "NOT" and where.left.operand.op == "="


def test_tepi4_subquery_di_from_tidak_melihat_tabel_saudaranya():
    # Berisiko: bila di-resolve setelah scope luar dibuat, alias 't' bocor ke dalam (spesifikasi 4.4).
    _, diags = resolve("SELECT d.z FROM t JOIN (SELECT t.z FROM u) d ON 1 = 1")
    assert any(d.level == "error" and "'t'" in d.message for d in diags)


def test_tepi5_subquery_di_from_tanpa_alias_menghasilkan_warning():
    # Berisiko: subquery tanpa alias tidak bisa dirujuk dan tidak boleh diam-diam diterima.
    _, diags = resolve("SELECT 1 FROM (SELECT 1 FROM t)")
    assert [d.level for d in diags] == ["warning"]