#!/usr/bin/python
import cv2
import numpy as np
import math
import time
import sc_config
from pl_util import current_milli_time, get_distance_from_pixels


'''
TODO:
make ECCENTRICITY dependent on craftAttitude
Clean up code 
Improve calcDistToTarget method
'''


class CircleDetector(object):



	def __init__(self):
		#load algorithm constants
		#how round a circle needs to be. Perfect circle = 1
		self.eccentricity = sc_config.config.get_float('algorithm', 'eccentricity', 0.6)
		#acceptable distance(pixels) between cocentric circle centers
		self.distance_threshold = sc_config.config.get_integer('algorithm','distance_threshold', 15)
		# number of circles needed for a valid target(times 2); 2 circles are often overlayed
		self.min_circles = sc_config.config.get_integer('algorithm','min_circles',5)
		#pixels: used to identify repeat circles(stacked circles). Problem caused by findContours()
		self.radius_tolerance = sc_config.config.get_integer('algorithm', 'radius_tolerance', 2)
		#Tolerance used in comparing actaul ratios and preceived ratios 
		self.ratio_tolerance = sc_config.config.get_float('algorithm', 'ratio_tolerance', 0.015)


		#target specific data
		#target_code is the unique ratio between rings
		target_code_def = np.array([0.8,0.91,0.76,0.84,0.7,0.66,0.49])
		self.target_code = sc_config.config.get_array('algorithm', 'target_code',target_code_def)
		#the outer_ring is a scaling factor for targets of various sizes; radius of outer ring in meters
		self.outer_ring = sc_config.config.get_float('algorithm', 'outer_ring', 0.08255)

		#define field of view
		self.cam_hfov = sc_config.config.get_float('camera', 'horizontal-fov', 70.42)
		self.cam_vfov = sc_config.config.get_float('camera', 'vertical-fov', 43.3)\

		#define camera size
		self.cam_width = sc_config.config.get_integer('camera', 'width', 640)
		self.cam_height = sc_config.config.get_integer('camera', 'height', 480)


	#analyze_frame - process an frame and look for a bullseye
	#params -child_conn: child pipe connection
	#		-img: raw image to be processed
	#		-craftAttitude: roll and pitch of aircraft
	#return -runtime: time in millis to process an image
	#		-center: tuple(x,y) of the objects position on; 'None' when no target
	#		-distance: distance in meters to the target; -1 when unable to calculate
	#		-targetEllipses: ellipses that compose the detected target 'None' when no target
	def analyze_frame(self, child_conn, img, craftAttitude):
		#start timer
		start = current_milli_time()


		#blur image and grayscale
		#img = cv2.medianBlur(img,5)

		#grayscale image
		cimg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)


		#canny edge detector
		edges = cv2.Canny(cimg,100,200,3)

		if edges is not None:

			#locate contours
			contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

			#turn contours into ellipses
			circles = np.empty((len(contours)),object)
			circlesCnt = 0
			for i in range(0,len(contours)):
				contour = contours[i]
				#make sure contour contains enough point for an ellipse
				if(len(contour) > 4):
					#detect an ellipse
					ellipse = cv2.fitEllipse(contour)
					#only take ellipses which are round
					if self.checkEccentricity(ellipse,self.eccentricity):
						circles[circlesCnt] = ellipse
						circlesCnt += 1


			#if circles were found then we look for nested circles
			if circlesCnt > 0:

				#get rid of null elements
				circles = np.resize(circles,circlesCnt)
				#look for nested ellipses
				nestedCircles = self.detectNested(circles)

				#if at least min_circles circles are nested look for target
				#Times min_circles by two because we haven't removed repeat/stacked circles yet
				if len(nestedCircles) > (self.min_circles * 2):

					#look for circles with a common center
					self.finalTarget, center = self.findCommonCenter(nestedCircles)

					#we found the target position on xy-plane
					if self.finalTarget is not None:

						#decode the target rings for a list of ring ratios
						ratios = self.tagAspectRatio(self.finalTarget)


						#try to calculate distance to target
						if ratios is not None:
							distance = self.calcDistToTarget(self.finalTarget,ratios)

							stop = current_milli_time()
							child_conn.send((stop-start,center, distance, self.finalTarget))
							return

						#unable to calculate distance due to invalid data
						else: 
							stop = current_milli_time()
							child_conn.send(( stop-start, center, -1, self.finalTarget))
							return


		#unable to locate target
		stop = current_milli_time()
		child_conn.send((stop-start,None,-1,None))
		return

	#distCenters - distance between two ellipses
	def distCenters(self,ellipse1,ellipse2):
		#distance between centers
		distance = math.sqrt(math.pow((ellipse1[0][0]-ellipse2[0][0]),2) + math.pow((ellipse1[0][1] - ellipse2[0][1]),2))
		return distance

	#detectNested- return circles which are nested within other circles
	def detectNested(self,rawCircles):
		size = len(rawCircles)
		nestedCircles = np.empty(size, object)
		nestedCnt = 0
		for i in range(0,size):
			nested = False
			for j in range(i, size):
				if i != j:
					circle1 = rawCircles[i]
					circle2 = rawCircles[j]
					#average major and minor axises
					radius1 = (circle1[1][0] + circle1[1][1]) /2.0
					radius2 = (circle2[1][0] + circle2[1][1]) /2.0

					distance = self.distCenters(circle1,circle2)
						
					#check if a circle is nested within another circle
					if(distance < math.fabs(radius1 - radius2)):
						nested = True
			#add the base circle if it is nested
			if nested:
				nestedCircles[nestedCnt] = rawCircles[i]
				nestedCnt += 1	
		#remove null objects
		nestedCircles  = np.resize(nestedCircles,nestedCnt)

		return nestedCircles


	#checkEccentricity - checks if an ellipse is 'round' enough
	def checkEccentricity(self,ellipse, threshold):
		#threshold = 1 for perfect circles
		if ellipse[1][0] * 1.0/ ellipse[1][1] > threshold:
			return True
		return False
	'''
	def findCommonCenter(self,ellipses):

		size = len(ellipses)
		minDistance = 640 #image width
		center = 0,0
		for i in range(0,size):
			nested = False
			for j in range(i, size):
				ellipse1 = ellipses[i]
				ellipse2 = ellipses[j]
				distance = math.sqrt(math.pow((ellipse1[0][0]-ellipse2[0][0]),2) + math.pow((ellipse1[0][1] - ellipse2[0][1]),2))
				if distance <= minDistance and i != j:
					minDistance = distance
					center = ellipse1[0][0], ellipse1[0][1]
		
		return center

	def ellipsesAroundCenter(ellipses, center, threshold):
		size = len(ellipses)
		centeredEllipses = np.empty(size,object)
		centeredCnt = 0
		for i in range(0,size):
				distance = math.sqrt(math.pow((ellipses[i][0][0]-center[0]),2) + math.pow((ellipses[i][0][1] - center[1]),2))
				if distance <= threshold:
					centeredEllipses[centeredCnt] = ellipses[i]
					centeredCnt += 1
		centeredEllipses = np.resize(centeredEllipses,centeredCnt)
		return centeredEllipses
	'''
	#findCommonCenter - locates a group of circles which share a the most common center. Returns the group and the center point 
	def findCommonCenter(self,nestedCircles):

		size = len(nestedCircles)

		#sort by radius
		for i in range(0,size):
			baseCircle = nestedCircles[i]
			smallestRadius = (baseCircle[1][0] + baseCircle[1][1]) /2.0
			smallest = i

			for j in range(i,size):
				circle = nestedCircles[j]
				radius = (circle[1][0] + circle[1][1]) /2.0
				if(radius < smallestRadius):
					smallestRadius = radius
					smallest = j

			nestedCircles[i] = nestedCircles[smallest]
			nestedCircles[smallest] = baseCircle

		#look at all circles
		#add all circles that are within a certain threshold distance
		#compare circle pairs and see which one has the most circles
		concentricCombos = np.empty([size,size],object)


		#start with the largest circle and scan all smaller circles and see if it is concentric with the large circle
		maxConcentricCnt = 1
		maxConcentricIndex = 0

		#stores circle centers
		xSum = np.zeros(size)
		ySum = np.zeros(size)

		for i in range(size-1,0,-1):
			outer = nestedCircles[i]
			concentricCombos[i][0] = outer
			cnt = 1
			

			for j in range(i, 0, -1):
				inner = nestedCircles[j]
				#outer circle and inner circle have same center, are different
				if (self.distCenters(outer,inner) < self.distance_threshold) and (i != j):
					#check that the circle isn't a repeat(a problem with findContours)
					previous = concentricCombos[i][cnt -1]
					radPrev = (previous[1][0] + previous[1][1]) /2.0
					radCurr = (inner[1][0] + inner[1][1]) /2.0
					#if the circle is cocentric and unique, add it
					if(radPrev - radCurr) > self.radius_tolerance:
						concentricCombos[i][cnt] = inner

						xSum[i] += inner[0][0]
						ySum[i] += inner[0][1]

						cnt += 1

			if(cnt > maxConcentricCnt):
				maxConcentricCnt = cnt
				maxConcentricIndex = i

		#no concentric circles
		if(maxConcentricCnt < self.min_circles):
			return None,None

		#choose the circle set with the most concentric circles
		mostConcentric = concentricCombos[maxConcentricIndex]
		mostConcentric = np.resize(mostConcentric, maxConcentricCnt)

		#calculate meanCenter
		meanCenter = xSum[maxConcentricIndex] / (maxConcentricCnt - 1), ySum[maxConcentricIndex]/(maxConcentricCnt - 1)

		return mostConcentric, meanCenter

	#tagAspectRatio- processes the final target and calculates the ratio between rings. returns an array of ratios
	def tagAspectRatio(self,target):
		size = len(target)
		#ratios = np.empty((size-1)*size/2.0, float)
		ratios = np.empty(size-1,float)
		cnt = 0

		for i in range(0,size-1):
			circle1 = target[i]
			circle2 = target[i+1]
			radius1 = (circle1[1][0] + circle1[1][1]) /2.0
			radius2 = (circle2[1][0] + circle2[1][1]) /2.0

			
			ratio = radius2 / radius1
			ratios[cnt] = round(ratio,3)
			cnt += 1
		return ratios			


	#calculateRingSize - based on ring ID number and target size, calculate the size of a specific ring
	def calculateRingSize(self,ringNumber):
		radius = self.outer_ring #in meters

		#actualRadius Outer ring size * ratio[n] * ratios[n + 1] ...
		for i in range(0,ringNumber):
			radius = radius * self.target_code[i]

		return radius #in meters


	#calcDistToTarget - processes a target and calculates distance to the target
	def calcDistToTarget(self,target, ratios):
		distance = 0
		readings = 0
		for i in range(0,len(ratios)):
			ratio = ratios[i]
			for j in range(0,len(self.target_code)):

				
				if(math.fabs(self.target_code[j] - ratio) <= self.ratio_tolerance):
					circle1 = target[i] #outer ring
					circle2 = target[i+1] #inner ring
					radius1 = (circle1[1][0] + circle1[1][1]) /2.0
					radius2 = (circle2[1][0] + circle2[1][1]) /2.0

					fov = math.sqrt(self.cam_vfov**2 + self.cam_hfov**2)
					img_size = math.sqrt(self.cam_width**2 + self.cam_height**2)


					dist1 = get_distance_from_pixels(radius1, self.calculateRingSize(j),fov,img_size)
					dist2 = get_distance_from_pixels(radius2, self.calculateRingSize(j+1),fov,img_size)
					distance += (dist1 + dist2 )/2.0
					
					
					readings += 1
		
		#can not decode target	
		if(readings == 0):
			return -1
		#average all distance readings
		return distance/(readings * 1.0)

