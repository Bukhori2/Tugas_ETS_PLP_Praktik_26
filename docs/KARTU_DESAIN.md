# Kartu Desain

Tuliskan lima keputusan desain penting dalam pekerjaan kalian. Untuk tiap keputusan, sebutkan
alternatif yang ditolak dan alasannya. Contoh topik (boleh memilih yang lain):

- bagaimana parser membedakan `*` sebagai "semua kolom" dan sebagai perkalian;
- di mana dan bagaimana presedensi `AND`/`OR` dinyatakan;
- mengapa error recovery berhenti di `;`, bukan di keyword `SELECT` berikutnya;
- urutan pencarian scope dan akibatnya pada shadowing serta correlated subquery;
- mengapa kolom tanpa qualifier hanya dilihat di scope terdalam, dan apa kelemahannya;
- bagaimana implementasi `INSERT ... SELECT` atau komentar blok kalian.

| No | Keputusan | Alternatif yang ditolak | Alasan |
| --- | --- | --- | --- |
| 1 | Lexer selalu menghasilkan token `STAR` untuk `*`; parser yang membedakan artinya: `_select_list` menganggap `*` di awal sebagai semua kolom, `_multiplicative` menganggapnya perkalian, dan `_function_call` menerimanya sebagai `COUNT(*)`. | Lexer memutuskan arti `*` dari token sebelumnya, atau memakai dua jenis token. | Arti `*` bergantung pada posisi dalam grammar, sedangkan lexer tidak mengenal grammar. Menaruh keputusan di parser menjaga lexer tetap sederhana dan sesuai spesifikasi (`STAR` satu jenis token). |
| 2 | Presedensi dinyatakan lewat struktur pemanggilan: `_or`, `_and`, `_not`, `_comparison`, `_additive`, `_multiplicative`, `_unary`, `_primary`; tingkat yang lebih lemah memanggil yang lebih kuat. | Satu fungsi `_logical` untuk `AND` dan `OR`, atau precedence climbing dengan tabel prioritas. | Satu fungsi untuk dua tingkat membuat `OR` dan `AND` setara (bug 4). Precedence climbing berfungsi, tetapi struktur kode tidak lagi sejajar satu-satu dengan grammar dan tabel presedensi di spesifikasi. |
| 3 | Error recovery panic mode: `_synchronize` membuang token sampai dan termasuk `;` berikutnya, lalu parsing berlanjut. | Berhenti di keyword awal statement berikutnya (`SELECT`, `INSERT`, dan seterusnya), atau membuang seluruh sisa file. | `SELECT` juga muncul di dalam subquery, jadi bisa salah sinkron. Membuang seluruh sisa file menghilangkan statement valid sesudahnya (bug 5). `;` adalah batas statement yang pasti. |
| 4 | `Resolver._lookup` menelusuri `scope` lalu `scope.parent` dan memakai hasil pertama, sehingga alias di subquery menutupi alias luar (shadowing) dan subquery tetap bisa merujuk alias luar (correlated). Scope dibuat per `SELECT`, `UPDATE`, dan `DELETE`, dan di-pop setelah statement selesai. | Satu tabel alias rata untuk seluruh statement, atau mencari dari scope terluar lebih dulu. | Tabel rata tidak bisa membedakan `x` di subquery dan `x` di query luar (`audit.sql` baris 12-14). Mencari dari terluar menghasilkan resolusi yang salah (bug 7). Scope yang tidak di-pop bocor ke statement berikutnya (bug 8). |
| 5 | Kolom tanpa qualifier hanya dicari di scope terdalam: satu tabel berarti kolom milik tabel itu, lebih dari satu tabel berarti warning ambigu dan `resolved` tetap `None`. | Naik ke scope luar bila tidak ketemu, atau menebak tabel pertama. | Tanpa skema tidak ada cara tahu kolom milik tabel mana, jadi menebak lebih berbahaya daripada melapor ambigu. Kelemahannya: pada subquery dengan satu tabel, kolom tanpa qualifier yang sebenarnya milik query luar akan di-resolve ke tabel subquery, dan kolom pada scope multi-tabel tidak masuk keluaran `--kolom`. |
