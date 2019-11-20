import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


num_channels = 8
sample_rate = 250
data_tuples = []

data = open("OpenBCI-RAW-2019-11-20_13-57-26.txt", "r")

while(True):
    line = data.readline()
    print(line)
    if "%" in line:
        continue
    if line == "":
        break
    line_list = line.split(", ")
    print(line_list)
    data_tuples.append((line_list[0], line_list[2], line_list[3], line_list[13]))


x = np.array(data_tuples,
             dtype=[('index', 'i4'), ('corrugator', 'f8'), ('zygomaticus', 'f8'), ('timestamp', 'i8')])
print(x)
print(x['index'])
plt.plot(x['timestamp'],x['corrugator'])
plt.show()
