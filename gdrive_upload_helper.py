import os
import subprocess
import sys
import webbrowser
from time import sleep
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google.auth
from google.auth.exceptions import DefaultCredentialsError

# Placeholder Google Drive folder ID - replace with your own
DRIVE_FOLDER_ID = "TEMP_DRIVE_FOLDER_ID"

def print_header():
    print("\n=== Google Drive Upload Helper ===\n")

def run_command(cmd, capture_output=False):
    print(f"\nRunning command:\n  {' '.join(cmd)}")
    try:
        if capture_output:
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(result.stdout)
            return result.stdout
        else:
            subprocess.run(cmd, check=True)
        return None
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        if e.stdout:
            print("Output:", e.stdout)
        if e.stderr:
            print("Errors:", e.stderr)
        return None

def verify_gcloud_installed():
    print("Checking if 'gcloud' CLI is installed...")
    if run_command(["gcloud", "--version"], capture_output=True) is None:
        print("ERROR: 'gcloud' command not found. Please install Google Cloud SDK first.")
        sys.exit(1)

def authenticate_adc():
    print("\nSTEP 1: Authenticate Application Default Credentials (ADC)")
    print("This will open a browser to login and authorize.")
    input("Press Enter to continue...")
    run_command(["gcloud", "auth", "application-default", "login",
                 "--scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/drive"])

def set_quota_project():
    print("\nSTEP 2: Set your Google Cloud quota project for ADC (needed for Drive uploads)")
    print("You need to create or have a Google Cloud Project ID to proceed.")
    proj_id = input("Enter your Google Cloud Project ID (or leave empty to skip and set it manually later): ").strip()
    if not proj_id:
        print("You chose to skip setting quota project now. You may see quota warnings or errors later.")
        return None
    run_command(["gcloud", "auth", "application-default", "set-quota-project", proj_id])
    print("Quota project set to:", proj_id)
    return proj_id

def enable_drive_api(proj_id):
    if not proj_id:
        print("\nNo quota project ID given, cannot enable Drive API automatically.")
        print("Please enable Drive API manually here:")
        print(f"https://console.developers.google.com/apis/api/drive.googleapis.com/overview?project=YOUR_PROJECT_ID")
        print("Replace YOUR_PROJECT_ID with your actual project ID.")
        input("Press Enter after you have enabled Drive API...")
        return
    
    print("\nSTEP 3: Enabling Google Drive API in your project on Google Cloud Console")
    url = f"https://console.developers.google.com/apis/api/drive.googleapis.com/overview?project={proj_id}"
    print("Opening this page in your browser to enable Google Drive API...")
    webbrowser.open(url)
    input("After enabling the API, press Enter to continue. This may take a few minutes.")

def test_adc_credentials():
    print("\nSTEP 4: Testing Application Default Credentials with Google Drive API")
    try:
        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive"])
        service = build("drive", "v3", credentials=creds)
        results = service.files().list(q=f"'{DRIVE_FOLDER_ID}' in parents", pageSize=1).execute()
        print(f"Drive API test successful. Found files in target folder (count limited to 1):")
        files = results.get("files", [])
        if not files:
            print("No files found (folder may be empty), but API access is working.")
        else:
            print(f"Sample file: {files[0].get('name')} (ID: {files[0].get('id')})")
        return True
    except DefaultCredentialsError:
        print("Error: Application Default Credentials not found or invalid.")
        return False
    except Exception as e:
        print(f"Drive API test failed with error: {e}")
        return False

def create_drive_folder(service, name, parent_id):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder['id']

def upload_file(service, filepath, parent_id):
    file_metadata = {'name': os.path.basename(filepath), 'parents': [parent_id]}
    media = MediaFileUpload(filepath, resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'Uploaded file: {filepath}')

def upload_folder(service, local_folder, drive_folder_id):
    folder_map = {local_folder: drive_folder_id}
    for root, dirs, files in os.walk(local_folder):
        parent_id = folder_map[root]
        for d in dirs:
            folder_id = create_drive_folder(service, d, parent_id)
            folder_map[os.path.join(root, d)] = folder_id
        for f in files:
            file_path = os.path.join(root, f)
            upload_file(service, file_path, parent_id)

def upload_current_folder():
    try:
        creds, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/drive'])
        service = build('drive', 'v3', credentials=creds)
    except DefaultCredentialsError:
        print("ERROR: Google Application Default Credentials not found. Please run authentication first.")
        return False
    except Exception as e:
        print(f"Failed to initialize Drive service: {e}")
        return False

    current_dir = os.path.abspath(os.path.dirname(__file__))
    print(f"\nUploading all files/folders under: {current_dir} to Google Drive folder ID: {DRIVE_FOLDER_ID}")
    upload_folder(service, current_dir, DRIVE_FOLDER_ID)
    print("\nUpload Completed Successfully!")
    return True

def main():
    print_header()
    verify_gcloud_installed()

    print("\nThis app will guide you to set up Google Application Default Credentials (ADC) with required scopes, set your quota project, enable Google Drive API, and upload the current folder recursively to Google Drive.")
    print("You will be asked to perform some automatic steps and some manual steps during this process.")
    input("Press Enter to continue...")

    authenticated = False
    while not authenticated:
        authenticate_adc()
        authenticated = test_adc_credentials()
        if not authenticated:
            print("\nAuthentication failed. Please ensure you logged into the correct Google account and granted the requested scopes.")
            retry = input("Try authentication again? (y/n): ").strip().lower()
            if retry != 'y':
                print("Exiting application.")
                sys.exit(1)

    quota_project = set_quota_project()
    enable_drive_api(quota_project)

    if not test_adc_credentials():
        print("\nDrive API access test failed after enabling API. Please check your Google Cloud Console permissions and API status, then rerun the app.")
        sys.exit(1)

    print("\nSTEP 5: Starting folder upload...")
    upload_current_folder()

    print("\nAll done! You can run this script anytime to upload this folder to your Google Drive folder again.\n")

if __name__ == "__main__":
    main()
