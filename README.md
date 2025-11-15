# SAP Training Management Toolkit

This repository provides a lightweight command-line application for managing the
training catalogue that is typically used in SAP enablement programs. You can
register employees, maintain course definitions, schedule sessions and generate
basic utilization reports without the need of a full ERP system.

## Getting started

1. Create a virtual environment (optional) and install the package in editable
   mode if you want to reuse it across multiple projects:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

2. Run the CLI via the module entrypoint:

   ```bash
   python -m sap_training.cli --help
   ```

The application stores all data in a JSON file (`sap_training_data.json` by
default). Pass `--db` to change the location, which is useful when keeping
separate datasets for different training waves.

## Example workflow

```bash
# Add a course to the catalogue
python -m sap_training.cli courses add SD100 "Sales & Distribution" Beginner 3 "SD basics"

# Register an employee
python -m sap_training.cli participants add E001 "Ada Lovelace" Finance

# Schedule a session and enroll the employee
python -m sap_training.cli sessions schedule SD100-01 SD100 2024-08-01 "Grace Hopper" Istanbul 12
python -m sap_training.cli enroll SD100-01 E001

# Review utilization
python -m sap_training.cli report
```

The report command emits JSON rows that can be piped into other command line
utilities or imported into Excel.

## Web tabanlı Tetrix'i çalıştırma

Tarayıcıda çalışan Tetrix mini oyunu, depo içerisindeki `web/tetris`
klasöründeki statik HTML/CSS/JS dosyalarından oluşur. Herhangi bir web
framework'üne gerek yoktur; sadece dosyaları servis edecek basit bir HTTP
sunucusu gerekir. Aşağıdaki adımları izleyin:

1. Depo kökündeyken statik dosyaları servis edin. Python'un standart
   kitaplığındaki `http.server` modülü bu iş için yeterlidir:

   ```bash
   python -m http.server 8000 --directory web/tetris
   ```

2. Tarayıcınızdan `http://localhost:8000` adresini açın. Ana ekran oyun
   tahtasını, skor ve seviye durumunu, sıradaki taşın ön izlemesini ve temel
   kontrol butonlarını içerir.

3. Oyunu aşağıdaki kontrollerle yönetebilirsiniz:

   - **Başlat/Duraklat/Sıfırla** butonları oyun akışını kontrol eder.
   - **Ok tuşları** taşları sola/sağa hareket ettirir, aşağı ok hızlı düşürür.
   - **Boşluk** taşları bırakır, **Yukarı ok** taşları döndürür.

İsterseniz sunucuyu kapatmadan tarayıcıyı yenileyerek yeni bir oyun
başlatabilirsiniz. Oyunun tüm durum bilgisi tarayıcı belleğinde tutulduğu için
ek bir sunucu yapılandırmasına gerek yoktur.

## Running tests

```bash
pytest
```
