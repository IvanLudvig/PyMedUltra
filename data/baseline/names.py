import os #Script to change the names of files
import re
files= os.listdir()
print(files)
tpl = r'Sensor\S+'
for i in files:
    if re.match(tpl, i):
        os.remove(i)
