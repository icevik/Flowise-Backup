# Do not forget to change the specified file paths to your own. This script was tested on Ubuntu 24.04.1 LTS.

# Flowise Backup Service

This service is a system that automatically backs up the Flowise application and uploads it to Google Drive. It performs backups three times a day (09:00, 13:00, 21:00).

## 🚀 Features

- Automatic scheduled backup
- Google Drive integration
- Automatic file cleanup
- Systemd service support
- Secure service account usage

## 📋 Requirements

- Python 3.x
- virtualenv
- Google Cloud Platform account
- Ubuntu/Debian based operating system

## 📥 Installation

### 1. Clone the repository git clone https://github.com/knowhyco/flowise-backup.git


### 2. Create a Python virtual environment

python -m venv myenv
source myenv/bin/activate


### 3. Install the required packages

pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client


### 4. Google Cloud Platform Settings

1. Create a new project in Google Cloud Console
2. Enable Google Drive API
3. Create a Service Account:
   - IAM & Admin > Service Accounts
   - Create Service Account
   - Create key in JSON format
4. Save the downloaded JSON file to `/home/ubuntu/TEMP/service-account-key.json`

### 5. Service Setup

1. Create the backup script:
sudo nano /home/ubuntu/TEMP/backup_script.py
Paste the content of backup_script.py

1.2: Create a Supabase account. Run the following SQL code:

create table backup_logs (
    id uuid default gen_random_uuid() primary key,
    backup_date timestamp with time zone default timezone('UTC'::text, now()) not null,
    file_name text not null,
    drive_link text not null,
    status text not null,
    error_message text,
    created_at timestamp with time zone default timezone('UTC'::text, now()) not null
);

-- Disable RLS
alter table backup_logs disable row level security;

1.3: Place the Supabase API Url and API Key into the script.


2. Create the run script:

sudo nano /home/ubuntu/TEMP/run_backup.sh
chmod +x /home/ubuntu/TEMP/run_backup.sh


3. Create the systemd service files:
sudo nano /etc/systemd/system/flowise-backup.service

Paste the content of the service file
sudo nano /etc/systemd/system/flowise-backup.timer

Paste the content of the timer file


4. Enable the service:
sudo systemctl daemon-reload
sudo systemctl enable flowise-backup.timer
sudo systemctl start flowise-backup.timer


## 🔍 Monitoring and Control

### Service Status
sudo systemctl status flowise-backup.timer
sudo systemctl status flowise-backup.service


### Timer Control
sudo systemctl list-timers --all


### Log Control
sudo journalctl -u flowise-backup.service
