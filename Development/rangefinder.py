import RPi.GPIO as GPIO
import time



class RangeFinder:
	
	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		self.TRIG = 23
		self.ECHO = 24
		self.calib_dist = 0  # in cm

	def initialize(self):
		"""Assign the GPIO pins and delay for 2 seconds while it settles
		"""
		print "Distance Measurement In Progress"

		GPIO.setup(self.TRIG,GPIO.OUT)
		GPIO.setup(self.ECHO,GPIO.IN)

		GPIO.output(self.TRIG, False)
		print "Waiting For Sensor To Settle"
		time.sleep(2)


	def calibration(self):
		"""Sets the calib_dist variable, which is a distance offset in cm.
		   Should be called at the very beginning before any distance_read calls.
		"""
		GPIO.output(self.TRIG, False)
		time.sleep(2)
		self.calib_dist = self.distance_read()  # in cm


	def distance_read(self):
		"""Sends ultrasonic pulse, times how long it takes to detect an echo, and 
		   then calculates the distance based on the speed of sound in air at sea level.
		   Uses the offset distance to zero out the distance reading.
		"""
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

		distance = (pulse_duration * 17150) - self.calib_dist  # 17150 = (34300 cm/s) / 2
		distance = round(distance, 2)  # distance is in cm

		# thresholds for accurate measurements
		if 0 < distance < 400:
			distance = distance
		else:
			distance = 0.0

		distance_m = distance / 100  # 171.50 = (343 m/s) / 2

		print "Raw travel time: ",pulse_duration,"s"
		print "Distance (meters):",distance_m,"meters"

		print "Distance (cm):",distance,"cm\n"

		return distance


	def wait(self):
		"""To be called in between distance reads in order to allow the sensor to settle.
		   Introduces a 1 second delay.
		"""
		GPIO.output(self.TRIG, False)
		time.sleep(0.5)

	def finish(self):
		"""Called when done using the ultrasonic sensor.
		   Uses GPIO.cleanup() function
		"""
		GPIO.cleanup()
		print "Measurement stopped"


