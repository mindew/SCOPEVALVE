import dweepy
import matplotlib.pyplot as plt
import pandas as pd 

time_init = 0
hr_vals = []
times = []
for dweet in dweepy.listen_for_dweets_from('valvefitbit'):
    print(dweet)
    dweet_dict = dict(dweet)
    if time_init == 0:
        time_init = dweet_dict['content']['time']
    times.append((dweet_dict['content']['time'] - time_init)/1000)
    hr_vals.append(dweet_dict['content']['hr'])
    if ((times[-1] - time_init)/1000 >= 780):
        break

heartdf = pd.DataFrame({'Heart Rate':hr_vals,'Time':times})
heartdf.to_csv('HR'+ \
               today +'.csv', \
               columns=['Time','Heart Rate'], header=True, \
               index = False)
	
    #plt.xlim(0, times[-1])
    #plt.ylim(40,150)
    #plt.plot(times, hr_vals)
    #print(dweet)
    #if len(times) > 60:
        #break
#plt.show()
