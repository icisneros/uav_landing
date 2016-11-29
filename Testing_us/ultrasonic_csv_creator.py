# Testing Control
CSV_NAME = 'measz_vs_actz_0_25m.csv'
# CSV_NAME = 'measz_vs_xoffs_0.01moffs_0_25m.csv'
# CSV_NAME = 'acc_vs_zdist_0_25mstart.csv'
MAX_ITERS = 1
ACT_DIST = 0.25   # in meters
XOFFS = 0   # in meters


"""
-----------------------------------------------------------------------------------------
Rangfinder Testing

-- Launch files: --
none

-- For /ar_pose_marker msg objects: --
none

-- Need to run: --
with sudo

-----------------------------------------------------------------------------------------
"""


# Peripheral libraries
# import numpy as np 
import math
from math import radians
import copy

# For testing
import csv



from rangefinder import RangeFinder
import numpy as np



# For testing 
ITERATIONS = 0
Last_Known_vars = []
DATA_POINT = 1



def median_distance():
    """Takes 3 readings. If 2/3 values are non zero, return the median value. Else
       returns 0.0
    """

    distances = []

    for i in range(0,3):    
        distances.append(rf.distance_read())
        rf.wait()

    num_nonzero = 0
    for i in range(0,3):
        if distances[1] != 0.0:
            num_nonzero += 1
    
    # remove the zeros
    while 0.0 in distances:
        distances.remove(0.0)

    if num_nonzero >= 2:  # if 2/3 values are non zero, return the median
        return np.median(distances)
        # return reduce(lambda x, y: x + y, distances) / num_nonzero
    else:
        return 0.0



if __name__ == '__main__':
    
    print "Initializing...\n"

    rf = RangeFinder()

    rf.initialize()


    print "Finished initialization.\n"


    # print "Calibrating..."
    # rf.calibration()


    try:
        print "Creating csv...\n"

        with open(CSV_NAME, 'wb') as csvfile:

            # fieldnames = ['DATA_POINT', 'accuracy', 'med_dist', 'ACT_DIST', 'XOFFS']

            spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            
            print "Begin writing to csv file...\n"
            # For continuous reading
            while True:
                med_dist = median_distance()

                print "Median Distance: ", med_dist," meters\n"

                # Testing, CSV stuff:
                ITERATIONS += 1

                # make sure we only iterate NUMBER_DETECTED if tag 0 is detected
                if med_dist > 0.0:
                    NUMBER_DETECTED += 1


                # at MAX_ITERS number of iterations, calculate the detection percentage vs the independent variable
                if ITERATIONS == MAX_ITERS:
                    accuracy = (float(NUMBER_DETECTED) / ITERATIONS) * 100  # given as a percentage

                    which_vars = [DATA_POINT, accuracy, med_dist, ACT_DIST, XOFFS]

                    print "Writing to CSV file...\n"
                    spamwriter.writerow(which_vars)

                    print "Datapoint = ", str(DATA_POINT)
                    DATA_POINT += 1
                    ITERATIONS = 0
                    NUMBER_DETECTED = 0
                    Last_Known_vars = []


    except KeyboardInterrupt:
        rf.finish()


