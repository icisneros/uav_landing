#!/usr/bin/env python


"""
-----------------------------------------------------------------------------------------
AR Tag Experimentations

-- Launch files: --
usb_cam usb_cam.launch
* or *
usb_cam usb_cam_wyaml.launch

** and **

webcam_ar_track webcam_indiv.launch
* or *
webcam_ar_track webcam_bundle.launch

-- For /ar_pose_marker msg objects: --
from ar_track_alvar_msgs.msg import AlvarMarkers

-- Need to run: --
roslaunch usb_cam usb_cam.launch
roslaunch webcam_ar_track webcam_indiv.launch
 * or * 
roslaunch ./all.launch.xml

-----------------------------------------------------------------------------------------
"""

# OpenCV
import cv2
from cv_bridge import CvBridge, CvBridgeError

# ROS
import rospy
from ar_track_alvar_msgs.msg import *
import tf

# Peripheral libraries
# import numpy as np 
import math
from math import radians
import copy





# AR Tag stuff
Tag_Detected = False
Multiple_Tags = False
Tags_Detected_List = []
Tags_Buffer = [None, None, None, None, None, None]
TAGS_BUFFER_SIZE = 6  # !!! The amount of frames that are buffered
Last_Seen_Tag = None

POS_TAG_IDEN = 0  # !!! The amount of positive identifications needed to flag Tag_Detected to True
                  # The higher the int, the more frames need to positively identify a tag (strictness is increased).

# format: {tag_id: [tag_x, tag_y, tag_z, tag_yaw, tag_pitch, tag_roll]}
Tags_Dict = {}  
# accessing:
# tag_x:      Tags_Dict[tag_id][0]
# tag_y:      Tags_Dict[tag_id][1]
# tag_z:      Tags_Dict[tag_id][2]
# tag_yaw:    Tags_Dict[tag_id][3]
# tag_pitch:  Tags_Dict[tag_id][4]
# tag_roll:   Tags_Dict[tag_id][5]


TAG0 = 0
TAG1 = 1
TAG2 = 2
TAG3 = 3
TAG4 = 4
TAG5 = 5
TAG6 = 6
TAG7 = 7
TAG8 = 8
TAG9 = 9





class ARTag():

    # ******************************************* PROCESSING ENVIRONMENT *******************************************


    # def processWebcam(self, data):
    #     image = self.bridge.imgmsg_to_cv2(data, "bgr8")
    #     # Display the resulting image
    #     cv2.imshow('Webcam', image)
    #     cv2.waitKey(3)


    def processTag(self, data):
        """index into tag data (if available):
           data.markers[0].pose.pose.position.x
           data.markers[0].pose.pose.position.y
           data.markers[0].pose.pose.position.z
        """
        global Tag_Detected
        global Tags_Detected_List
        global Tags_Dict
        global Multiple_Tags

        # buffered_bool, buffered_list = self.arBufferer(data.markers)
        # # data.markers
        # if buffered_bool: # triggers cond. if enough frames of tag have been seen
        #     Tag_Detected = True
        #     Tags_Detected_List = buffered_list
        # else:
        #     Tag_Detected = False
        #     Tags_Detected_List = None

        # rospy.loginfo("Tag_Detected")
        # rospy.loginfo(Tag_Detected)

        if data.markers:  # make sure data is not empty

            Tag_Detected = True

            len_of_dict = len(data.markers)

            if len_of_dict > 1:
                Multiple_Tags = True

            for tag in range(len_of_dict):

                tag_id = data.markers[tag].id

                # position (in meters) rounded to the nearest cm
                tag_x = round(data.markers[tag].pose.pose.position.x, 2)
                tag_y = round(-data.markers[tag].pose.pose.position.y, 2)  # inverted in the camera's reference
                tag_z = round(data.markers[tag].pose.pose.position.z, 2)

                # pose angles (in radians).  range restricted: -pi to +pi
                tag_angles = self.quaternion_to_euler(data.markers[tag])

                # populate the global dict
                Tags_Dict[tag_id] = [tag_x, tag_y, tag_z] + tag_angles

            rospy.loginfo("tags_dict = ")
            rospy.loginfo(Tags_Dict)
        else:
            Tag_Detected = False
            Multiple_Tags = False
            # remember to empty the dict every loop
            Tags_Dict = {}



    # ************************************ AR TAG FUNCTIONS ************************************



    def quaternion_to_euler(self, artag):
        """Uses the quaternion coordinates to calculate the euler angles.
           Arguments: a data.marker object
           Returns: a list of rounded floats in the form: [tag_yaw, tag_pitch, tag_roll]
        """

        qt_x = artag.pose.pose.orientation.x
        qt_y = artag.pose.pose.orientation.y
        qt_z = artag.pose.pose.orientation.z
        qt_w = artag.pose.pose.orientation.w


        quaternion = (qt_x, qt_y, qt_z, qt_w)
        euler = tf.transformations.euler_from_quaternion(quaternion)
        tag_roll = round(euler[0], 2)
        tag_pitch = round(euler[1], 2)
        tag_yaw = round(euler[2], 2)


        return [tag_yaw, tag_pitch, tag_roll]

    

    def arBufferer(self, tags):
        """Returns True and a tag list if at least one tag is identified
           within a series of size TAGS_BUFFER SIZE
        """
        global Tags_Buffer

        sizeOf = 0

        if tags is not None:
            sizeOf = len(tags)

        if sizeOf > 0:
            Tags_Buffer.append(tags)
        else:
            Tags_Buffer.append(None)
        Tags_Buffer.pop(0)  # pop first item in list


        buffered_tag_list = None
        emptyFrames = 0

        for i in range(0, TAGS_BUFFER_SIZE):
            if Tags_Buffer[i] is None:
                emptyFrames += 1
            else:
                buffered_tag_list = Tags_Buffer[i]  # will return last frame where there was a tag spotted
        
        # If a tag is seen at least once, set to true
        # We get more false negatives than false positives, so this is the way we can 
        # deal with it.
        if TAGS_BUFFER_SIZE - emptyFrames > POS_TAG_IDEN:
            tagDetected = True
        else:
            tagDetected = False

        return tagDetected, buffered_tag_list


    def oriented_properly(self, single_est):
        """Returns a boolean which states whether the orientation is proper.
           'Proper' orientation is defined as:
           yaw ~ 0
           pitch ~ 0
           roll ~ +/- pi

           Thresholds give around 15 degrees (0.2 rad) of leeway in each direction of rotation 
           (since we use the absolute value of the angle)

           Argument single_est is a dict with only on key value pair.  It is either a single tag
           id (since only one was identified) or the id = 'center'

        """
        yaw_good = False
        pitch_good = False
        roll_good = False


        for tag_id in single_est.keys():
            tag_yaw = abs(single_est[tag_id][3])
            tag_pitch = abs(single_est[tag_id][4])
            tag_roll = abs(single_est[tag_id][5])

            if 0.0 <= tag_yaw <= 0.2:
                yaw_good = True
            if 0.0 <= tag_pitch <= 0.2:
                pitch_good = True
            if 2.9 < tag_roll:
                roll_good = True

        return yaw_good and pitch_good and roll_good


    def mean_measurements(self):
        """If multiple tags are detected, returns a dict with the mean measurements of positions
           and orientations.

           Returns a dict of format: {'center': [mean_x, mean_y, mean_z, mean_yaw, mean_pitch, mean_roll]}

        """

        num_of_tags = len(Tags_Dict)

        mean_x = 0.0
        mean_y = 0.0
        mean_z = 0.0
        mean_yaw = 0.0
        mean_pitch = 0.0
        mean_roll = 0.0

        ## TODO: get the means
        for tagid in Tags_Dict.keys():
            mean_x += Last_Known_vars[i][0]
            mean_y += Last_Known_vars[i][1]
            mean_z += Last_Known_vars[i][2]
            mean_yaw += Last_Known_vars[i][3]
            mean_pitch += Last_Known_vars[i][4]
            mean_roll += Last_Known_vars[i][5]

        
        m_measurements = [mean_x, mean_y, mean_z, mean_yaw, mean_pitch, mean_roll]
        m_measurements = [ round(elem, 2) for elem in m_measurements ]  # round all elements to 2 decimal places

        return {'center': m_measurements}


    def fsm(self):

        if Tag_Detected:

            single_estimate = copy.deepcopy(Tags_Dict)

            if Multiple_Tags:
                # If multiple tags are detected, get the means
                single_estimate = self.mean_measurements()
                # other wise, single_estimate dict has only one key value pair

            # Check if orientation is proper
            if self.oriented_properly(single_estimate):
                rospy.loginfo("Oriented properly!")
            else:
                rospy.loginfo("NOT oriented properly")

            rospy.loginfo("single_estimate = ")
            rospy.loginfo(single_estimate)


        self.r.sleep()



    def __init__(self):
        global STATE
        rospy.init_node('artag_node', anonymous=False)
        # ctrl + c -> call self.shutdown function
        rospy.on_shutdown(self.shutdown)
        # print msg 
        rospy.loginfo("Initializing...")

        # offers a convenient way for looping at the desired rate. Default is 10hz
        self.r = rospy.Rate(10);

        self.bridge = CvBridge()

        # Subscribe to depth sensor
        rospy.Subscriber('/ar_pose_marker', AlvarMarkers, self.processTag, queue_size=1,  buff_size=2**24)

        # Webcam subscriber
        # rospy.Subscriber('/image_raw', Image, self.processWebcam, queue_size=1,  buff_size=2**24)

        # Movement publisher
        # self.wheels = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
        # Publish to velocity smoother publisher 
        # self.wheels = rospy.Publisher('velocity_smoother/raw_cmd_vel', Twist, queue_size=10)



        rospy.loginfo("Finished init...\n")
        while not rospy.is_shutdown():
            self.fsm()


    def shutdown(self):
        cv2.destroyAllWindows()
        # stop robot
        rospy.loginfo("Stopping Script")
        # sleep just makes sure TurtleBot receives the stop command prior to shutting down the script
        rospy.sleep(1)
        sys.exit()


if __name__ == '__main__':
    try:
        ARTag()
    except Exception as e:
        print e
        rospy.loginfo("ARTag node terminated.")