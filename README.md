# Website Pribadi Berbasis Django Framework

## Deskripsi

Ini adalah kode sumber blog baru saya: [prasetyadi.name](https://prasetyadi.name/). Proyek web ini juga dapat digunakan dan dimodifikasi oleh siapapun yang tertarik melakukannya. Perlu diingat bahwa web hosting yang mendukung _environment_ Python tidak banyak, seringkali memerlukan konfigurasi ekstra, dan biayanya lebih mahal dari web hosting biasa (yang umumnya hanya mendukung PHP).

File README ini sengaja ditulis hanya dalam bahasa Indonesia.

## Detail

Konten sebuah artikel dapat disusun dengan menggunakan sintaks Markdown ([link ke dokumentasi](https://www.markdownguide.org/cheat-sheet/)) (atau HTML jika membutuhkan format yang tidak didukung Markdown). Paket `markdownx` yang digunakan pada proyek web ini sudah mendukung _drag and drop_ gambar. Formula matematika ditampilkan dengan [MathJax](https://www.mathjax.org/) (khusus AsciiMath) dengan delimiter `$$`.

Ketika membuat dan mengedit artikel, file `sitemap.txt` akan dibuat ulang secara otomatis. Sistem juga akan melakukan _ping_ ke mesin pencari melalui [Ping-O-Matic](https://pingomatic.com/).

Sistem komentar yang digunakan adalah Disqus. Anda harus mendaftarkan website Anda di [Disqus](https://disqus.com/) terlebih dahulu.

Sistem basis data yang digunakan adalah SQLite.

Blog juga dilengkapi dengan fitur pencarian artikel.

## Panduan Instalasi

Proyek web ini harus di-_deploy_ di web hosting yang mendukung Python/Django. Mohon ikuti petunjuk dari _provider_ masing-masing tentang bagaimana cara deploy yang benar. Jika sudah, ikuti langkah-langkah berikut untuk melakukan konfigurasi pada aplikasi web ini.

1. Ubah nama file `.env.example` menjadi `.env` dan isi nilai konstan di dalamnya dengan nilai yang benar.

2. Edit halaman 'About' di blog -> templates -> blog -> `about.html`.

3. Pada file templates -> `base.html`, ubah nama _copyright holder_ dan logo.

4. Periksa juga file blog_project -> `settings.py` untuk konfigurasi lainnya, misalnya `LANGUAGE_CODE` dan `TIME_ZONE`.

## Lisensi

MIT. Lihat file `LICENSE`.

Konten artikel yang Anda tulis dilindungi CC-BY. Tapi Anda dapat mengubah ini sesuai keinginan. Ingat, hindari mengambil konten orang lain tanpa izin.