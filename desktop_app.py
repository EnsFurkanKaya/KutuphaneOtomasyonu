"""Online Kütüphane Yönetim Sistemi - Bağımsız Windows Masaüstü Uygulaması.

Bu dosya PyInstaller ile derlenerek tek başına çalışan bir .exe dosyasına dönüştürülür.
Hem FastAPI REST API'sini hem de derlenmiş React/TypeScript web arayüzünü sunar.
"""
import os
import sys
import time
import socket
import webbrowser
import threading
from pathlib import Path

# PyInstaller paketleme ve normal çalışma dizini tespiti
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.resolve()
    APP_DIR = BASE_DIR

# Backend modüllerini sys.path'e dahil et
backend_dir = BASE_DIR / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# UTF-8 konsol çıktısı
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Statik frontend dizinini bul
dist_dir = BASE_DIR / "frontend" / "dist"
if not dist_dir.exists():
    dist_dir = BASE_DIR / "frontend_dist"

# Veritabanı yapılandırması
def setup_database():
    import os
    from app.core.config import get_settings
    settings = get_settings()

    # PostgreSQL bağlantısını test et
    use_sqlite = False
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(settings.database_url, connect_args={"connect_timeout": 2})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"[VERİTABANI] PostgreSQL bağlantısı aktif: {settings.database_url.split('@')[-1]}")
    except Exception as e:
        print("[VERİTABANI] PostgreSQL bulunamadı. Yerel SQLite moduna geçiliyor...")
        use_sqlite = True

    if use_sqlite:
        sqlite_path = (APP_DIR / "kutuphane.db").resolve()
        os.environ["DATABASE_URL"] = f"sqlite:///{sqlite_path}"
        get_settings.cache_clear()
        
        # Tabloları oluştur ve ilk seed verilerini yükle
        from app.db.seed import init_db_and_seed
        print(f"[VERİTABANI] SQLite veritabanı hazırlanıyor: {sqlite_path}")
        init_db_and_seed()
        print("[VERİTABANI] SQLite tabloları ve örnek veriler hazır.")

setup_database()

# FastAPI uygulamasını al
from app.main import app
from starlette.responses import FileResponse

# SPA React Frontend'ini FastAPI'ye bağla
if dist_dir.exists():
    print(f"[ÖN YÜZ] Statik React arayüzü bağlandı: {dist_dir}")
    
    # API dışındaki tüm istekler için SPA Fallback
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        target_file = dist_dir / full_path
        if target_file.is_file():
            return FileResponse(target_file)
        index_file = dist_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"error": "Frontend dosyaları bulunamadı"}
else:
    print(f"[UYARI] Frontend dist klasörü bulunamadı: {dist_dir}")

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def open_browser_after_delay(url: str, delay: float = 1.5):
    def _open():
        time.sleep(delay)
        print(f"[TARAYICI] Uygulama açılıyor: {url}")
        webbrowser.open(url)
    threading.Thread(target=_open, daemon=True).start()

def main():
    import uvicorn

    port = 8000
    while is_port_in_use(port) and port < 8010:
        port += 1

    url = f"http://localhost:{port}"
    print("=" * 65)
    print("  ONLINE KÜTÜPHANE YÖNETİM SİSTEMİ - MASAÜSTÜ UYGULAMASI")
    print("=" * 65)
    print(f"  * Uygulama Adresi : {url}")
    print(f"  * Swagger API     : {url}/docs")
    print(f"  * Varsayılan Giriş: admin@kutuphane.edu.tr / Admin12345!")
    print("=" * 65)
    print("  Durdurmak için pencereyi kapatın veya CTRL+C tuşlarına basın.\n")

    open_browser_after_delay(url)

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

if __name__ == "__main__":
    main()
