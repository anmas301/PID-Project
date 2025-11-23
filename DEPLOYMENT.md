# 🚀 Deploy Dashboard ke Streamlit Cloud (Publik)

## Cara Deploy Dashboard Agar Bisa Diakses Publik

### Option 1: Streamlit Cloud (Recommended - GRATIS)

#### Langkah 1: Persiapan Repository
```bash
# Pastikan semua file sudah di-commit dan di-push ke GitHub
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

#### Langkah 2: Deploy ke Streamlit Cloud

1. **Buka Streamlit Cloud**
   - Kunjungi: https://share.streamlit.io/
   - Login dengan akun GitHub Anda

2. **Create New App**
   - Klik "New app"
   - Pilih repository: `anmas301/PID-Project`
   - Branch: `main`
   - Main file path: `src/dashboard.py`

3. **Advanced Settings (PENTING)**
   - Klik "Advanced settings"
   - Tambahkan secrets (copy dari `.streamlit/secrets.toml`):
   ```toml
   OPENWEATHER_API_KEY = "a2a73644ed35384c9ac73bc606560ed5"
   WEATHERAPI_KEY = "e67f32eab28541b892b40743251609"
   ```

4. **Deploy!**
   - Klik "Deploy!"
   - Tunggu 2-5 menit untuk deployment
   - Dashboard akan tersedia di URL seperti: `https://your-app-name.streamlit.app`

#### Langkah 3: Share URL
Setelah deploy, Anda akan mendapat URL publik yang bisa dibagikan ke siapa saja!

---

### Option 2: Ngrok (Temporary - Untuk Testing)

Jika ingin share dashboard lokal secara temporary:

#### 1. Install Ngrok
```bash
# Download ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

#### 2. Setup Ngrok
```bash
# Signup di https://dashboard.ngrok.com/signup
# Copy auth token dari dashboard
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

#### 3. Run Dashboard & Ngrok
```bash
# Terminal 1: Run dashboard
streamlit run src/dashboard.py --server.port 8501

# Terminal 2: Expose dengan ngrok
ngrok http 8501
```

Ngrok akan memberikan URL publik (e.g., `https://xxxx-xxxx.ngrok.io`) yang bisa diakses dari mana saja.

**Catatan**: URL ngrok gratis hanya aktif selama sesi berjalan.

---

### Option 3: Heroku (GRATIS dengan batasan)

#### 1. Buat file tambahan

**Procfile:**
```
web: sh setup.sh && streamlit run src/dashboard.py
```

**setup.sh:**
```bash
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

**runtime.txt:**
```
python-3.12.1
```

#### 2. Deploy ke Heroku
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create pid-project-dashboard

# Set environment variables
heroku config:set OPENWEATHER_API_KEY=a2a73644ed35384c9ac73bc606560ed5
heroku config:set WEATHERAPI_KEY=e67f32eab28541b892b40743251609

# Deploy
git push heroku main

# Open dashboard
heroku open
```

---

### Option 4: Render (GRATIS)

1. Kunjungi: https://render.com/
2. Connect GitHub repository
3. Create new "Web Service"
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run src/dashboard.py --server.port 8501 --server.address 0.0.0.0`
5. Add environment variables (API keys)
6. Deploy!

---

## 🎯 Rekomendasi

**Untuk Proyek Kuliah**: 
- ✅ **Streamlit Cloud** (Paling mudah, gratis, professional)
- URL permanen: `https://pid-project.streamlit.app`

**Untuk Testing/Demo Cepat**:
- ✅ **Ngrok** (Instant, tapi temporary)

**Untuk Production**:
- ✅ **Heroku** atau **Render** (Lebih kontrol, scaling)

---

## 📝 Checklist Sebelum Deploy

- [ ] Semua file sudah di-commit
- [ ] `requirements.txt` lengkap dan tested
- [ ] API keys tidak hardcoded (gunakan secrets)
- [ ] Dashboard berjalan lokal tanpa error
- [ ] `.gitignore` sudah benar (jangan commit secrets)
- [ ] README.md updated dengan deployment info

---

## 🔒 Keamanan

**PENTING**:
- ❌ Jangan commit API keys ke Git
- ✅ Gunakan secrets/environment variables
- ✅ Add `.streamlit/secrets.toml` ke `.gitignore`

---

## 📞 Support

Jika ada masalah deployment:
1. Check Streamlit Cloud logs
2. Verify requirements.txt
3. Test locally first
4. Check API keys validity

**Streamlit Docs**: https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app

---

**Good luck! 🚀**
