# Laporan Akhir

## 1. Hasil evaluasi

Tempel keluaran `python evaluate.py` setelah `data/ground_truth.csv` dilengkapi.

```text

Dievaluasi: audit.sql, campuran_error.sql, laporan_penjualan.sql, pemeliharaan.sql (27 triple)

Metode   Precision  Recall     F1
parser        1.00    1.00   1.00
regex         0.65    0.81   0.72

[regex]
  salah ditemukan (FP): ('audit.sql', 16, 'sesi', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 4, 'pesanan', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 8, 'keranjang', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'D')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pesanan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'rahasia', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 15, 'pesanan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.alamat', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.pelanggan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'pelanggan_lama', 'U')
  salah ditemukan (FP): ('pemeliharaan.sql', 15, 'crm.alamat', 'R')
  terlewat (FN):       ('audit.sql', 2, 'pesanan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pelanggan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pesanan', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.alamat', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.pelanggan', 'R')

```

## 2. Tiga kasus di mana regex salah

Untuk tiap kasus: SQL-nya, kesalahan regex, dan mengapa parser benar (kaitkan dengan konsep
lexing, parsing, atau resolusi).

1. **Komentar dan string (lexing).** `laporan_penjualan.sql` baris 2-7:

   ```sql
   -- DELETE FROM pelanggan   (baris ini komentar, bukan perintah)
   SELECT p.nama, SUM(o.total) AS omzet
   FROM pelanggan p
   JOIN pesanan o ON o.pelanggan_id = p.id
   WHERE o.status = 'LUNAS' AND o.catatan <> 'FROM rahasia'
   GROUP BY p.nama;
   ```

   *Kesalahan regex.* Teks dipotong di `;`, lalu kata kunci pertama dicari mentah-mentah. `DELETE` di dalam komentar dianggap awal statement, sehingga seluruh statement diberi nomor baris 2 (bukan 3), `DELETE FROM pelanggan` dihitung sebagai `D`, dan `'FROM rahasia'` di dalam string dianggap tabel `rahasia`. Hasilnya empat FP di baris 2 dan dua FN di baris 3. Komentar blok di `pemeliharaan.sql` (`UPDATE pelanggan_lama`) menghasilkan kesalahan yang sama.

   *Mengapa parser benar.* Lexer membuang komentar (tidak menghasilkan token) dan memindai `'...'` sebagai satu token `STRING`, sehingga isinya tidak pernah menjadi `KEYWORD` atau `IDENT`. Parser hanya melihat urutan token yang sudah bersih. Ini konsep scanner pada *Crafting Interpreters* bab 4: teks diubah menjadi lexeme, komentar dibuang, dan literal string dipindai utuh.
2.**Daftar tabel dengan koma dan `DELETE FROM` (parsing).** `audit.sql` baris 2-3 dan 16:

   ```sql
   SELECT p.id, p.nama
   FROM pelanggan p, pesanan o
   ...
   DELETE FROM sesi s WHERE s.kedaluwarsa < :sekarang;
   ```

   *Kesalahan regex.* Pola `FROM <nama>` hanya mengambil satu nama, jadi `pesanan` terlewat (FN `audit.sql, 2, pesanan, R`). Pola yang sama juga cocok di dalam `DELETE FROM sesi`, sehingga `sesi` dihitung `R` selain `D` (FP); hal serupa terjadi pada `DELETE FROM keranjang` di `campuran_error.sql` baris 8.

   *Mengapa parser benar.* Grammar `FROM table_ref { "," table_ref }` diwujudkan sebagai loop `while self._match(T.COMMA)` di `Parser._select`, sedangkan `DELETE FROM` ditangani `Parser._delete` dan analyzer memberi tabel targetnya hanya `D`. Parser mengikuti struktur statement (*Crafting Interpreters* bab 5-6: satu fungsi per aturan grammar), sedangkan regex hanya mencocokkan pola dangkal dan tidak tahu `FROM` milik statement jenis apa.
3. **Statement yang rusak (parsing dan error recovery).** `campuran_error.sql` baris 4:

   ```sql
   SELECT id nama, FROM pesanan;
   ```

   *Kesalahan regex.* `pesanan` tetap dihitung `R` (FP `campuran_error.sql, 4, pesanan, R`), padahal menurut spesifikasi bagian 5 statement yang gagal di-parse tidak dihitung. Regex tidak punya konsep statement yang valid.

   *Mengapa parser benar.* Setelah koma, `_select_list` mengharapkan ekspresi dan menemukan `FROM`, sehingga muncul satu `ParseError` ("Baris 4, kolom 17: diharapkan ekspresi, ditemukan 'FROM'"). Statement itu dibuang dengan panic mode sampai `;` (*Crafting Interpreters* bab 6, sinkronisasi), tidak masuk matrix, dan `UPDATE produk` serta `DELETE FROM keranjang` sesudahnya tetap diproses.

## 3. Batas pendekatan kami

Minimal tiga hal yang **tidak bisa** ditangani dengan benar oleh tool ini meskipun semua bug
sudah diperbaiki. Untuk tiap batas: contoh SQL atau situasinya, akibatnya pada CRUD matrix,
dan informasi apa yang dibutuhkan untuk mengatasinya.

1. **Kolom tanpa qualifier di scope dengan lebih dari satu tabel.**
   Contoh: `SELECT nama FROM pelanggan p, pesanan o`. Resolver hanya memberi warning `kolom 'nama' ambigu tanpa skema`, `resolved` tetap `None`, dan kolom itu tidak muncul di keluaran `--kolom`. Matrix tabel tetap benar, tetapi pemakaian kolom tidak lengkap.
   Dibutuhkan: skema database (daftar kolom per tabel), yang sengaja tidak dipakai tool ini (SPESIFIKASI.md bagian 7, poin 4).
2. **Efek yang tidak tertulis di teks query: view, cascade, trigger.**
   `SELECT * FROM v_pelanggan` dicatat sebagai tabel `v_pelanggan` dengan `R`, padahal view itu mungkin membaca `pelanggan` dan `alamat`. `DELETE FROM pelanggan WHERE id = :id` dicatat `pelanggan: D` saja, padahal `ON DELETE CASCADE` atau trigger bisa menghapus baris di `pesanan`. Akibatnya matrix kurang lengkap (tabel yang terdampak tidak tercatat).
   Dibutuhkan: definisi view, aturan foreign key, dan definisi trigger dari database.
3. **Konstruk di luar lingkup (bagian 9): CTE dan `UNION`.**
   `WITH x AS (SELECT id FROM a) SELECT id FROM x` menghasilkan satu `ParseError` ("diharapkan awal statement ... ditemukan 'WITH'"), dan `SELECT id FROM a UNION SELECT id FROM b` menghasilkan error ("diharapkan ';' di akhir statement, ditemukan 'SELECT'"). Pada kedua kasus statement tidak dihitung, sehingga tabel `a` dan `b` hilang dari matrix (false negative). 
   Dibutuhkan: perluasan grammar (`WITH`, `UNION`) dan aturan scope untuk nama CTE, supaya nama CTE tidak dihitung sebagai tabel.
4. **`LexError` menghentikan seluruh file.**
   Quoted identifier (di luar lingkup) seperti `SELECT "nama" FROM b;` menghasilkan `LexError: karakter tidak dikenal '"'`. Karena lexing dijalankan untuk seluruh file lebih dulu, statement valid sebelumnya (`SELECT id FROM a;`) ikut hilang: `statements` kosong dan matrix kosong. Akibatnya satu karakter asing menghapus seluruh kontribusi file itu. 
   Dibutuhkan: dukungan dialek (sintaks quoted identifier) atau lexer yang bisa pulih dari error, yang berbeda dari aturan spesifikasi bagian 2.7.
5. **SQL yang tidak ada sebagai file SQL.**
   Query yang dibangun di kode aplikasi lewat penggabungan string atau ORM, atau nama tabel yang baru diketahui saat runtime, tidak pernah dilihat tool karena inputnya hanya file `.sql`.
   Dibutuhkan: analisis kode aplikasi atau log query saat runtime.

## 4. Pembagian kerja

Siapa mengerjakan apa, dan bagaimana kalian memastikan keduanya memahami seluruh kode.

Pembagian berdasarkan `docs/LAPORAN_BUG.md`: Ahmad Bukhori menemukan bug 1, 2, 5, dan 8 serta memperbaiki bug 1, 2, 6, 8, dan 9. Gebby Rizki Aditya menemukan bug 3, 4, 6, 7, dan 9 serta memperbaiki bug 3, 4, 5, dan 7. Pada bug 5, 6, dan 9 penemu bug dan orang yang memperbaikinya berbeda, sehingga masing-masing membaca dan mengubah kode yang bukan ditemukannya sendiri:
Ahmad menyentuh lexer, parser, resolver, dan analyzer sedangkan Gebby menyentuh lexer, parser, dan resolver, serta menemukan bug di analyzer.

Setiap bug dikerjakan dengan prosedur yang sama: test dipasang lebih dulu dan dipastikan gagal pada kode asli, perbaikan dipasang, lalu seluruh test dijalankan (tercatat di `docs/LOG_AI.md`).