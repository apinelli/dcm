import glob
import os
import tarfile
import gzip, shutil
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

pd.set_option('mode.chained_assignment', None)
register_matplotlib_converters()

def get_bw(file):
    list_json = []
    with open(file, mode='r') as d:
        for line in d.readlines():
            line = line.strip("@cee: ")
            line_json = json.loads(line)
            list_json.append(line_json)
    return list_json

# def prep_dcm_logs(logs):
path = os.getcwd()
path_tgz = (path + "/dcmFiles/*.tgz")
original_tar = glob.glob(path_tgz)
os.chdir(path + "/dcmFiles/")
tar = tarfile.open(os.path.basename(original_tar[0]))
tar.extractall()
tar.close()
os.chdir(path + "/dcmFiles/tmp/.var.log-ro/")

alarms = (glob.glob(path + "/dcmFiles/tmp/.var.log-ro/alarms*.gz"))
with gzip.open(alarms[0], 'rb') as f_in:
    with open(path + "/dcmFiles/tmp/.var.log-ro/0-file", 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

source = path + "/dcmFiles/tmp/.var.log-ro/"
destination = path + "/dcmFiles/unzipped_alarms"
extension = ".gz"
alarms = (glob.glob(path + "/dcmFiles/tmp/.var.log-ro/alarms*.gz"))
os.mkdir(destination)

for i, alarm in enumerate(alarms):
    alarm = os.path.join(source, alarm)
    alarm_without_path = os.path.split(alarm)[1]
    dest = os.path.join(destination, os.path.splitext(alarm_without_path)[0])

    with gzip.open(alarm, "rt") as zip:
        with open(dest, "w") as out:
            for line in zip:
                out.write(line)

# Concatenate all alarms into one file:
read_files = glob.glob("/home/angelo/projects/dcm/dcmFiles/unzipped_alarms/*.*")
with open("all_alarms", "wb") as outfile:
    for f in read_files:
        with open(f, "rb") as infile:
            outfile.write(infile.read())

lista = get_bw("all_alarms")
df = pd.DataFrame(lista)
df1 = df[['msg','time','detail']]

df_bw = df1.loc[df['msg'] == 'Bandwidth Exceeded'] # selecting only the lines with BW Exceeded
df_dejitter = df1.loc[df['msg'] == 'Dejitter Buffer Reset'] # selecting only the lines with Dejitter Buffer Reset
df_dejitter = df_dejitter.loc[df_dejitter['detail'] == 'TS=239.56.1.2:5612=;Source IP=192.168.65.2=;']  # Selecting only the OIT

df_bw = df_bw.sort_values(['detail', 'time'], ascending=[1,1])  # sorting by TS and time
df_bw['time'] = pd.to_datetime(df_bw['time']) # Converting time string to time time
df_bw['detail'] = df_bw['detail'].str.replace('TS=','') # Adjusting the TS column
df_bw['detail'] = df_bw['detail'].str.replace(':.+','') # Adjusting the TS column

output_streams = list(df_bw['detail'].unique()) # Getting unique transport streams that suffer from BW Exceeded

# Preparing the plot of BW Exceeded occurrences for all transport streams
for ts in range(len(output_streams)):
    temp = df_bw.loc[df_bw['detail'] == output_streams[ts]]
    sLength = len(temp)
    temp.loc[:, output_streams[ts]] = pd.Series(np.full((sLength), output_streams[ts]), index=temp.index)
    plt.plot(temp['time'], temp[output_streams[ts]], '.')

plt.title("BW Exceeded alarms for OIT multicast")
plt.xticks(rotation='vertical')
plt.subplots_adjust(bottom=0.3)
plt.show()
