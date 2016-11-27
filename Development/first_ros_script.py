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





# AR Tag stuff
Tag_Detected = False
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
        # rospy.loginfo("data: ")

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

            for tag in range(len(data.markers)):

                tag_id = data.markers[tag].id

                # position (in meters) rounded to the nearest cm
                tag_x = round(data.markers[tag].pose.pose.position.x, 2)
                tag_y = round(-data.markers[tag].pose.pose.position.y, 2)  # inverted in the camera's reference
                tag_z = round(data.markers[tag].pose.pose.position.z, 2)

                # pose
                tag_angles = self.quaternion_to_euler(data.markers[tag])

                # populate the global dict
                Tags_Dict[tag_id] = [tag_x, tag_y, tag_z]

            rospy.loginfo("tags_dict = ")
            rospy.loginfo(Tags_Dict)
        else:
            # remember to empty the dict every loop
            Tags_Dict = {}



    # ************************************ AR TAG FUNCTIONS ************************************



    def quaternion_to_euler(self, artag):

        qt_x = artag.pose.pose.orientation.x
        qt_y = artag.pose.pose.orientation.y
        qt_z = artag.pose.pose.orientation.z
        qt_w = artag.pose.pose.orientation.w



        quaternion = (qt_x, qt_y, qt_z, qt_w)
        euler = tf.transformations.euler_from_quaternion(quaternion)
        roll = euler[0]
        pitch = euler[1]
        yaw = euler[2]

        # tag_yaw = 
        # tag_pitch
        # tag_roll


        # return [tag_yaw, tag_pitch, tag_roll]
        return 0.0
        # pass
    

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


    def returnIDandCoord(self,listItem):
        """Returns a tuple
           in the form (tagID_1, (x_1,y_1,z_1))
        """
        tagID = listItem.id
        x = listItem.pose.pose.position.x
        y = listItem.pose.pose.position.y
        z = listItem.pose.pose.position.z
        return (tagID, (x,y,z))


    def convertTagPosition(self, tagList):
        """Returns a list
           in the form [(tagID_1, (x_1,y_1,z_1)), (tagID_2, (x_2,y_2,z_2)), ...]
        """
        newList = []
        if tagList is not None:
            sizeOf = len(tagList)
        else:
            sizeOf = 0
        if sizeOf > 0:  # ideally this case is checked before the function is called...
            for i in range(0, sizeOf):
                useful = self.returnIDandCoord(tagList[i])
                newList.append(useful)
        else:
            return None

        return newList, sizeOf


    def lastSeenTagUpdate(self, tag):
        global Last_Seen_Tag
        if tag is not None:
            Last_Seen_Tag = tag



    # def lastSeenTagUpdate(self, tag):
    #     global Last_Seen_Tag
    #     if tag is not None:
    #         Last_Seen_Tag = tag


    # def isolateATag(self, idTagToIsolate):
    #     """Returns the (x,y,z) coordinates of a specific tag
    #        If tag not in the list of visible tags, returns None
    #     """
    #     #tagsList = list(Tags_Detected_List)

    #     if Tag_Detected:
    #         tags, sizeOf = self.convertTagPosition(Tags_Detected_List)

    #         if sizeOf > 0:  # ideally this case is checked before the function is called...
    #             for i in range(0, sizeOf):
    #                 tagID, tag_coords = tags[i]

    #                 if tagID == idTagToIsolate:
    #                     return tag_coords

    #             # Case where wanted tag is not in the list of visible tags
    #             return None
    #         else:
    #             # Odd case where Tag_Detected is true but that data list is empty
    #             rospy.loginfo("Error, AR tags list is empty")
    #             return None
    #     else:
    #         rospy.loginfo("Error, no AR tags in sight. Can't use this function.")
    #         return None



    # def fsm(self):
    #     global STATE
        
    #     # Sense before entering finite state machine
    #     if Tags_Detected_List is not None:
    #         tagsList = list(Tags_Detected_List)
    #     else: 
    #         tagsList = None
    #     tagDetected = Tag_Detected
    #     # if not OBSTACLE_DETECTED:

    #     move_recommend = Twist()
    #     move_recommend.linear.x = 0
    #     move_recommend.angular.z = 0

    #     if tagDetected:
    #         rospy.loginfo("move_recommend.angular.z")
    #         if tagsList is not None:
    #             tags, tags_list_size = self.convertTagPosition(tagsList)
    #         else:
    #             tags = Last_Seen_Tag

    #         # rospy.loginfo("tags[0]")
    #         # rospy.loginfo(tags[0])

    #         # rospy.loginfo("approachATag")
    #         move_recommend = self.approachATag(tags[0])
    #         # rospy.loginfo("Done with approachATag")

    
    #     rospy.loginfo("Last seen tag")
    #     rospy.loginfo(Last_Seen_Tag)
    #     # rospy.loginfo("move_recommend.angular.z")
    #     # rospy.loginfo(move_recommend.angular.z)
    #     self.wheels.publish(move_recommend)
    #     self.r.sleep()
    #     # pass


    def fsm(self):
        # rospy.loginfo("Running fsm function\n")
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



        rospy.loginfo("Finished init...")
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