import dweepy
#import matplotlib.pyplot as plt
import pandas as pd
import datetime

time_init = 0
hr_vals = []
abs_times = []
rel_times = []
today = str(datetime.datetime.now().strftime("%Y%m%d")) 

for dweet in dweepy.listen_for_dweets_from('valvefitbit'):
    print(dweet)
    hr_dict = dict(dweet)
    if time_init == 0:
            time_init = hr_dict['content']['time']
    abs_times.append(hr_dict['content']['time'])
    rel_times.append((hr_dict['content']['time'] - time_init)/1000)
    hr_vals.append(hr_dict['content']['hr'])
    heartdf = pd.DataFrame({'Heart Rate':hr_vals,'Abs Time':abs_times, 'Rel Time':rel_times})
    heartdf.to_csv('HR'+ str(time_init) + '.csv', \
               columns=['Abs Time', 'Rel Time', 'Heart Rate'], header=True, \
               index = False)
    if (rel_times[-1] >= 800):
        break

    #plt.xlim(0, times[-1])
    #plt.ylim(40,150)
    #plt.plot(times, hr_vals)
    #print(dweet)
    #if len(times) > 60:
        #break
#plt.show()
