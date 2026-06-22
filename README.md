# Sistem Informasi Prediksi Timbulan Sampah (SAMPAH.AI)

Sistem Informasi berbasis Flask untuk mengelola data kecamatan, data demografi, bisnis Horeca, sensor IoT, serta visualisasi spasial GIS per kecamatan di Kota Bandung. Sistem ini terintegrasi dengan database MySQL dan terhubung ke microservice FastAPI AI (ensemble Random Forest) via REST API.

## Struktur Project

*   `app.py`: Entry point utama aplikasi Flask. Mengelola inisialisasi context, session, blueprints, dan data seeding.
*   `config.py`: File konfigurasi parameter sistem, memuat data dari `.env`.
*   `models_db/`: Modul koneksi basis data.
    *   `database.py`: Inisialisasi SQLAlchemy dengan mekanisme fallback otomatis dari MySQL ke SQLite jika koneksi MySQL gagal.
    *   `models.py`: Deklarasi schema ORM database (AdminUser, District, Horeca, IoTDevice, PredictionHistory, ModelRegistry).
*   `routes/`: Blueprint routing halaman web.
    *   `auth.py`: Manajemen autentikasi session admin (Login/Logout).
    *   `dashboard.py`: Menampilkan diagram statistik Chart.js dan monitoring volume total real-time.
    *   `data.py`: Halaman manajemen data CRUD terintegrasi filter pencarian instan.
    *   `prediction.py`: Panel kontrol parameter apa-jika (what-if) untuk model prediksi AI dan pelatihan ulang model.
    *   `gis.py`: Route visualisasi Leaflet dan endpoint GeoJSON API.
*   `services/`: Modul integrasi pihak ketiga.
    *   `ai_client.py`: API Connector REST ke FastAPI AI Service (`/predict` & `/train`) dengan simulasi model lokal jika server FastAPI offline.
*   `static/`: Asset statis visual (CSS custom, JS interaktif, data GeoJSON Bandung).
*   `templates/`: Jinja2 HTML templates yang responsif menggunakan Tailwind CSS.
*   `schema.sql`: Script inisialisasi database MySQL mentah.

## Prasyarat Setup

Aplikasi ini menggunakan Python 3. Pastikan dependensi sudah terpasang:

```bash
pip install -r requirements.txt
```

## Konfigurasi Database & API

Atur credential database Anda di file `.env` di direktori root:

```env
SECRET_KEY=dev_secret_key_change_in_production_998811
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=sistem_prediksi_sampah
FASTAPI_API_URL=http://localhost:8000
```

> **Catatan:** Jika MySQL tidak aktif atau belum diatur pada startup pertama, sistem secara otomatis akan menggunakan database SQLite lokal (`sistem_prediksi_sampah.db`) di dalam folder project agar sistem tetap dapat berjalan.

### Menggunakan MySQL saja (disarankan untuk produksi)

Proyek ini dapat berjalan sepenuhnya menggunakan MySQL. Untuk memaksa penggunaan MySQL (tanpa fallback SQLite) ikuti langkah berikut:

1. Pastikan MySQL berjalan dan database dibuat (contoh nama `sistem_prediksi_sampah`).
2. Tambahkan kredensial di file `.env` (contoh):

```
DB_USER=root
DB_PASSWORD=@Akucinta17
DB_HOST=localhost
DB_PORT=3306
DB_NAME=sistem_prediksi_sampah
# Jika password mengandung karakter khusus seperti '@' gunakan URL-encoding di DATABASE_URL
DATABASE_URL=mysql+pymysql://root:%40Akucinta17@localhost:3306/sistem_prediksi_sampah
```

3. Gunakan helper PowerShell untuk men-set environment, menjalankan seeding, dan memulai aplikasi:

```powershell
.\.venv\Scripts\Activate.ps1
.\scripts\start_mysql.ps1
```

Catatan penting: Setelah mengaktifkan mode MySQL-only proyek akan melempar error dan berhenti jika koneksi MySQL gagal — ini untuk mencegah penggunaan database SQLite lokal secara tidak sengaja.

## Cara Menjalankan Aplikasi

Jalankan server aplikasi Flask dengan perintah berikut:

```bash
python app.py
```

Setelah aplikasi berjalan, buka peramban Anda dan akses:
`http://127.0.0.1:5000/`

## Kredensial Login Default

*   **Username**: `admin`
*   **Password**: `admin123`
