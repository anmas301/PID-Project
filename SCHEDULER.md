# 🕐 ETL Pipeline Scheduler

Dokumentasi untuk menjalankan ETL pipeline secara otomatis setiap 1 jam.

## 📋 Fitur Scheduler

- ✅ **Otomatis fetch data** setiap 1 jam dari API
- ✅ **Transform & calculate** Risk Ratio dengan metodologi multiplikatif
- ✅ **Save hasil** ke CSV dan JSON dengan timestamp
- ✅ **Background process** - bisa berjalan 24/7
- ✅ **Error handling** - tetap lanjut jika ada error
- ✅ **Easy to stop** - Ctrl+C untuk menghentikan

## 🚀 Cara Menggunakan

### Opsi 1: Jalankan Scheduler (Recommended)

```bash
python src/scheduler.py
```

**Output:**
```
======================================================================
🚀 ETL PIPELINE SCHEDULER
======================================================================
📅 Schedule: Every 1 hour
⏰ Started at: 2025-11-23 10:00:00
======================================================================

💡 Tips:
   - Tekan Ctrl+C untuk stop scheduler
   - Scheduler akan terus berjalan di background
   - Data baru akan disimpan setiap 1 jam
======================================================================

🏃 Running initial ETL job...

======================================================================
🔄 SCHEDULED ETL RUN - 2025-11-23 10:00:00
======================================================================
...
✅ Scheduled ETL job completed successfully!

⏰ Next run scheduled at: 2025-11-23 11:00:00
======================================================================

⏳ Scheduler is running... (Press Ctrl+C to stop)
```

### Opsi 2: Background Mode (Linux/Mac)

```bash
# Jalankan di background
nohup python src/scheduler.py > scheduler.log 2>&1 &

# Lihat log
tail -f scheduler.log

# Stop scheduler
pkill -f scheduler.py
```

### Opsi 3: Background Mode (Windows)

```powershell
# Gunakan Task Scheduler di Windows
# Atau run di PowerShell:
Start-Process python -ArgumentList "src/scheduler.py" -WindowStyle Hidden
```

## ⚙️ Konfigurasi Custom

Edit `src/scheduler.py` untuk mengubah interval:

```python
# Setiap 30 menit
schedule.every(30).minutes.do(run_etl_job)

# Setiap 2 jam
schedule.every(2).hours.do(run_etl_job)

# Setiap hari jam 9 pagi
schedule.every().day.at("09:00").do(run_etl_job)

# Setiap Senin jam 8 pagi
schedule.every().monday.at("08:00").do(run_etl_job)
```

## 📊 Output Files

Setiap run akan menghasilkan:

```
output/
├── risk_analysis_20251123_100000.csv  # Run 1 (10:00)
├── risk_analysis_20251123_100000.json
├── risk_analysis_20251123_110000.csv  # Run 2 (11:00)
├── risk_analysis_20251123_110000.json
├── risk_analysis_20251123_120000.csv  # Run 3 (12:00)
└── risk_analysis_20251123_120000.json
```

## 🔍 Monitoring

### Check Status

```bash
# Linux/Mac: Check if scheduler is running
ps aux | grep scheduler.py

# Check latest output
ls -lt output/risk_analysis_*.csv | head -5

# View latest data
python -c "import pandas as pd; df = pd.read_csv('output/risk_analysis_20251123_*.csv'); print(df.head())"
```

### View Logs

```bash
# Real-time monitoring
tail -f scheduler.log

# View last 50 lines
tail -50 scheduler.log

# Search for errors
grep "Error" scheduler.log
```

## 🛑 Stop Scheduler

### Method 1: Ctrl+C (jika foreground)

```bash
# Tekan Ctrl+C di terminal
^C
```

Output:
```
======================================================================
🛑 SCHEDULER STOPPED
======================================================================
⏰ Stopped at: 2025-11-23 15:30:45
✅ All scheduled jobs have been cancelled.
======================================================================
```

### Method 2: Kill Process (jika background)

```bash
# Linux/Mac
pkill -f scheduler.py

# Windows
taskkill /F /IM python.exe /FI "WINDOWTITLE eq scheduler*"
```

## 🐳 Docker (Advanced)

### Dockerfile untuk Scheduler

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/scheduler.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  etl-scheduler:
    build: .
    restart: unless-stopped
    volumes:
      - ./output:/app/output
    environment:
      - TZ=Asia/Jakarta
```

### Run dengan Docker

```bash
# Build
docker build -t etl-scheduler .

# Run
docker run -d --name etl-scheduler \
  -v $(pwd)/output:/app/output \
  etl-scheduler

# View logs
docker logs -f etl-scheduler

# Stop
docker stop etl-scheduler
```

## 📝 Integrasi dengan Dashboard

Dashboard Streamlit akan **otomatis load file terbaru** yang dihasilkan scheduler:

```bash
# Terminal 1: Run scheduler
python src/scheduler.py

# Terminal 2: Run dashboard
streamlit run src/dashboard_simple.py
```

Dashboard akan selalu menampilkan data terbaru karena fitur **auto-select newest file**.

## ⚠️ Troubleshooting

### Error: Module 'schedule' not found

```bash
pip install schedule
```

### Error: API Timeout

Scheduler akan tetap lanjut ke run berikutnya. Check log untuk detail error.

### Error: Port 8501 already in use (Dashboard)

```bash
pkill -9 streamlit
streamlit run src/dashboard_simple.py
```

### Memory Issues (Long-running)

Restart scheduler setiap 24 jam untuk clear memory:

```bash
# Crontab (Linux): Restart setiap midnight
0 0 * * * pkill -f scheduler.py && cd /path/to/PID-Project && python src/scheduler.py > scheduler.log 2>&1 &
```

## 🎯 Use Cases

### 1. Production Monitoring (24/7)

```bash
# Setup systemd service (Linux)
sudo nano /etc/systemd/system/etl-scheduler.service
```

```ini
[Unit]
Description=ETL Pipeline Scheduler
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/PID-Project
ExecStart=/usr/bin/python3 /path/to/PID-Project/src/scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl start etl-scheduler
sudo systemctl enable etl-scheduler

# Check status
sudo systemctl status etl-scheduler
```

### 2. Testing/Development

```python
# Edit scheduler.py untuk testing
schedule.every(5).minutes.do(run_etl_job)  # Setiap 5 menit
```

### 3. Data Collection Period

```bash
# Run untuk 12 jam data collection
timeout 12h python src/scheduler.py
```

## 📊 Expected Performance

- **Execution time**: ~30 seconds per run (34 kota)
- **Output size**: ~5-10 KB CSV per run
- **Memory usage**: ~50-100 MB
- **API calls**: 34 cities × 2 APIs = 68 calls per hour
- **Daily data**: 24 files × 2 formats = 48 files per day

## 💡 Tips & Best Practices

1. **Clean old files** secara berkala:
   ```bash
   # Keep only last 7 days
   find output/ -name "risk_analysis_*.csv" -mtime +7 -delete
   ```

2. **Backup data** penting:
   ```bash
   # Daily backup
   tar -czf backup_$(date +%Y%m%d).tar.gz output/
   ```

3. **Monitor API limits**:
   - OpenWeatherMap: 60 calls/minute (free tier)
   - WeatherAPI: 1 million calls/month (free tier)

4. **Alert on failures**:
   ```python
   # Tambahkan di scheduler.py
   import smtplib
   # Send email if ETL fails
   ```

## 📚 References

- [schedule library documentation](https://schedule.readthedocs.io/)
- [Python background processes](https://docs.python.org/3/library/subprocess.html)
- [Systemd service setup](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

**Made with ❤️ for automated ETL pipeline**
