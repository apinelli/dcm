This script takes the log files from a DCM (Digital Content Manager) and outputs a chart with the occurrences 
of "BW Exceeded" alarms, if they exist. The directory structure of the script is currently configured to be run 
under Linux.

Instructions:
- git clone https://github.com/apinelli/dcm to a directory (e.g. /home/user/)
- cd dcm
- mkdir dcmFiles
- pip install -r requirements.txt
- Copy the complete exported logs from the DCM to the directory "dcmFiles"
- Run the script (python bw_exceeded5.py)
