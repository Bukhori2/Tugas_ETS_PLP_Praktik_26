# Log Penggunaan AI

Catat setiap penggunaan AI atau coding agent yang memengaruhi kode atau laporan.

| No | Siapa | Prompt / tugas (ringkas) | Hasil: diterima, diubah, atau ditolak | Alasan | Cara verifikasi |
| --- | --- | --- | --- | --- | --- |
| 1 | Ahmad Bukhori | Mengoreksi output kegagalan pytest untuk mengidentifikasi lokasi dan penyebab error. | Diterima | AI berhasil membedah struktur pesan error pytest dan menunjukkan lokasi spesifik kesalahan | Memeriksa langsung file sumber kode di baris dan kolom yang ditunjuk oleh AI |
| 2 | Ahmad Bukhori | Meminta AI mencari penyebab `<>` terpecah dan usulan perbaikan (bug 2). | Diterima | Sesuai aturan maximal munch 2.5 | Test dipasang dulu (gagal), perbaikan dipasang (lulus), lalu seluruh test dijalankan |
| 3 | Gebby Rizki Aditya | Meminta AI mencari penyebab `'O''Brien'` terpotong, usulan perbaikan `_string` dan penjelasan code yang diberikan. | Diterima, test disederhanakan jadi dua | Penyebab (tiap `'` dianggap penutup) dan lookahead `_peek()` sesuai 2.4 | Test dipasang dulu (gagal), perbaikan dipasang (lulus), lalu seluruh test dijalankan |
| 4 | Gebby Rizki Aditya | Meminta AI mencari penyebab presedensi AND/OR salah dan usulan perbaikan (bug 4). | Diterima | Sesuai tabel presedensi 3.1 | Test dipasang dulu (gagal), perbaikan dipasang (lulus), lalu seluruh test dijalankan |
| 5 | Gebby Rizki Aditya | Meminta AI mencari penyebab statement setelah error hilang dan usulan perbaikan (bug 5). | Diterima | Sesuai aturan error recovery 6 | Test dipasang dulu (gagal), perbaikan dipasang (lulus), lalu seluruh test dijalankan |
| 6 | Ahmad Bukhori | Meminta AI mencari penyebab statement `LEFT OUTER JOIN` ditolak dan usulan perbaikan (bug 6). | Diterima | Sesuai aturan error recovery 6 | Test dipasang dulu (gagal), perbaikan dipasang (lulus), lalu seluruh test dijalankan |
| 7 | Gebby Rizki Aditya | Meminta AI mencari penyebab alias subquery salah resolve dan usulan perbaikan (bug 7). | Diterima | Sesuai aturan resolusi 4.3 | Test dipasang dulu (gagal), perbaikan dipasang (lulus), lalu seluruh test dijalankan |
| 8 | Ahmad Bukhori | Meminta AI mencari penyebab alias subquery salah resolve dan usulan perbaikan (bug 7). | Diterima | Sesuai aturan resolusi §4.3 | Test dipasang dulu (gagal), perbaikan dipasang (lulus), lalu seluruh test dijalankan |


**Refleksi (3-5 kalimat).** Di bagian mana AI paling membantu? Di mana AI keliru atau
menyesatkan, dan bagaimana kalian mengetahuinya?

AI paling membantu dalam membaca keluaran pytest dan menunjuk lokasi penyebabnya: dari pesan
`ditemukan '>'` ke cabang `<` di lexer, dan dari `TypeError: 'NoneType' object is not iterable`
ke `values` yang bernilai `None` pada `INSERT ... SELECT`, serta mengingatkan bahwa bug yang sama
akan muncul di resolver lalu analyzer. AI keliru ketika belum melihat kode kami: ia menebak nama
fungsi dan field (misalnya `_parse_select`, `InsertStmt`, `self.scopes`, `rows=[]`), padahal kode
memakai `_select`, `ast.Insert`, `self.scope`, dan `values=None`, sehingga saran tidak bisa
ditempel mentah-mentah. Kami mengetahuinya karena kode saran tidak cocok dengan file sumber dan
pytest tetap gagal sampai kami menyesuaikannya sendiri. Karena itu setiap usulan AI kami uji
dengan test yang gagal lebih dulu, lalu seluruh test dijalankan.