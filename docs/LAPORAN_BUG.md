# Laporan Bug

Salin blok di bawah untuk setiap bug. Bagian **Akar masalah** wajib ditulis dengan kata-kata
sendiri dan memakai konsep dari *Crafting Interpreters* (sebutkan bab). Bagian ini diuji lisan.

---

## Bug 1: Keyword Peka Huruf Besar / Kecil

**Ditemukan oleh:** Ahmad Bukhori · **Diperbaiki oleh:** Ahmad Bukhori

**Gejala.** `tokenize("select id from t")` mengembalikan token pertama bertipe `IDENT` dengan nilai `'select'`. Menurut SPESIFIKASI.md §2.2, keyword tidak peka huruf besar/kecil dan nilai tokennya selalu dinormalisasi ke huruf besar, jadi yang diharapkan adalah `KEYWORD` dengan nilai `'SELECT'`. Akibat lanjutannya, parser tidak mengenali statement yang ditulis dengan keyword huruf kecil.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
select id from t
```

**Akar masalah.** Di `Lexer._word`, pengecekan `text in KEYWORDS` membandingkan teks apa adanya, sedangkan `KEYWORDS` berisi kata huruf besar. Kata `select` atau `Select` tidak pernah cocok, sehingga jatuh ke cabang `IDENT`. Aturan yang dilanggar: pencocokan keyword harus tidak peka huruf besar/kecil (§2.2).

**Perbaikan.** File `crud/lexer.py`, fungsi `Lexer._word`. Teks kata diubah ke huruf besar (`upper = text.upper()`), dicocokkan ke `KEYWORDS`, dan nilai token keyword memakai `upper`. Token `IDENT` tetap memakai teks asli karena normalisasi ke huruf kecil menjadi tugas parser (§2.2). Kata yang hanya diawali keyword (`selection`, `fromage`) tetap `IDENT` karena yang dicocokkan adalah seluruh kata hasil pemindaian. Alternatif yang dipertimbangkan: mengubah isi `KEYWORDS` menjadi huruf kecil dan membandingkan dengan `text.lower()`. Tidak dipilih karena nilai token tetap harus huruf besar sehingga perlu `upper()` juga, dan `KEYWORDS` adalah bagian API publik (§7) yang sebaiknya tidak berubah isinya.

**Test regresi.** `test_keyword_huruf_kecil_dan_campuran` di `tests/test_tambahan.py` (gagal sebelum perbaikan, lulus sesudahnya):

Test bawaan `tests/test_lexer.py::test_keyword_huruf_kecil` juga ikut lulus.

**Peran AI.** AI membantu menemukan lokasi bug dari output pytest dan potongan `_word`, serta mengusulkan perbaikannya. Verifikasi: menjalankan ulang pytest, memastikan `test_keyword_huruf_kecil` dan test regresi di atas lulus, dan memeriksa bahwa isi `KEYWORDS` memang huruf besar semua.

---

## Bug 3: `''` di dalam String Memotong String

**Ditemukan oleh:** Gebby Rizki Aditya · **Diperbaiki oleh:** Gebby Rizki Aditya

**Gejala.** `tokenize("'O''Brien'")` menghasilkan dua token `STRING` (`'O'` dan `'Brien'`). Menurut SPESIFIKASI.md §2.4, `''` di dalam string mewakili satu karakter kutip, jadi hasil yang benar adalah satu token bernilai `O'Brien`. Lexer tidak melaporkan error; yang protes adalah parser: `diharapkan ';' di akhir statement, ditemukan 'Brien'`.

**Reproduksi minimal.**

```sql
SELECT 'O''Brien' FROM t;
```

**Akar masalah.** Di `Lexer._string`, setiap `'` langsung dianggap penutup string. Padahal `'` bisa berarti penutup atau separuh dari `''`, dan keduanya hanya bisa dibedakan dengan mengintip karakter berikutnya tanpa mengonsumsinya (lookahead satu karakter, `_peek()`). Pola `peek` ini sama dengan scanner di *Crafting Interpreters* bab 4 (membedakan `!` dan `!=`), tetapi buku tidak menangani escape di string, jadi pola itu kami perluas. Akar masalah ada di lexer, sedangkan gejalanya muncul di parser.

**Perbaikan.** `crud/lexer.py`, fungsi `_string`: setelah membaca `'`, bila `_peek()` juga `'`, kutip kedua dikonsumsi dan satu `'` ditambahkan ke nilai, lalu pemindaian lanjut; bila bukan, string selesai. Alternatif yang ditolak: `replace("''", "'")` setelah string selesai, karena string sudah terpotong menjadi dua token sebelum sempat diganti.

**Test regresi.** Di `tests/test_tambahan.py`:
- `test_bug2_kutip_ganda_dalam_string_adalah_satu_karakter`: gagal sebelum perbaikan, lulus sesudahnya.
- `test_bug2_string_tidak_ditutup_setelah_kutip_ganda`: memastikan `'abc''` tetap `LexError` (§2.4). Test ini lulus sebelum dan sesudah perbaikan, berfungsi sebagai penjaga agar perbaikan tidak terlalu longgar.

**Peran AI.** AI membantu menunjukkan lokasi bug dan mengusulkan perbaikan `_string`. Saya memasang test lebih dulu dan memastikan gagal pada kode asli, memasang perbaikan, lalu menjalankan seluruh test untuk memastikan tidak ada yang rusak.

---

## Bug ?: Judul Singkat

**Ditemukan oleh:** Siapa · **Diperbaiki oleh:** Siapa

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
(sebutkan bagiannya).

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql

```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?

---
