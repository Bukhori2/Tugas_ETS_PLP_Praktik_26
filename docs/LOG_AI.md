# Log Penggunaan AI

Catat setiap penggunaan AI atau coding agent yang memengaruhi kode atau laporan.

| No | Siapa | Prompt / tugas (ringkas) | Hasil: diterima, diubah, atau ditolak | Alasan | Cara verifikasi |
| --- | --- | --- | --- | --- | --- |
| 1 | Ahmad Bukhori | Mengoreksi output kegagalan pytest untuk mengidentifikasi lokasi dan penyebab error. | Diterima | AI berhasil membedah struktur pesan error pytest dan menunjukkan lokasi spesifik kesalahan | Memeriksa langsung file sumber kode di baris dan kolom yang ditunjuk oleh AI |
| 2 | Gebby Rizki Aditya | Meminta AI mencari penyebab `'O''Brien'` terpotong, usulan perbaikan `_string` dan penjelasan code yang diberikan. | Diterima, test disederhanakan jadi dua | Penyebab (tiap `'` dianggap penutup) dan lookahead `_peek()` sesuai §2.4 | Test dipasang dulu (gagal), perbaikan dipasang (lulus), lalu seluruh test dijalankan |
| 3 | Gebby Rizki Aditya | Meminta AI mencari penyebab presedensi AND/OR salah dan usulan perbaikan (bug 4). | Diterima | Sesuai tabel presedensi §3.1 | Test dipasang dulu (gagal), perbaikan dipasang (lulus), lalu seluruh test dijalankan |

**Refleksi (3-5 kalimat).** Di bagian mana AI paling membantu? Di mana AI keliru atau
menyesatkan, dan bagaimana kalian mengetahuinya?
