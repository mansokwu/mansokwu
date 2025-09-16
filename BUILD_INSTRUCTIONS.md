# MantaTools - Build Instructions

## Setup Auto-Update System

MantaTools sekarang memiliki sistem auto-update yang lengkap dengan notifikasi otomatis.

### Fitur Auto-Update

1. **Cek Update Otomatis**: Aplikasi akan mengecek update saat startup
2. **Notifikasi Update**: Menampilkan notifikasi jika ada versi baru
3. **Download Otomatis**: Download installer versi terbaru
4. **Install Otomatis**: Jalankan installer untuk update
5. **Tombol Manual**: Tombol "Check Update" di header untuk cek manual

### Cara Build Installer

#### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Install build tools
pip install pyinstaller pyinstaller-hooks-contrib
```

#### 2. Build Executable

```bash
# Build dengan versi default
python build_installer.py

# Build dengan versi spesifik
python build_installer.py 1.0.1
```

#### 3. Release ke GitHub

```bash
# Release dengan versi baru
python release.py 1.0.1
```

### File yang Dihasilkan

- `dist/MantaTools.exe` - Executable utama
- `dist/MantaTools_Setup_v1.0.0.exe` - Installer untuk distribusi

### Cara Release Update

1. **Update Version**: Edit `src/mantatools/core/version.py`
2. **Build**: Jalankan `python build_installer.py <version>`
3. **Release**: Jalankan `python release.py <version>`
4. **Upload**: Upload installer ke GitHub Releases

### GitHub Actions

Workflow otomatis akan:
- Build executable saat ada tag baru
- Upload ke GitHub Releases
- Generate release notes

### Struktur Update System

```
src/mantatools/core/
├── updater.py      # Sistem auto-update
├── version.py      # Manajemen versi
└── ...

src/qml/components/
└── Header.qml      # Tombol "Check Update"
```

### Konfigurasi Repository

Update URL repository di `src/mantatools/core/version.py`:

```python
REPO_URL = "https://github.com/mansokwu/mansokwu.git"
```

### Testing Update System

1. Build versi 1.0.0
2. Release ke GitHub
3. Update version ke 1.0.1
4. Build dan release versi baru
5. Jalankan aplikasi - akan muncul notifikasi update

### Troubleshooting

**Update tidak muncul?**
- Pastikan GitHub Releases sudah ada
- Cek koneksi internet
- Pastikan versi di GitHub lebih baru

**Download gagal?**
- Cek URL repository di version.py
- Pastikan GitHub API accessible
- Cek firewall/antivirus

**Installer tidak jalan?**
- Pastikan file .exe tidak corrupt
- Cek Windows Defender
- Jalankan sebagai administrator
