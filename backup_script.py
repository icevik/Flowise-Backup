import shutil
import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from supabase import create_client, Client
import json

# Mevcut sabitler
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SOURCE_DIR = '<FLOWISE_FILE_PATH>'
TEMP_DIR = 'TEMP_FILE_PATH'

# Supabase bağlantı bilgileri
SUPABASE_URL = <SUPABASE_URL>
SUPABASE_KEY = <SUPABASE_KEY>

def init_supabase() -> Client:
    """Supabase istemcisini başlat"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def log_backup(supabase: Client, file_name: str, drive_link: str, status: str, error_message: str = None):
    """Yedekleme logunu Supabase'e kaydet"""
    try:
        data = {
            "file_name": file_name,
            "drive_link": drive_link,
            "status": status,
            "error_message": error_message
        }
        
        result = supabase.table('backup_logs').insert(data).execute()
        print("Log kaydı başarıyla oluşturuldu")
        return result
    except Exception as e:
        print(f"Log kaydı oluşturulurken hata: {str(e)}")
        return None

def create_zip_backup():
    """Flowise klasörünü zipleme"""
    current_date = datetime.now().strftime('%d-%m-%Y')
    zip_filename = f"Knowhy {current_date}.zip"
    zip_path = os.path.join(TEMP_DIR, zip_filename)
    
    try:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        shutil.make_archive(
            os.path.join(TEMP_DIR, f"Knowhy {current_date}"),
            'zip',
            SOURCE_DIR
        )
        print(f"Yedekleme başarıyla oluşturuldu: {zip_filename}")
        return zip_path, zip_filename
    except Exception as e:
        print(f"Yedekleme oluşturulurken hata: {str(e)}")
        return None, None

def authenticate():
    """Google Drive kimlik doğrulama"""
    SERVICE_ACCOUNT_FILE = '/home/ubuntu/TEMP/KnowhyServices.json'
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, 
        scopes=SCOPES
    )
    return credentials

def upload_to_drive(file_path):
    """Drive'a yükleme"""
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    
    file_name = os.path.basename(file_path)
    file_metadata = {
        'name': file_name,
    }
    
    media = MediaFileUpload(file_path, resumable=True)
    
    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        service.permissions().create(
            fileId=file.get('id'),
            body={
                'type': 'anyone',
                'role': 'reader'
            }
        ).execute()
        
        share_link = f"https://drive.google.com/file/d/{file.get('id')}/view?usp=sharing"
        print(f"Dosya başarıyla yüklendi")
        print(f"Paylaşım linki: {share_link}")
        return True, share_link
    
    except Exception as e:
        print(f"Yükleme sırasında hata: {str(e)}")
        return False, None

def cleanup(zip_path):
    """Geçici dosyaları temizle"""
    try:
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print("Geçici dosyalar temizlendi")
    except Exception as e:
        print(f"Temizlik sırasında hata: {str(e)}")

def main():
    supabase = init_supabase()
    
    # 1. Zip dosyası oluştur
    zip_path, file_name = create_zip_backup()
    if not zip_path:
        log_backup(
            supabase,
            file_name="",
            drive_link="",
            status="ERROR",
            error_message="Zip dosyası oluşturulamadı"
        )
        return
    
    # 2. Drive'a yükle
    upload_success, drive_link = upload_to_drive(zip_path)
    
    # 3. Supabase'e kaydet
    if upload_success:
        log_backup(
            supabase,
            file_name=file_name,
            drive_link=drive_link,
            status="SUCCESS"
        )
        # 4. Temizlik yap
        cleanup(zip_path)
    else:
        log_backup(
            supabase,
            file_name=file_name,
            drive_link="",
            status="ERROR",
            error_message="Drive'a yükleme başarısız"
        )

if __name__ == "__main__":
    main()