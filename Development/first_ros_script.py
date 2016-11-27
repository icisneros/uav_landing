"""
AR Tag Experimentations

-- Launch file package: --
ar_track_alvar package for launch file

-- For /ar_pose_marker msg objects: --
from ar_track_alvar_msgs.msg import AlvarMarkers

-- Need to run: --
roslaunch usb_cam usb_cam.launch
roslaunch webcam_ar_track webcam_indiv.launch
 * or * 
roslaunch webcam_ar_track webcam_bundle.launch

"""
# OpenCV
import cv2
from cv_bridge import CvBridge, CvBridgeError

# ROS
import rospy
from ar_track_alvar_msgs.msg import *

# Peripheral libraries
# import numpy as np 
import math
from math import radians



# # Speeds
# LIN_SPEED = 0.15  # might need to up this from 0.5
# SLOW_ROT_SPEED = radians(25)
# ROT_SPEED = radians(60) # slight turns
# ROT90 = radians(90)  # 90 degree turns


# # AR Tag stuff
Tag_Detected = False
Tags_Detected_List = None
# Tags_Buffer = [None, None, None, None, None, None]
# TAGS_BUFFER_SIZE = 6

# Last_Seen_Tag = None

# # Decided at beginning
# BarTagID = 0

# # EXPERIMENTALLY DETERMINED
# RIGHT_THRESH = 0.13
# LEFT_THRESH = -0.13
# DISTANCE_THRESH = 0.13
# BAR_RIGHT_THRESH = 0.10
# BAR_LEFT_THRESH = -0.10
# BAR_DISTANCE_THRESH = 0.15
# TIGHT_R_THRESH = 0.03
# TIGHT_L_THRESH = -0.03


# # FSM states
# START = 0
# APR_BAR = 1
# NEXT = 2



class ARTag():


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
        # rospy.loginfo("data: ")

        buffered_bool, buffered_list = self.arBufferer(data.markers)
        # data.markers
        if buffered_bool: # triggers cond. if enough frames of tag have been seen
            Tag_Detected = True
            Tags_Detected_List = buffered_list
        else:
            Tag_Detected = False
            Tags_Detected_List = None

        rospy.loginfo("Tag_Detected")
        rospy.loginfo(Tag_Detected)


    def arBufferer(self, tags):
        """Returns True and a tag list if at least one tag is identified
           within a series of size TAGS_BUFFER SIZE
        """
        global Tags_Buffer


        if tags is not None:
            sizeOf = len(tags)
        else:
            sizeOf = 0
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
        if TAGS_BUFFER_SIZE - emptyFrames > 0:
            tagDetected = True
        else:
            tagDetected = False

        return tagDetected, buffered_tag_list


    # def returnIDandCoord(self,listItem):
    #     """Returns a tuple
    #        in the form (tagID_1, (x_1,y_1,z_1))
    #     """
    #     tagID = listItem.id
    #     x = listItem.pose.pose.position.x
    #     y = listItem.pose.pose.position.y
    #     z = listItem.pose.pose.position.z
    #     return (tagID, (x,y,z))


    # def convertTagPosition(self, tagList):
    #     """Returns a list
    #        in the form [(tagID_1, (x_1,y_1,z_1)), (tagID_2, (x_2,y_2,z_2)), ...]
    #     """
    #     newList = []
    #     if tagList is not None:
    #         sizeOf = len(tagList)
    #     else:
    #         sizeOf = 0
    #     if sizeOf > 0:  # ideally this case is checked before the function is called...
    #         for i in range(0, sizeOf):
    #             useful = self.returnIDandCoord(tagList[i])
    #             newList.append(useful)
    #     else:
    #         return None

    #     return newList, sizeOf



    # def approachATag(self, tag):
    #     """
    #         STATE -> same
    #               or 
    #               -> NEXT


    #     Takes a tag coordinates and centers the camera on it.
    #        Moves towards it until the z coordinate (depth) is 
    #        below a certain threshold.
    #     """
    #     global STATE
        
    #     move_recommend = Twist()
        
    #     if Tag_Detected:
    #         self.lastSeenTagUpdate(tag)

    #         (tagID, (x_coord, y_coord, z_coord)) = tag

    #         if tagID == BarTagID:  # different thresh for the Bar tag
    #             right_thresh = BAR_RIGHT_THRESH
    #             left_thresh = BAR_LEFT_THRESH
    #             dist_thresh = BAR_DISTANCE_THRESH
    #         else:
    #             right_thresh = RIGHT_THRESH
    #             left_thresh = LEFT_THRESH
    #             dist_thresh = DISTANCE_THRESH

    #         # Center the tag
    #         if x_coord > right_thresh:
    #             move_recommend.angular.z = -ROT_SPEED  # turn left
    #         elif x_coord < left_thresh:
    #             move_recommend.angular.z = ROT_SPEED  # turn right
    #         else:
    #             move_recommend.angular.z = 0

    #         # Move towards tag; check for distance
    #         if z_coord > dist_thresh:
    #             move_recommend.linear.x = LIN_SPEED
    #         else:
    #             move_recommend.linear.x = 0
    #             # Center the tag once up close
    #             if x_coord > TIGHT_R_THRESH:
    #                 move_recommend.angular.z = -ROT_SPEED  # turn left
    #             elif x_coord < TIGHT_L_THRESH:
    #                 move_recommend.angular.z = ROT_SPEED  # turn right
    #             else:
    #                 move_recommend.angular.z = 0
    #                 # STATE = NEXT
    #     else:
    #         move_recommend.linear.x = 0
    #         move_recommend.angular.z = 0

    #     return move_recommend



    # def lookForBarAtStart(self):
    #     """ 
    #         STATE -> same
    #               or
    #               -> APR_BAR


    #         Will spin until it spots the Bar AR tag.
    #     """
    #     global STATE

    #     #tagsList = list(Tags_Detected_List)

    #     move_obj = Twist()
    #     move_obj.linear.x = 0
    #     move_obj.angular.z = SLOW_ROT_SPEED
        
    #     if Tag_Detected:
    #         rospy.loginfo("Iterating through tags")
    #         tags, sizeOf = self.convertTagPosition(Tags_Detected_List)
    #         if sizeOf > 0:
    #             for i in range(0, sizeOf):
    #                 tagID, tag_coords = tags[i]

    #                 if tagID == BarTagID:  # found Bar tag; stop rotating
    #                     STATE = APR_BAR     # Change the STATE
    #                     move_obj.angular.z = 0
    #                     break

    #             return move_obj
    #         else:
    #             # Odd case where Tag_Detected is true but that data list is empty
    #             rospy.loginfo("Error, AR tags list is empty")
    #             return move_obj
    #     else:
    #         # defaults to same STATE
    #         # default move is to rotate ad infinitum
    #         return move_obj


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
        rospy.loginfo("Running fsm function\n")



    def __init__(self):
        global STATE
        rospy.init_node('ARTag', anonymous=False)
        # ctrl + c -> call self.shutdown function
        rospy.on_shutdown(self.shutdown)
        # print msg 
        rospy.loginfo("Initializing...")
        # How often should provide commands? 10 HZ
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

        # Necessary so that bot can take an action without moving
        # move_obj = Twist()
        # move_obj.linear.x = 0
        # move_obj.angular.z = 0

        # # Initial FMS State
        # STATE = START


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