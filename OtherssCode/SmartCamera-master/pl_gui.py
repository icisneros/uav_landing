#!/usr/bin/python
import cv2
import numpy as np
from copy import copy


class PrecisionLandGUI(object):


	@classmethod
	#render_image - completes all gui operation according to config file
	def render_image(self, img, fps=None, target=None, distance=None, mode=None, vel=None, craftAttitude=None, locationCraft=None, locationTarget=None):
		pass

	@classmethod
	#add_predicted_location- place a marker on image where the target is suppossed to be based on GPS
	def add_predicted_location(self, img, locationCraft, locationTarget):
		pass

	@classmethod
	#add_artifical_horizon- place a bubble on image to indicate a line perpendicular to level
	def add_artifical_horizon(self, img, craftAttitude):
		pass

	@classmethod		
	#add_mode_border- put a colored border around the image to signify the control the computer has
	def add_mode_border(self, mode):
		pass

	@classmethod
	#add_velocity_vectors- add vectors to show how the commands sent to the autopilot
	def add_velocity_vectors(self, vel):
		pass

	@classmethod
	#add_target_highlight- highlight the detected target, 1.the target center 2.each ring
	def add_target_highlights(self, image, target):
		#create a shallow copy of image
		img = copy(image)
		
		if target is not None:
			for i in range(0,len(target)):
				cv2.ellipse(img,target[i],(0,255,0),2)
		return img

	@classmethod
	#add_distance - adds a distance value to image
	def add_distance(self,img, distance):
		pass

	@classmethod
	#add_fps- display actaul runtime
	def add_fps(self,img,fps):
		pass