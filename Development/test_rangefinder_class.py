from rangefinder import RangeFinder


def mean_distance():
	distances = []

	for i in range(0,5):	
		distances.append(rf.distance_read())
		rf.wait()

	suff_nonzero = 0
	for i in range(0,5):
		if distances[1] != 0:
			suff_nonzero += 1

	if suff_nonzero >= 3:
		return reduce(lambda x, y: x + y, distances) / len(distances)
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
			print "Mean Distance: ", mean_distance(),"cm\n"

		# For a single shot read
		# rf.distance_read()
	except KeyboardInterrupt:
		rf.finish()