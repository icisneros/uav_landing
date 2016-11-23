from rangefinder import RangeFinder


if __name__ == '__main__':
	rf = RangeFinder()

	rf.initialize()

	# For continuous reading
	# while True:
	# 	rf.distance_read()

	# For a single shot read
	rf.distance_read()


	rf.finish()