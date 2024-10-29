#!/bin/bash
cd /home/ubuntu/TEMP
source /home/ubuntu/TEMP/myenv/bin/activate <MYENV_FILE_PATH>
python /home/ubuntu/TEMP/backup_script.py <BACKUP_SCRIPT_FILE_PATH>
deactivate
