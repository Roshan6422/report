import os
import sys
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from google.oauth2 import service_account
from googleapiclient.discovery import build

creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/drive'])
drive_service = build('drive', 'v3', credentials=creds)

about = drive_service.about().get(fields='storageQuota').execute()
print("STORAGE QUOTA:")
print(about)

print("\nTOP 50 FILES:")
res = drive_service.files().list(spaces='drive', fields='files(id, name, size, trashed)', pageSize=50).execute()
for f in res.get('files', []):
    print(f)
