import csv
import serial
import matplotlib.pyplot as plt

# Open com port
ser = serial.Serial('COM1', 9600)
toggle = 0
startTime = 0
with open("datafile.csv", "w") as new_file:
    csv_writer = csv.writer(new_file)

    line_count = 0
    while True:
        # Strip whitespace on the left and right side
        # of the line
        lines = ser.readline().strip()

         # Split the string "180,3600,1234" into a list ["180", "3600", "1234"]
        xyz_string_triplet = lines.split(b',')
        # if len(xyz_string_triplet) != 3:
        #    print("Ignored invalid XYZ line: " + xyz_line)
        #    continue

        # Convert the numbers from string format to integer 
        if(len(xyz_string_triplet) is 2):
            if(toggle is 0):
                startTime = long(xyz_string_triplet[1])
                time = 0
                toggle = 1
            else:
                time = (long(xyz_string_triplet[1]) - startTime)/1000

            data = int(xyz_string_triplet[0])

            # Write XYZ to the CSV file
            csv_writer.writerow([time,data])

            # Increment the line count, and stop the loop
            # once we have 10 lines
            line_count += 1
            if time >= 30:
                break

x = []
y = []

with open('datafile.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for row in plots:
        x.append(row[0])
        y.append(row[1])

plt.plot(x,y, label='Loaded from file!')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Mini-Project For The Win!')
plt.legend()
plt.show()