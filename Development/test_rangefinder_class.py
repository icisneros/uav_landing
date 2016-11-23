from rangefinder import RangeFinder


if __name__ == '__main__':
	rf = RangeFinder()

	rf.initialize()


	print "Calibrating..."
	rf.calibration()


	try:
		# For continuous reading
		while True:
			rf.distance_read()
			rf.wait()

		# For a single shot read
		# rf.distance_read()
	except KeyboardInterrupt:
		rf.finish()