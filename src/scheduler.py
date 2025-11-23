"""
Scheduler untuk ETL Pipeline
Menjalankan ETL otomatis setiap 1 jam
"""

import schedule
import time
from datetime import datetime
import subprocess
import sys
import os

# Tambahkan path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.etl_pipeline import SimpleETL

def run_etl_job():
    """Fungsi yang akan dijalankan setiap 1 jam"""
    print("\n" + "="*70)
    print(f"🔄 SCHEDULED ETL RUN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    try:
        # Jalankan ETL pipeline
        etl = SimpleETL()
        result = etl.run(output_format='both')
        
        if result is not None:
            print("\n✅ Scheduled ETL job completed successfully!")
        else:
            print("\n❌ Scheduled ETL job failed!")
            
    except Exception as e:
        print(f"\n❌ Error in scheduled job: {str(e)}")
    
    print(f"\n⏰ Next run scheduled at: {datetime.now().replace(hour=(datetime.now().hour + 1) % 24, minute=0, second=0)}")
    print("="*70)

def main():
    """Main scheduler function"""
    print("\n" + "="*70)
    print("🚀 ETL PIPELINE SCHEDULER")
    print("="*70)
    print("📅 Schedule: Every 1 hour")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print("\n💡 Tips:")
    print("   - Tekan Ctrl+C untuk stop scheduler")
    print("   - Scheduler akan terus berjalan di background")
    print("   - Data baru akan disimpan setiap 1 jam")
    print("="*70)
    
    # Jalankan sekali di awal
    print("\n🏃 Running initial ETL job...")
    run_etl_job()
    
    # Schedule untuk setiap 1 jam
    schedule.every(1).hours.do(run_etl_job)
    
    # Alternative: Bisa juga setiap X menit untuk testing
    # schedule.every(5).minutes.do(run_etl_job)  # Setiap 5 menit
    
    print("\n⏳ Scheduler is running... (Press Ctrl+C to stop)")
    
    # Loop untuk menjalankan scheduled jobs
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check setiap 1 menit
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("🛑 SCHEDULER STOPPED")
        print("="*70)
        print(f"⏰ Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("✅ All scheduled jobs have been cancelled.")
        print("="*70)

if __name__ == "__main__":
    main()
