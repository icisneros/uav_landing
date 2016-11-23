from rangefinder import RangeFinder
import numpy as np


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
	rf = RangeFinder()

	rf.initialize()


	print "Calibrating..."
	rf.calibration()


	try:
		# For continuous reading
		while True:
			print "Median Distance: ", median_distance(),"cm\n"

		# For a single shot read
		# rf.distance_read()
	except KeyboardInterrupt:
		rf.finish()