# MantaTools

Aplikasi Python dengan sistem auto-update yang lengkap untuk manajemen game Steam.

## 🚀 Fitur

- **Sistem Auto-Update**: Cek dan download update otomatis
- **Notifikasi Update**: Window notifikasi saat ada versi baru
- **Installer Otomatis**: Build installer.exe yang bisa di-update
- **GitHub Integration**: Release otomatis ke GitHub
- **UI Modern**: Interface QML yang responsif

## 📦 Install & Build

### 1. Setup Environment

```bash
# Clone repository
git clone https://github.com/mansokwu/mansokwu.git
cd mantatools

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup GitHub (Pertama kali)

```bash
# Setup repository GitHub
python setup_github.py
```

### 3. Build Installer

```bash
# Build installer
python build_installer.py

# Atau dengan versi spesifik
python build_installer.py 1.0.1
```

### 4. Release Update

```bash
# Release versi baru
python release.py 1.0.1
```

## 🔄 Sistem Auto-Update

### Cara Kerja

1. **Startup Check**: Aplikasi cek update saat startup
2. **Notifikasi**: Tampil notifikasi jika ada versi baru
3. **Download**: Download installer otomatis
4. **Install**: Jalankan installer untuk update

### Konfigurasi

Edit `src/mantatools/core/version.py`:

```python
VERSION = "1.0.0"  # Update versi di sini
REPO_URL = "https://github.com/mansokwu/mansokwu.git"  # URL repository
```

## 🛠️ Development

### Struktur Project

```
MantaTools/
├── src/mantatools/
│   ├── core/
│   │   ├── updater.py      # Sistem auto-update
│   │   └── version.py      # Manajemen versi
│   └── main.py             # Entry point
├── src/qml/                # UI QML
├── build_installer.py      # Script build
├── release.py              # Script release
└── requirements.txt        # Dependencies
```

### Testing

```bash
# Test sistem update
python test_update.py

# Test dengan GUI
python test_update.py --gui
```

## 📋 Workflow Release

1. **Update Version**: Edit `src/mantatools/core/version.py`
2. **Build**: `python build_installer.py <version>`
3. **Release**: `python release.py <version>`
4. **Upload**: Otomatis ke GitHub Releases

## 🔧 Troubleshooting

**Update tidak muncul?**
- Pastikan GitHub Releases sudah ada
- Cek koneksi internet
- Pastikan versi di GitHub lebih baru

**Build gagal?**
- Install dependencies: `pip install -r requirements.txt`
- Cek Python version (3.11+)
- Pastikan PyInstaller terinstall

**GitHub release gagal?**
- Setup GitHub CLI: `gh auth login`
- Cek repository permissions
- Pastikan tag sudah dibuat

## 📄 License

MIT License - lihat file LICENSE untuk detail.

## 🤝 Contributing

1. Fork repository
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Buat Pull Request

---

**MantaTools** - Auto-updating game management tool

Aplikasi manajemen game Steam yang modern dan modular dengan antarmuka QML.

## 🚀 Fitur

- **Manajemen Game Steam**: Tambah, hapus, dan kelola game Steam
- **Antarmuka Modern**: UI yang elegan menggunakan QML
- **Notifikasi Toast**: Feedback visual untuk setiap aksi
- **Arsitektur Modular**: Kode yang terorganisir dan mudah dipelihara

## 📁 Struktur Project

```
MantaTools/
├── src/                          # Source code utama
│   ├── mantatools/              # Package utama
│   │   ├── core/                # Core functionality
│   │   ├── ui/                  # UI components
│   │   ├── main.py              # Entry point utama
│   │   └── bridge.py            # QML Bridge
│   ├── qml/                     # QML UI files
│   │   ├── components/          # Reusable QML components
│   │   └── pages/               # Page components
│   ├── assets/                  # Static assets
│   └── docs/                    # Documentation
├── run.py                       # Main entry point
└── requirements.txt             # Dependencies
```

## 🛠️ Instalasi

1. Clone repository ini
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi:
   ```bash
   python run.py
   ```

## 📖 Penggunaan

1. Jalankan aplikasi dengan `python run.py`
2. Pilih game yang ingin dikelola
3. Gunakan tombol-tombol untuk:
   - **Add to Steam**: Tambahkan game ke Steam
   - **Remove Game**: Hapus game dari Steam
   - **Restart Steam**: Restart Steam client
   - **Update Game**: Update game

## 🔧 Pengembangan

### Struktur Kode

- **Core**: Logika bisnis dan utilitas
- **UI**: Komponen UI yang dapat digunakan kembali
- **QML**: Antarmuka pengguna
- **Assets**: Resource dan icon

### Menambah Fitur Baru

1. Tambahkan logika di `src/mantatools/core/`
2. Buat komponen UI di `src/mantatools/ui/`
3. Tambahkan halaman QML di `src/qml/pages/`
4. Update bridge jika diperlukan

## 📝 Lisensi

MIT License
