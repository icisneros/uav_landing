import RPi.GPIO as GPIO
import time
# GPIO.setmode(GPIO.BCM)

# TRIG = 23 
# ECHO = 24


class RangeFinder:
	
	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		self.TRIG = 23
		self.ECHO = 24

	def initialize(self):
		print "Distance Measurement In Progress"

		GPIO.setup(self.TRIG,GPIO.OUT)
		GPIO.setup(self.ECHO,GPIO.IN)

		GPIO.output(self.TRIG, False)
		print "Waiting For Sensor To Settle"
		time.sleep(2)


	def distance_read(self):
		# send ultrasonic pulse
		GPIO.output(self.TRIG, True)
		time.sleep(0.00001)  # 10uS pules
		GPIO.output(self.TRIG, False)

		# listen for the echo
		while GPIO.input(self.ECHO)==0:
			pulse_start = time.time()

		# echo was heard
		while GPIO.input(self.ECHO)==1:
			pulse_end = time.time()

		# time differential; time.time() returns the time in seconds
		pulse_duration = pulse_end - pulse_start

		distance = pulse_duration * 17150  # 17150 = (34300 cm/s) / 2
		distance = round(distance, 2)  # distance is in cm

		distance_m = pulse_duration * 171.50  # 171.50 = (343 m/s) / 2
		# distance_m = round(distance, 2)  # distance is in meters

		print "Raw travel time: ",pulse_duration,"s"
		print "Distance (meters):",distance_m,"meters"

		print "Distance (cm):",distance,"cm\n"


	def finish(self):
		GPIO.cleanup()


