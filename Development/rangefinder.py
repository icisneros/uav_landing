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
		GPIO.output(self.TRIG, True)
		time.sleep(0.00001)
		GPIO.output(self.TRIG, False)

		while GPIO.input(self.ECHO)==0:
		  pulse_start = time.time()

		while GPIO.input(self.ECHO)==1:
		  pulse_end = time.time()

		pulse_duration = pulse_end - pulse_start

		distance = pulse_duration * 17150

		distance = round(distance, 2)

		print "Distance:",distance,"cm"


	def finish(self):
		GPIO.cleanup()


