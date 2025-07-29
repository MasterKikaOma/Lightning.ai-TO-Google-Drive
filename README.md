# Lightning.ai-TO-Google-Drive
Data Transfer app for lightning.ai


How to Use This App:

    Save the code above as gdrive_upload_helper.py inside the folder you want to upload.

    Make sure you have Python 3.7+ installed.

    Install dependencies (once):

text
--> pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

Run the script:

    text
    -->  python gdrive_upload_helper.py

    Follow the on-screen prompts:

        Authenticate ADC (this will open your browser).

        Enter your quota project ID (or create one manually if you don’t have).

        The script will open a page to enable Drive API in your Google Cloud project.

        It tests your Drive access.

        Uploads the entire folder recursively.

    Repeat running this script anytime you want to upload the folder again without error or hassle.

What This App Does for You:

    Checks and guides you to install and authenticate Google Cloud credentials correctly.

    Sets your quota project to handle Google Drive API usage.

    Directs you to enable Google Drive API in your project.

    Tests connectivity and permissions automatically.

    Uploads the entire folder (including subfolders) with progress output.

    All steps are clear, sequential, and require minimal manual intervention besides browser/logged-in prompts.

    Can be run multiple times without redoing previous steps unless necessary.
