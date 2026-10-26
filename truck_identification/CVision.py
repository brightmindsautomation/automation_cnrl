import cv2
import numpy as np
import imutils
from configparser import ConfigParser
import AccessSql
import vlc
import time
import pandas as pd
import subprocess
import shutil
from datetime import datetime, date


# from operator import itemgetter, attrgetter


# Global Variable #
def nothing():
    pass


## Configuration file and initial settings ##
ConfigFile = 'cvision_config.ini'
config = ConfigParser()
config.read(ConfigFile)

# Runtime environment
execEvnr = config['CAMERA']['envr']

# Camera feed
# VideoFeedName = config['CAMERA']['camera_path']
VideoFeedName = 'E:/Actual_python38/CVision/vision.mkv'
StartFrameNo = int(config['CAMERA']['start_frame_no'])
AngelOfRotation = int(config['CAMERA']['angel_of_rotation'])
feed_condition = config['CAMERA']['feed_condition']
feed_condition_orig = config['CAMERA']['feed_condition']

# VideoFeedName = '/media/ubuntu/OPEN CV/ongc_video/new_14_video.mkv'

AllowDevInPcntg = int(config['CAMERA']['allow_deviation_in_pcntg'])
PermitDeviation = int(config['CAMERA']['permit_deviation'])

# Rtsp feed
RtspVideoFeedName = config['CAMERA']['rtsp_camera_path']

# Motion Capture Settings
Motion_Capture_Active = config['CAMERA']['Motion_Capture_Active']
Motion_Capture_Refr_Frame = int(config['CAMERA']['Motion_Capture_Refr_Frame'])

# Site glass filters
Site_Glass_60_80_upper_hsv = np.fromstring(config['SITE_GLASS']['Site_Glass_60_80_upper_hsv'][1:-1]
                                           , sep=',').astype(int)
# np.array(list(config['SITE_GLASS']['Site_Glass_60_80_upper_hsv']), dtype=int)
Site_Glass_60_80_lower_hsv = np.fromstring(config['SITE_GLASS']['Site_Glass_60_80_lower_hsv'][1:-1]
                                           , sep=',').astype(int)

Site_Glass_20_40_upper_hsv = np.fromstring(config['SITE_GLASS']['Site_Glass_20_40_upper_hsv'][1:-1]
                                           , sep=',').astype(int)
Site_Glass_20_40_lower_hsv = np.fromstring(config['SITE_GLASS']['Site_Glass_20_40_lower_hsv'][1:-1]
                                           , sep=',').astype(int)

Min_20T_Val_For_40_Select = int(config['SITE_GLASS']['Min_20T_Val_For_40_Select'])
Min_40T_Val_For_60_Select = int(config['SITE_GLASS']['Min_40T_Val_For_60_Select'])
Min_60T_Val_For_80_Select = int(config['SITE_GLASS']['Min_60T_Val_For_80_Select'])

SG60_Good_Feed_Threshold = int(config['SITE_GLASS']['SG60_Good_Feed_Threshold'])
SG60_Bad_Feed_Threshold = int(config['SITE_GLASS']['SG60_Bad_Feed_Threshold'])

SG20_Feed_Threshold = int(config['SITE_GLASS']['SG20_Feed_Threshold'])
SG40_Feed_Threshold = int(config['SITE_GLASS']['SG40_Feed_Threshold'])
SG80_Feed_Threshold = int(config['SITE_GLASS']['SG80_Feed_Threshold'])

# Sand Level identification filter
Sand_Lvl_upper_hsv = np.fromstring(config['SAND_IDENT_FILTER']['Sand_lvl_upper_hsv'][1:-1]
                                   , sep=',').astype(int)
Sand_Lvl_lower_hsv = np.fromstring(config['SAND_IDENT_FILTER']['Sand_lvl_lower_hsv'][1:-1]
                                   , sep=',').astype(int)

Sand_Lvl_40_upper_hsv = np.fromstring(config['SAND_IDENT_FILTER']['Sand_lvl_40_upper_hsv'][1:-1]
                                      , sep=',').astype(int)
Sand_Lvl_40_lower_hsv = np.fromstring(config['SAND_IDENT_FILTER']['Sand_lvl_40_lower_hsv'][1:-1]
                                      , sep=',').astype(int)

Sand_Lvl_20_lower_hsv = np.fromstring(config['SAND_IDENT_FILTER']['Sand_lvl_20_lower_hsv'][1:-1]
                                      , sep=',').astype(int)
Sand_Lvl_20_upper_hsv = np.fromstring(config['SAND_IDENT_FILTER']['Sand_lvl_20_upper_hsv'][1:-1]
                                      , sep=',').astype(int)

# OPC Connection attributes
Write_To_OPC = config['OPC']['Write_To_OPC']
Write_To_OPC_Exec = config['OPC']['Write_To_OPC_Exec']
OPC_Server_Name = config['OPC']['OPC_Server_Name']
OPC_Write_Address = config['OPC']['OPC_Write_Address']
OPC_Write_Freq_In_Frames = config['OPC']['OPC_Write_Freq_In_Frames']

Show_Video = config['DISPLAY']['Show_Video']

# ELK settings
Elk_Host = config['ELK']['Elk_Host']
Elk_IndexName = config['ELK']['Elk_IndexName']

# DB Settings
Purge_No_Of_Days = config['DATABASE']['Purge_No_Of_Days']

##################################################################
List_Size = int(config['EQUALIZER']['List_Size'])
#################################################################

Elk_Dict = {
}

# DB Objects Initialization
CvDb = AccessSql.CrtConnObject()
Blue_Tube_Initiater = [(687, 915, 201, 564), (703, 115, 199, 604), (344, 516, 195, 591), (354, 1306, 183, 511)]
Db_Value_Log = ''
Db_Algo_Level = ''
f_curr_frame_no = 0
frame_total = 1
No_of_Tubes_Identified = 0
Site_Glass_Contours = []
# Time objects
now = time.localtime(time.time())
total_seconds = 0

Algo_Yaxis_Lvl = 0
tmp_Algo_Yaxis_Lvl = 0

Yax_Algo_Lvl = []

tube_level_dict = {
    "S-20": 1,
    "S-40": 2,
    "S-60": 3,
    "S-80": 4,
    "PREV": 0,
    "INIT": 0,
    "EMPTY": 0
}

prev_frame = []
# curr_frame =[]
Video_Name = ''
Moca_Kpi = ''

# Residue identifiers

res_list_20 = np.fromstring(config['RESIDUE']['res_20_A1'][1:-1], sep=',').astype(int)
res_list_40 = np.fromstring(config['RESIDUE']['res_40_A1'][1:-1], sep=',').astype(int)
res_list_60 = np.fromstring(config['RESIDUE']['res_60_A1'][1:-1], sep=',').astype(int)
res_list_80 = np.fromstring(config['RESIDUE']['res_80_A1'][1:-1], sep=',').astype(int)

Mask_Glass_20 = config['RESIDUE']['Mask_Glass_20']
Mask_Glass_40 = config['RESIDUE']['Mask_Glass_40']
Mask_Glass_60 = config['RESIDUE']['Mask_Glass_60']
Mask_Glass_80 = config['RESIDUE']['Mask_Glass_80']

sg_20_res = [(res_list_20[0], res_list_20[1])]
sg_40_res = [(res_list_40[0], res_list_40[1])]
sg_60_res = [(res_list_60[0], res_list_60[1])]
sg_80_res = [(res_list_80[0], res_list_80[1])]
sg_res_blue = [(res_list_20[0], res_list_20[1]), (res_list_40[0], res_list_40[1])
    , (res_list_60[0], res_list_60[1]), (res_list_80[0], res_list_80[1])]

####  sept 17th  modification for  ini file
T1_Ymin = int(config['SITE_GLASS']['T1_Ymin'])
T1_Ymax = int(config['SITE_GLASS']['T1_Ymax'])
T2_Ymin = int(config['SITE_GLASS']['T2_Ymin'])
T2_Ymax = int(config['SITE_GLASS']['T2_Ymax'])

T1_Xmin = int(config['SITE_GLASS']['T1_Xmin'])
T1_Xmax = int(config['SITE_GLASS']['T1_Xmax'])
T2_Xmin = int(config['SITE_GLASS']['T2_Xmin'])
T2_Xmax = int(config['SITE_GLASS']['T2_Xmax'])

T1_x_rel = int(config['SITE_GLASS']['T1_x_relative'])
T1_y_rel = int(config['SITE_GLASS']['T1_y_relative'])
T1_w_rel = int(config['SITE_GLASS']['T1_w_relative'])
T1_h_rel = int(config['SITE_GLASS']['T1_h_relative'])
T2_x_rel = int(config['SITE_GLASS']['T2_x_relative'])
T2_y_rel = int(config['SITE_GLASS']['T2_y_relative'])
T2_w_rel = int(config['SITE_GLASS']['T2_w_relative'])
T2_h_rel = int(config['SITE_GLASS']['T2_h_relative'])

Min_Y_20 = int(config['SITE_GLASS']['Min_Y_20'])
Min_Y_40 = int(config['SITE_GLASS']['Min_Y_40'])
Min_Y_60 = int(config['SITE_GLASS']['Min_Y_60'])
Min_Y_80 = int(config['SITE_GLASS']['Min_Y_80'])
Max_Y_20 = int(config['SITE_GLASS']['Max_Y_20'])
Max_Y_40 = int(config['SITE_GLASS']['Max_Y_40'])
Max_Y_60 = int(config['SITE_GLASS']['Max_Y_60'])
Max_Y_80 = int(config['SITE_GLASS']['Max_Y_80'])

else_threshold_level = int(config['SITE_GLASS']['threshold_lower_lvl'])

# Y axis calc
Total_Height = int(config['Y_AXIS_LEVEL_CALC']['Total_Height'])
Flow_above_80 = int(config['Y_AXIS_LEVEL_CALC']['Flow_above_80'])
Flow_above_60 = int(config['Y_AXIS_LEVEL_CALC']['Flow_above_60'])
Flow_above_40 = int(config['Y_AXIS_LEVEL_CALC']['Flow_above_40'])
Flow_above_20 = int(config['Y_AXIS_LEVEL_CALC']['Flow_above_20'])
above_80_divider = float(config['Y_AXIS_LEVEL_CALC']['above_80_divider'])
above_60_divider = float(config['Y_AXIS_LEVEL_CALC']['above_60_divider'])
above_40_divider = float(config['Y_AXIS_LEVEL_CALC']['above_40_divider'])
above_20_divider = float(config['Y_AXIS_LEVEL_CALC']['above_20_divider'])
else_divider = float(config['Y_AXIS_LEVEL_CALC']['else_divider'])

# SIGHT GLASS IDENTIFIER
T1_sg_name = str(config['SG_LEVEL_IDENTIFIER']['T1_sg_name'])
T1_inner_iden_x = int(config['SG_LEVEL_IDENTIFIER']['T1_inner_iden_x'])
T1_inner_iden_y = int(config['SG_LEVEL_IDENTIFIER']['T1_inner_iden_y'])
T1_inner_iden_w = int(config['SG_LEVEL_IDENTIFIER']['T1_inner_iden_w'])
T1_inner_iden_h = int(config['SG_LEVEL_IDENTIFIER']['T1_inner_iden_h'])
T1_min_sand_w = int(config['SG_LEVEL_IDENTIFIER']['T1_min_sand_w'])
T1_min_sand_h = int(config['SG_LEVEL_IDENTIFIER']['T1_min_sand_h'])
T1_min_rgb_avg = int(config['SG_LEVEL_IDENTIFIER']['T1_min_rgb_avg'])
T1_min_approx_shape = int(config['SG_LEVEL_IDENTIFIER']['T1_min_approx_shape'])
T1_min_moca_to_sand_ratio = int(config['SG_LEVEL_IDENTIFIER']['T1_min_moca_to_sand_ratio'])
T1_min_moca_elem = int(config['SG_LEVEL_IDENTIFIER']['T1_min_moca_elem'])

T2_sg_name = str(config['SG_LEVEL_IDENTIFIER']['T2_sg_name'])
T2_inner_iden_x = int(config['SG_LEVEL_IDENTIFIER']['T2_inner_iden_x'])
T2_inner_iden_y = int(config['SG_LEVEL_IDENTIFIER']['T2_inner_iden_y'])
T2_inner_iden_w = int(config['SG_LEVEL_IDENTIFIER']['T2_inner_iden_w'])
T2_inner_iden_h = int(config['SG_LEVEL_IDENTIFIER']['T2_inner_iden_h'])
T2_min_sand_w = int(config['SG_LEVEL_IDENTIFIER']['T2_min_sand_w'])
T2_min_sand_h = int(config['SG_LEVEL_IDENTIFIER']['T2_min_sand_h'])
T2_min_rgb_avg = int(config['SG_LEVEL_IDENTIFIER']['T2_min_rgb_avg'])
T2_min_approx_shape = int(config['SG_LEVEL_IDENTIFIER']['T2_min_approx_shape'])
T2_min_moca_to_sand_ratio = int(config['SG_LEVEL_IDENTIFIER']['T2_min_moca_to_sand_ratio'])
T2_min_moca_elem = int(config['SG_LEVEL_IDENTIFIER']['T2_min_moca_elem'])

T3_sg_name = str(config['SG_LEVEL_IDENTIFIER']['T3_sg_name'])
T3_inner_iden_x = int(config['SG_LEVEL_IDENTIFIER']['T3_inner_iden_x'])
T3_inner_iden_y = int(config['SG_LEVEL_IDENTIFIER']['T3_inner_iden_y'])
T3_inner_iden_w = int(config['SG_LEVEL_IDENTIFIER']['T3_inner_iden_w'])
T3_inner_iden_h = int(config['SG_LEVEL_IDENTIFIER']['T3_inner_iden_h'])
T3_min_sand_w = int(config['SG_LEVEL_IDENTIFIER']['T3_min_sand_w'])
T3_min_sand_h = int(config['SG_LEVEL_IDENTIFIER']['T3_min_sand_h'])
T3_min_rgb_avg = int(config['SG_LEVEL_IDENTIFIER']['T3_min_rgb_avg'])
T3_min_approx_shape = int(config['SG_LEVEL_IDENTIFIER']['T3_min_approx_shape'])
T3_min_moca_to_sand_ratio = int(config['SG_LEVEL_IDENTIFIER']['T3_min_moca_to_sand_ratio'])
T3_min_moca_elem = int(config['SG_LEVEL_IDENTIFIER']['T3_min_moca_elem'])

T4_sg_name = str(config['SG_LEVEL_IDENTIFIER']['T4_sg_name'])
T4_inner_iden_x = int(config['SG_LEVEL_IDENTIFIER']['T4_inner_iden_x'])
T4_inner_iden_y = int(config['SG_LEVEL_IDENTIFIER']['T4_inner_iden_y'])
T4_inner_iden_w = int(config['SG_LEVEL_IDENTIFIER']['T4_inner_iden_w'])
T4_inner_iden_h = int(config['SG_LEVEL_IDENTIFIER']['T4_inner_iden_h'])
T4_min_sand_w = int(config['SG_LEVEL_IDENTIFIER']['T4_min_sand_w'])
T4_min_sand_h = int(config['SG_LEVEL_IDENTIFIER']['T4_min_sand_h'])
T4_min_rgb_avg = int(config['SG_LEVEL_IDENTIFIER']['T4_min_rgb_avg'])
T4_min_approx_shape = int(config['SG_LEVEL_IDENTIFIER']['T4_min_approx_shape'])
T4_min_moca_to_sand_ratio = int(config['SG_LEVEL_IDENTIFIER']['T4_min_moca_to_sand_ratio'])
T4_min_moca_elem = int(config['SG_LEVEL_IDENTIFIER']['T4_min_moca_elem'])

SG_20_Constant = int(config['SG_LEVEL_IDENTIFIER']['SG_20_Constant'])
SG_40_Constant = int(config['SG_LEVEL_IDENTIFIER']['SG_40_Constant'])
SG_60_Constant = int(config['SG_LEVEL_IDENTIFIER']['SG_60_Constant'])
SG_80_Constant = int(config['SG_LEVEL_IDENTIFIER']['SG_80_Constant'])
Min_20_to_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_20_to_fill'])
Min_40_to_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_40_to_fill'])
Min_60_to_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_60_to_fill'])
Min_80_to_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_80_to_fill'])
Max_20_to_fill = int(config['SG_LEVEL_IDENTIFIER']['Max_20_to_fill'])
Max_40_to_fill = int(config['SG_LEVEL_IDENTIFIER']['Max_40_to_fill'])
Max_60_to_fill = int(config['SG_LEVEL_IDENTIFIER']['Max_60_to_fill'])
Max_80_to_fill = int(config['SG_LEVEL_IDENTIFIER']['Max_80_to_fill'])
Min_20_Suggest_to_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_20_Suggest_to_fill'])
Min_40_Suggest_to_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_40_Suggest_to_fill'])
Min_60_Suggest_to_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_60_Suggest_to_fill'])
Min_40_for_others_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_40_for_others_fill'])
Min_60_for_others_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_60_for_others_fill'])
Min_80_for_others_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_80_for_others_fill'])

# FLow level  indicator
Above_80_Multiplier = float(config['FLOW_LEVEL_IND']['Above_80_Multiplier'])
Above_60_Multiplier = float(config['FLOW_LEVEL_IND']['Above_60_Multiplier'])
Above_40_Multiplier = float(config['FLOW_LEVEL_IND']['Above_40_Multiplier'])
Above_20_Multiplier = float(config['FLOW_LEVEL_IND']['Above_20_Multiplier'])
Above_80_Adder = int(config['FLOW_LEVEL_IND']['Above_80_Adder'])
Above_60_Adder = int(config['FLOW_LEVEL_IND']['Above_60_Adder'])
Above_40_Adder = int(config['FLOW_LEVEL_IND']['Above_40_Adder'])
Above_20_Adder = int(config['FLOW_LEVEL_IND']['Above_20_Adder'])
else_multiplier = float(config['FLOW_LEVEL_IND']['else_multiplier'])

df_tube_mvmt = pd.DataFrame()  # columns=['curr_datetime', 'tube_refr', 'tube_mvmt_delta'])
prev_df_tube_mvmt = pd.DataFrame()


# data = pd.DataFrame({'curr_datetime':datetime.now(),' tube_refr':0, 'tube_mvmt_delta':0},
#                                    index=[0])
# df_tube_mvmt = df_tube_mvmt.append(data, ignore_index=True)


def findTubeCoordinates(img):
    mask = np.zeros((frame.shape[0], frame.shape[1], 3), dtype='uint8')

    for (x, y, w, h) in Blue_Tube_Initiater:
        points = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]])
        cv2.fillPoly(mask, [points], (255, 255, 255))
    masked = cv2.bitwise_and(img, mask)
    masked_img = cv2.resize(masked, (360, 640))
    # cv2.imshow(" framesq ", masked_img)

    return masked


def findSiteGlasses(img, lower_hsv_fltr, upper_hsv_fltr):
    # Set minimum and max HSV values to display
    # lower = np.array([32, 13, 90])
    # upper = np.array([153, 105, 255])
    Blue_list = []  # stores  the  coordinates  of the   4  tubes
    # print(type(lower_hsv_fltr))
    # Create HSV Image and threshold into a range.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_hsv_fltr, upper_hsv_fltr)
    kernel = np.ones((3, 3), np.uint8)

    # output = cv2.dilate(output, kernel, iterations=5)
    output = cv2.bitwise_and(img, img, mask=mask)

    # output = cv2.bitwise_and(output, output, mask=mask)

    imgray_tmp = cv2.cvtColor(output, cv2.COLOR_HSV2BGR)
    imgray = cv2.cvtColor(imgray_tmp, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(imgray, (33, 33), 0)  # 3,3 for tubes # Changed from 3,3 on Oct 17th, 2022
    ret, thresh = cv2.threshold(blur, 20, 255, 0)  # 20 for tubes

    new_contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  #
    # cv2.drawContours(img, new_contours, -1, (255, 255, 0), 3)

    for contour in new_contours:
        (x, y, w, h) = cv2.boundingRect(contour)

        if 35000 < cv2.contourArea(contour) < 100000000:
            if 400 < h < 700 and 150 < w < 215:
                if (T1_Ymin < y < T1_Ymax):
                    Blue_list.append((x, y, w, h))  # append  the  original  60th  tube  coordinates
                    # finding 20th tube
                    twenty_x = x + T1_x_rel
                    twenty_y = y + T1_y_rel
                    twenty_w = w - T1_w_rel
                    twenty_h = h - T1_h_rel
                    Tube_20 = (twenty_x, twenty_y, twenty_w, twenty_h)  # appending the relative 20th  tube  coordinate
                    Blue_list.append(Tube_20)
                if (T2_Ymin < y < T2_Ymax):
                    Blue_list.append((x, y, w, h))  # append  the  original  40th  tube  coordinates
                    # finding 80th tube
                    eighty_x = x + T2_x_rel
                    eighty_y = y - T2_y_rel
                    eighty_w = w - T2_w_rel
                    eighty_h = h + T2_h_rel
                    Tube_80 = (eighty_x, eighty_y, eighty_w, eighty_h)
                    Blue_list.append(Tube_80)

                cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(output, str(cv2.contourArea(contour)), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255),
                            2)
    # output = cv2.resize(output, (360, 640))
    # cv2.imshow("frame_1 ", output)
    print("  ***********************************  BLUE  LIST **************", Blue_list)
    return Blue_list


def region_of_interest(frame, tube_coordinates):
    mask = np.zeros((frame.shape[0], frame.shape[1], 3), dtype='uint8')

    for (x, y, w, h) in tube_coordinates:

        if 300 < h < 700 and 150 < w < 240:  # reduce the  unwanted  rectangles using the height and width of the tube
            points = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]])
            cv2.fillPoly(mask, [points], (255, 255, 255))
    masked = cv2.bitwise_and(frame, mask)

    return masked


# below function used  to ensure the  total number of tubes in the  process(4 tubes  must)
def Find_All_SiteGlasses(maskable_img):
    total_tube_list = []
    # Set minimum and max HSV values to display
    lower = np.array([0, 0, 0])
    upper = np.array([255, 255, 255])

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    kernel = np.ones((3, 3), np.uint8)
    # output = cv2.dilate(output, kernel, iterations=5)
    output = cv2.bitwise_and(maskable_img, maskable_img, mask=mask)
    # output = cv2.bitwise_and(output, output, mask=mask)

    imgray_tmp = cv2.cvtColor(output, cv2.COLOR_HSV2BGR)
    imgray = cv2.cvtColor(imgray_tmp, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(imgray, (3, 3), 0)  # 3,3 for tubes
    ret, thresh = cv2.threshold(blur, 20, 255, 0)  # 20 for tubes

    new_contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  #
    # cv2.drawContours(img, new_contours, -1, (255, 255, 0), 3)

    Mask_list.clear()
    total_tubes = 0

    for contour in new_contours:
        (x, y, w, h) = cv2.boundingRect(contour)

        if 30000 < cv2.contourArea(contour) < 100000000:
            total_tube_list.append((x, y, w, h))
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(output, str(cv2.contourArea(contour)), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 255, 255), 2)
            total_tubes = len(total_tube_list)
            Mask_list.append(x)

            if total_tubes == 4:
                Blue_Tube_Initiater.clear()
                Blue_Tube_Initiater.extend(total_tube_list)  # clear  the  list  and  append  the  4 tube
                print(" there is  coordinate  updated", Blue_Tube_Initiater)

    output = cv2.resize(output, (360, 640))
    # cv2.imshow("frame_siteglasses ", output)

    return new_contours, total_tubes


def Flow_Level_Calculation(mask_image, tube_name, feed_quality):
    tubes = 0
    level_list = []
    level = 0
    threshold_lower_lvl = 0
    Sand_Lvl_lw_hsv = []
    Sand_Lvl_up_hsv = []

    if tube_name == 'T60':
        if feed_quality == 'good':
            threshold_lower_lvl = SG60_Good_Feed_Threshold  # threshold for bad feed is 100
        else:
            threshold_lower_lvl = SG60_Bad_Feed_Threshold
    elif tube_name == 'T20':
        threshold_lower_lvl = SG20_Feed_Threshold  # 60
    elif tube_name == 'T40':
        threshold_lower_lvl = SG40_Feed_Threshold  # 40 changed from 70
    elif tube_name == 'T80':
        threshold_lower_lvl = SG80_Feed_Threshold  # 40 changed from 70
    else:
        threshold_lower_lvl = else_threshold_level

    if tube_name == 'T20':
        Sand_Lvl_lw_hsv = Sand_Lvl_20_lower_hsv
        Sand_Lvl_up_hsv = Sand_Lvl_20_upper_hsv
    elif tube_name == 'T40':
        Sand_Lvl_lw_hsv = Sand_Lvl_40_lower_hsv
        Sand_Lvl_up_hsv = Sand_Lvl_40_upper_hsv
    else:
        Sand_Lvl_lw_hsv = Sand_Lvl_lower_hsv
        Sand_Lvl_up_hsv = Sand_Lvl_upper_hsv

    hsv = cv2.cvtColor(mask_image, cv2.COLOR_BGR2HSV)
    Sand_Lvl_Mask = cv2.inRange(hsv, Sand_Lvl_lw_hsv, Sand_Lvl_up_hsv)
    output = cv2.bitwise_and(mask_image, mask_image, mask=Sand_Lvl_Mask)
    imgray_tmp = cv2.cvtColor(output, cv2.COLOR_HSV2BGR)
    imgray = cv2.cvtColor(imgray_tmp, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(imgray, (33, 33), 0)  # 3,3 for tubes

    ret, thresh = cv2.threshold(blur, threshold_lower_lvl, 255, 0)

    new_contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return new_contours, hierarchy


def calc_Lvl_Algo_Yaxis(Y_Lvl):
    Algo_Yaxis_Lvl = 0

    if Y_Lvl != 9999:
        Lvl_Value = Total_Height - Y_Lvl

        if Lvl_Value >= Flow_above_80:
            Algo_Yaxis_Lvl = 80 + (Lvl_Value - Flow_above_80) / above_80_divider
        elif Lvl_Value >= Flow_above_60:
            Algo_Yaxis_Lvl = 60 + (Lvl_Value - Flow_above_60) / above_60_divider
        elif Lvl_Value >= Flow_above_40:
            Algo_Yaxis_Lvl = 40 + (Lvl_Value - Flow_above_40) / above_40_divider
        elif Lvl_Value >= Flow_above_20:
            Algo_Yaxis_Lvl = 20 + (Lvl_Value - Flow_above_20) / above_20_divider
        else:
            Algo_Yaxis_Lvl = Lvl_Value / else_divider
    else:
        Algo_Yaxis_Lvl = 0

    return round(Algo_Yaxis_Lvl, 2)


# this lists  store the  constant and actual height of the sand  region
sand_20 = []
sand_40 = []
sand_60 = []
sand_80 = []
sand_level = []

Vibration_arr = []

smooth_sand_level = []
temp_series_list = []
sand_y_lvl_list = []
sand_y_lvl_dict = {}

Actual_Yax_Level = []


# sand_20.append(0)
# sand_40.append(0)
# sand_60.append(0)
# sand_80.append(0)

def Find_Video_Vibrations(frame1, frame2):
    vib_count = 0
    if frame1 != [] and frame2 != []:
        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blur, 10, 255,
                                  cv2.THRESH_BINARY)  # if  we put  5  then    it produce  much more  contours
        dilated = cv2.dilate(thresh, None, iterations=5)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        print("number of contours=" + str(len(contours)))  # counting the   length of  the  total  contours

        frame3 = frame2.copy()
        cv2.drawContours(frame3, contours, -1, (0, 255, 0), 3)
        frame3_res = cv2.resize(frame3, (360, 640))
        # cv2.imshow('feed', frame3_res)
        vib_count = len(contours)
    else:
        vib_count = 0

    return vib_count, contours, frame3_res


def calc_var(X):
    S = 0.0
    SS = 0.0
    for x in X:
        S += x
        SS += x * x
    xbar = S / float(len(X))
    return (SS - len(X) * xbar * xbar) / (len(X) - 1.0)


def calc_cov(X, Y):
    n = len(X)
    xbar = sum(X) / n
    ybar = sum(Y) / n
    return sum([(x - xbar) * (y - ybar) for x, y in zip(X, Y)]) / (n - 1)


def calc_beta(y):
    slope = 0
    if len(y) > 20:
        if len(y) > 50:
            y = y[-50:]
        x = range(1, len(y) + 1)
        slope = calc_cov(x, y) / calc_var(x)
    return slope


def reject_outliers(data, m):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    ret_data = (data[s < m])

    return ret_data  # data[s < m]


def Find_Exp_Avg(numpy_list):
    src_numpy_arr = np.array(numpy_list)
    clean_numpy_list = np.array(reject_outliers(src_numpy_arr, 60))
    # clean_numpy_list.append(reject_outliers(numpy_list, 12))

    df = pd.Series(
        clean_numpy_list)  # pd.series is capable of holding  one diemensional  array(convert list into  series )
    # df['avg_data '] = df.mean()  # calculating the  average  (SMA)  of  the  data
    df['EMA_0.1'] = df.ewm(alpha=0.1).mean()
    lvl_np = df['EMA_0.1'].to_numpy(dtype=object)
    Level_Ewma = round(lvl_np[-1], 2)
    return Level_Ewma


def Find_Sand_Color(masked_sand_roi):
    roi = masked_sand_roi
    channels = cv2.mean(roi)
    rgb_feature = np.array([(channels[2], channels[1], channels[0])])
    mean_color = int((channels[2] + channels[1] + channels[0]) / 3)
    print('avg colors: ' + str(channels))
    return mean_color


def Find_Motion_capture(frame1, frame2):
    try:
        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blur, 10, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=5)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        return contours

    except Exception as e:
        print(e)


def Find_Motion_Ratio(masked_img, sand_x, sand_y, sand_w, sand_h, sand_region_area, prev_frame, feed_quality):
    sand_roi = masked_img[sand_y: sand_y + sand_h, sand_x: sand_x + sand_w]
    rgb_avg = Find_Sand_Color(sand_roi)  # function  returns  the   rgb  value
    sand_roi_prev = prev_frame[sand_y: sand_y + sand_h, sand_x: sand_x + sand_w]
    Motion_Contours = Find_Motion_capture(sand_roi, sand_roi_prev)  # function returns  the (moca_region_area)
    moca_region_area = 0
    min_sand_region_area = sand_region_area * 1

    for moca_contour in Motion_Contours:
        (x, y, w, h) = cv2.boundingRect(moca_contour)
        if (w * h) < min_sand_region_area:
            moca_region_area = moca_region_area + (w * h)
        cv2.rectangle(sand_roi, (x, y), (x + w, y + h), (255, 255, 0), 2)

    return moca_region_area, Motion_Contours, rgb_avg


def Residue_Filter(tmp_all_sand_lvl, sg_res_array, sand_y_level):
    tmp_final_sand_lvl_arr = []
    sand_y_level_tmp = sand_y_level  # default value if the below logic dfails
    if len(tmp_all_sand_lvl) > 1:
        for res in sg_res_array:
            res_low, res_high = res
            for yax in tmp_all_sand_lvl:
                print(calc_Lvl_Algo_Yaxis(yax))
                act_ylvl = calc_Lvl_Algo_Yaxis(yax)
                if act_ylvl < res_low or act_ylvl > res_high:
                    tmp_final_sand_lvl_arr.append(yax)

        tmp_final_sand_lvl_arr.sort()
        print(tmp_final_sand_lvl_arr)
        # tmp_final_sand_lvl = tmp_all_sand_lvl[0]

        if len(tmp_final_sand_lvl_arr) > 0:
            sand_y_level_tmp = tmp_final_sand_lvl_arr[0]

    print(calc_Lvl_Algo_Yaxis(sand_y_level_tmp))
    return sand_y_level_tmp


def Parse_Residue_Filter(sand_y):
    count_res_idn = 0
    ret_sand_y = 0
    yax_sand_y = calc_Lvl_Algo_Yaxis(sand_y)

    for res in sg_res_array:
        res_low, res_high = res
        if res_low < yax_sand_y < res_high:
            count_res_idn = count_res_idn + 1

    if count_res_idn > 0:
        ret_sand_y = 0
    else:
        ret_sand_y = sand_y

    return ret_sand_y


def Config_Refresh():
    ConfigFile = 'cvision_config.ini'
    config = ConfigParser()
    config.read(ConfigFile)
    global res_list_20
    global res_list_40
    global res_list_60
    global res_list_80
    global sg_20_res
    global sg_40_res
    global sg_60_res
    global sg_80_res
    global sg_res_blue
    global Mask_Glass_20
    global Mask_Glass_80
    global Sand_Lvl_40_upper_hsv
    global Sand_Lvl_40_lower_hsv
    global Sand_Lvl_20_lower_hsv
    global Sand_Lvl_20_upper_hsv
    global T1_min_rgb_avg
    global T2_min_rgb_avg
    global T3_min_rgb_avg
    global T4_min_rgb_avg
    global Min_20_Suggest_to_fill
    global Min_40_Suggest_to_fill
    global Min_60_Suggest_to_fill
    global Min_40_for_others_fill
    global Min_60_for_others_fill
    global Min_80_for_others_fill

    Min_20_Suggest_to_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_20_Suggest_to_fill'])
    Min_40_Suggest_to_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_40_Suggest_to_fill'])
    Min_60_Suggest_to_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_60_Suggest_to_fill'])
    Min_40_for_others_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_40_for_others_fill'])
    Min_60_for_others_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_60_for_others_fill'])
    Min_80_for_others_fill = int(config['SG_LEVEL_IDENTIFIER']['Min_80_for_others_fill'])

    res_list_20 = np.fromstring(config['RESIDUE']['res_20_A1'][1:-1], sep=',').astype(int)
    res_list_40 = np.fromstring(config['RESIDUE']['res_40_A1'][1:-1], sep=',').astype(int)
    res_list_60 = np.fromstring(config['RESIDUE']['res_60_A1'][1:-1], sep=',').astype(int)
    res_list_80 = np.fromstring(config['RESIDUE']['res_80_A1'][1:-1], sep=',').astype(int)

    sg_40_res = [(res_list_40[0], res_list_40[1])]
    sg_60_res = [(res_list_60[0], res_list_60[1])]
    sg_80_res = [(res_list_80[0], res_list_80[1])]
    sg_res_blue = [(res_list_20[0], res_list_20[1]), (res_list_40[0], res_list_40[1])
        , (res_list_60[0], res_list_60[1]), (res_list_80[0], res_list_80[1])]
    Mask_Glass_20 = config['RESIDUE']['Mask_Glass_20']
    Mask_Glass_80 = config['RESIDUE']['Mask_Glass_80']

    Sand_Lvl_40_upper_hsv = np.fromstring(config['SAND_IDENT_FILTER']['Sand_lvl_40_upper_hsv'][1:-1]
                                          , sep=',').astype(int)
    Sand_Lvl_40_lower_hsv = np.fromstring(config['SAND_IDENT_FILTER']['Sand_lvl_40_lower_hsv'][1:-1]
                                          , sep=',').astype(int)

    Sand_Lvl_20_lower_hsv = np.fromstring(config['SAND_IDENT_FILTER']['Sand_lvl_20_lower_hsv'][1:-1]
                                          , sep=',').astype(int)
    Sand_Lvl_20_upper_hsv = np.fromstring(config['SAND_IDENT_FILTER']['Sand_lvl_20_upper_hsv'][1:-1]
                                          , sep=',').astype(int)
    T1_min_rgb_avg = int(config['SG_LEVEL_IDENTIFIER']['T1_min_rgb_avg'])
    T2_min_rgb_avg = int(config['SG_LEVEL_IDENTIFIER']['T2_min_rgb_avg'])
    T3_min_rgb_avg = int(config['SG_LEVEL_IDENTIFIER']['T3_min_rgb_avg'])
    T4_min_rgb_avg = int(config['SG_LEVEL_IDENTIFIER']['T4_min_rgb_avg'])


# Stores the  actual  flow level of the sand
def Calculate_Levels_in_SG(sg_name, Masked_Site_Glasses, sg_contour,
                           inner_iden_x, inner_iden_y, inner_iden_w, inner_iden_h, min_sand_w, min_sand_h, min_rgb_avg,
                           min_approx_shape, min_moca_to_sand_ratio, min_moca_elem, feed_quality):
    # inner_rects_count = 1  # increment the  inner  rects  as  1 point
    mask = np.zeros((frame.shape[0], frame.shape[1], 3), dtype='uint8')
    (tube_x, tube_y, tube_w, tube_h) = cv2.boundingRect(sg_contour)
    points_list = []

    # ensure_inner_rects.append(inner_rects_count)

    x = tube_x + inner_iden_x
    y = tube_y + inner_iden_y
    w = inner_iden_w
    h = tube_h - inner_iden_h

    cv2.putText(Masked_Site_Glasses, sg_name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)

    points = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
    points_list.append(points)
    cv2.rectangle(Masked_Site_Glasses, (x, y), (x + w, y + h), (255, 255, 255), 3,
                  cv2.FONT_HERSHEY_SIMPLEX)
    points_list_np = np.array(points_list)
    for point in points_list_np:
        cv2.fillPoly(mask, [point], (255, 255, 255))

    masked_sg = cv2.bitwise_and(frame, mask)

    #  apply the  hsv sand function for the masked image
    sand_region, sand_hierarchy = Flow_Level_Calculation(masked_sg, sg_name, feed_quality)
    # sort applied above to pick up only the last and biggest sand block observed in the sand contour list
    sorted_sand_region = sorted(sand_region,
                                key=lambda obj_contour_sand: cv2.contourArea(obj_contour_sand))

    sand_y_lvl_dict = 9999  # ['y_20']
    total_sand_h = 0
    Moca_Kpi_sg = ''
    tmp_all_sand_lvl = []

    for contour_sand in sorted_sand_region:
        (sand_x, sand_y, sand_w, sand_h) = cv2.boundingRect(contour_sand)

        sand_region_area = (sand_w) * (sand_h)

        print('Contour Area: ' + str(cv2.contourArea(contour_sand)))
        if 500 < cv2.contourArea(contour_sand) < 100000000:

            Motion_Region_area, Moca_Contours_tube_sg, rgb_avg_sg = Find_Motion_Ratio \
                (masked_sg, sand_x, sand_y, sand_w, sand_h, sand_region_area, prev_frame, feed_quality)

            moca_to_sand_ratio = round((Motion_Region_area / sand_region_area) * 100)
            count_moca_elem = len(Moca_Contours_tube_sg)

            if Motion_Capture_Active == 'N':
                moca_to_sand_ratio = 50  # Arbitary value that overides identified motion

            cv2.rectangle(frame, (sand_x, sand_y), (sand_x + sand_w, sand_y + sand_h), (0, 255, 0), 2,
                          cv2.FONT_HERSHEY_SIMPLEX)

            approx_shape = cv2.approxPolyDP(contour_sand, 0.01 * cv2.arcLength(sg_contour, True), True)

            cv2.putText(frame, str(cv2.contourArea(contour_sand)) + ' shp:' + str(
                len(approx_shape)) + 'w:' + str(sand_w) + ' c:' + str(
                rgb_avg_sg) + ' h:' + str(sand_h),
                        (sand_x - 200, sand_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame,
                        'N.Moca: ' + str(len(Moca_Contours_tube_sg)) + ' MocaR:' + str(moca_to_sand_ratio),
                        (sand_x - 200, sand_y - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
                        )
            print("sand_w and min_sand_w", sand_w, min_sand_w)
            print("rgb_avg_sg and min_rgb_avg_sg", rgb_avg_sg, min_rgb_avg)
            print("len(approx) and min approx", len(approx_shape), min_approx_shape)
            print("moca to sand and min moca to sand", moca_to_sand_ratio, min_moca_to_sand_ratio)
            print("count_moca and min_moca count", count_moca_elem,min_moca_elem)
            print("sand_h and min_sand_h", sand_h, min_sand_h)
            if sand_w >= min_sand_w and rgb_avg_sg >= min_rgb_avg and len(approx_shape) >= min_approx_shape \
                    and moca_to_sand_ratio < min_moca_to_sand_ratio and count_moca_elem <= min_moca_elem \
                    and sand_h >= min_sand_h:  # Pratheep 02/Nov/2020 Only if sand width > 35 select it for processing

                Moca_Kpi_sg = Moca_Kpi_sg + sg_name + ' : [ points-' + str((count_moca_elem)) + ' ratio-' + str(
                    moca_to_sand_ratio) + ' ]\n'
                print(" sand_y value", sand_y)
                print("sand_y_lvl_dict", sand_y_lvl_dict)
                if sand_y < sand_y_lvl_dict:
                    sand_y_lvl_dict = sand_y
                    print("Inside if condition", sand_y_lvl_dict)

                tmp_all_sand_lvl.append(sand_y)

                cv2.drawContours(frame, contour_sand, -1, (255, 255, 0), 3)
                # Db_Value_Log = Db_Value_Log + str('hgt_sand_20: ' + str(sand_h) + ';')

                # if Parse_Residue_Filter(sand_y) > 0:
                total_sand_h = total_sand_h + sand_h
    #
    # if sg_name == 'T20':
    #     sand_y_lvl_dict = Residue_Filter(tmp_all_sand_lvl, sg_20_res, sand_y_lvl_dict)  # recent sand Y level  passed
    # elif sg_name == 'T40':
    #     sand_y_lvl_dict = Residue_Filter(tmp_all_sand_lvl, sg_40_res, sand_y_lvl_dict)
    # elif sg_name == 'T60':
    #     sand_y_lvl_dict = Residue_Filter(tmp_all_sand_lvl, sg_60_res, sand_y_lvl_dict)
    # elif sg_name == 'T80':
    #     sand_y_lvl_dict = Residue_Filter(tmp_all_sand_lvl, sg_80_res, sand_y_lvl_dict)
    #
    return total_sand_h, sand_y_lvl_dict, Moca_Kpi_sg


##############################################################
Yax_Algo_Lvl_Before_Filt = []
Yax_Algo_Lvl_After_Filt = []


##############################################################

def Clean_Site_Glass_Identifier(Masked_Site_Glasses, No_of_Tubes_Identified, Site_Glass_Contours, curr_frame,
                                prev_frame, Video_Vibrating, Yax_Trend, feed_quality, prev_Lvl_In_Tube, df_tube_mvmt):
    # below  mask  values   used for  each tubes
    mask_20 = np.zeros((frame.shape[0], frame.shape[1], 3), dtype='uint8')
    mask_40 = np.zeros((frame.shape[0], frame.shape[1], 3), dtype='uint8')
    mask_60 = np.zeros((frame.shape[0], frame.shape[1], 3), dtype='uint8')
    mask_80 = np.zeros((frame.shape[0], frame.shape[1], 3), dtype='uint8')

    #  below lists used to store the  inner rectangles  coordinates  for  each  tubes
    points_list_40 = []
    points_list_60 = []
    points_list_80 = []

    ensure_inner_rects = []  # this list ensures  whether the  inner  rectangles  are   4  or  not

    ret_flow_level = 0

    sand_20_relative_40 = []
    sand_40_relative_60 = []
    sand_60_relative_80 = []
    prev_sand_ewma = 0
    prev_Yax_ewma = 0

    Moca_Kpi = ''

    total_sand_20_h = total_sand_40_h = total_sand_60_h = total_sand_80_h = 0
    sand_20_h = 0
    sand_40_h = 0
    sand_60_h = 0
    sand_80_h = 0

    sand_y_lvl_dict['y_20'] = 9999
    sand_y_lvl_dict['y_40'] = 9999
    sand_y_lvl_dict['y_60'] = 9999
    sand_y_lvl_dict['y_80'] = 9999

    Lvl_In_Tube = ''

    if No_of_Tubes_Identified == 4:
        Db_Value_Log = ' '

        if len(sand_level) > 40:
            prev_sand_ewma = Find_Exp_Avg(sand_level)

        if len(Yax_Algo_Lvl) > 40:
            prev_Yax_ewma = Find_Exp_Avg(Yax_Algo_Lvl)

        for contour in Site_Glass_Contours:
            (tube_x, tube_y, tube_w, tube_h) = cv2.boundingRect(contour)

            if 35000 < cv2.contourArea(contour) < 100000000:

                #      TUBE 20 LEVEL  CALCULATION
                if Min_Y_20 < tube_y < Max_Y_20:  # 475
                    print(" this is 20th tube ")
                    inner_rects_count = 1  # increment the  inner  rects  as  1 point
                    ensure_inner_rects.append(inner_rects_count)
                    total_sand_20_h, sand_y_lvl_dict['y_20'], tmp_moca_kpi = Calculate_Levels_in_SG(sg_name='T20',
                                                                                                    Masked_Site_Glasses=Masked_Site_Glasses,
                                                                                                    sg_contour=contour,
                                                                                                    inner_iden_x=T1_inner_iden_x,
                                                                                                    inner_iden_y=T1_inner_iden_y,
                                                                                                    inner_iden_w=T1_inner_iden_w,
                                                                                                    inner_iden_h=T1_inner_iden_h,
                                                                                                    min_sand_w=T1_min_sand_w,
                                                                                                    min_sand_h=T1_min_sand_h,
                                                                                                    min_rgb_avg=T1_min_rgb_avg,
                                                                                                    min_approx_shape=T1_min_approx_shape,
                                                                                                    min_moca_to_sand_ratio=T1_min_moca_to_sand_ratio,
                                                                                                    min_moca_elem=T1_min_moca_elem,
                                                                                                    feed_quality=feed_quality
                                                                                                    )
                    Moca_Kpi = Moca_Kpi + tmp_moca_kpi
                    #     TUBE 40 LEVEL CALCULATION
                elif Min_Y_40 < tube_y < Max_Y_40:
                    print(" this is 40th tube  ")
                    inner_rects_count = 1  # increment the  inner  rects  as  1 point
                    ensure_inner_rects.append(inner_rects_count)

                    total_sand_40_h, sand_y_lvl_dict['y_40'], tmp_moca_kpi = Calculate_Levels_in_SG(sg_name='T40',
                                                                                                    Masked_Site_Glasses=Masked_Site_Glasses,
                                                                                                    sg_contour=contour,
                                                                                                    inner_iden_x=T2_inner_iden_x,
                                                                                                    inner_iden_y=T2_inner_iden_y,
                                                                                                    inner_iden_w=T2_inner_iden_w,
                                                                                                    inner_iden_h=T2_inner_iden_h,
                                                                                                    min_sand_w=T2_min_sand_w,
                                                                                                    min_sand_h=T2_min_sand_h,
                                                                                                    min_rgb_avg=T2_min_rgb_avg,
                                                                                                    min_approx_shape=T2_min_approx_shape,
                                                                                                    min_moca_to_sand_ratio=T2_min_moca_to_sand_ratio,
                                                                                                    min_moca_elem=T2_min_moca_elem,
                                                                                                    feed_quality=feed_quality
                                                                                                    )
                    Moca_Kpi = Moca_Kpi + tmp_moca_kpi
                #  TUBE 60 LEVEL CALCULATION
                elif Min_Y_60 < tube_y < Max_Y_60:
                    print(" this is 60th tube")
                    inner_rects_count = 1  # increment the  inner  rects  as  1 point
                    ensure_inner_rects.append(inner_rects_count)
                    x = tube_x + 60
                    y = tube_y + 55
                    w = 66
                    h = tube_h - 110

                    total_sand_60_h, sand_y_lvl_dict['y_60'], tmp_moca_kpi = Calculate_Levels_in_SG(sg_name='T60',
                                                                                                    Masked_Site_Glasses=Masked_Site_Glasses,
                                                                                                    sg_contour=contour,
                                                                                                    inner_iden_x=T3_inner_iden_x,
                                                                                                    inner_iden_y=T3_inner_iden_y,
                                                                                                    inner_iden_w=T3_inner_iden_w,
                                                                                                    inner_iden_h=T3_inner_iden_h,
                                                                                                    min_sand_w=T3_min_sand_w,
                                                                                                    min_sand_h=T3_min_sand_h,
                                                                                                    min_rgb_avg=T3_min_rgb_avg,
                                                                                                    min_approx_shape=T3_min_approx_shape,
                                                                                                    min_moca_to_sand_ratio=T3_min_moca_to_sand_ratio,
                                                                                                    min_moca_elem=T3_min_moca_elem,
                                                                                                    feed_quality=feed_quality
                                                                                                    )
                    Moca_Kpi = Moca_Kpi + tmp_moca_kpi


                # TUBE 80 LEVEL CALCULATION
                elif Min_Y_80 < tube_y < Max_Y_80:
                    print(" this is 80th tube  ")
                    inner_rects_count = 1  # increment the  inner  rects  as  1 point
                    ensure_inner_rects.append(inner_rects_count)
                    x = tube_x + 60
                    y = int(tube_y + 60)
                    w = 66
                    h = tube_h - 115

                    total_sand_80_h, sand_y_lvl_dict['y_80'], tmp_moca_kpi = Calculate_Levels_in_SG(sg_name='T80',
                                                                                                    Masked_Site_Glasses=Masked_Site_Glasses,
                                                                                                    sg_contour=contour,
                                                                                                    inner_iden_x=T4_inner_iden_x,
                                                                                                    inner_iden_y=T4_inner_iden_y,
                                                                                                    inner_iden_w=T4_inner_iden_w,
                                                                                                    inner_iden_h=T4_inner_iden_h,
                                                                                                    min_sand_w=T4_min_sand_w,
                                                                                                    min_sand_h=T4_min_sand_h,
                                                                                                    min_rgb_avg=T4_min_rgb_avg,
                                                                                                    min_approx_shape=T4_min_approx_shape,
                                                                                                    min_moca_to_sand_ratio=T4_min_moca_to_sand_ratio,
                                                                                                    min_moca_elem=T4_min_moca_elem,
                                                                                                    feed_quality=feed_quality
                                                                                                    )
                    print("Total Sand Height ", total_sand_80_h)
                    print("Dict level ", sand_y_lvl_dict['y_80'])
                    print("Tmp moca kpi", tmp_moca_kpi)
                    Moca_Kpi = Moca_Kpi + tmp_moca_kpi

        ####################  FLOW LEVEL  CALCULATION #################################
        Db_Algo_Level = ' '
        prev_sand_level = 0
        pctng_diff = 0
        flow_level_calc = 0

        tmp_Algo_Yaxis_Lvl = 0
        prev_yax_lvl = 0
        Yaxis_Lvl_Ind = 0

        Yaxis_Lvl_20 = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_20'])
        Yaxis_Lvl_40 = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_40'])
        Yaxis_Lvl_60 = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_60'])
        Yaxis_Lvl_80 = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_80'])

        print('Yaxis Lvls are: ')
        print('Yax 20: ' + str(Yaxis_Lvl_20) + ' Yax 40: ' + str(Yaxis_Lvl_40) + ' Yax 60: ' + str(
            Yaxis_Lvl_60) + ' Yax 80: ' + str(Yaxis_Lvl_80))
        print('Total_Sand_H Values :')
        print('Total_sand_20_h: ' + str(total_sand_20_h) + ' Total_sand_40_h: ' + str(total_sand_40_h) +
              ' Total_sand_60_h: ' + str(total_sand_60_h) + ' Total_sand_80_h: ' + str(total_sand_80_h))

        # SG-20 calculations
        if Mask_Glass_20 == 'Y':
            sand_20_h = 420
            sand_y_lvl_dict['y_20'] = 1370
        else:
            if Min_20_to_fill <= total_sand_20_h < Max_20_to_fill:
                sand_20_h = 420
            elif 0 < total_sand_20_h < Min_20_to_fill:
                sand_20_h = total_sand_20_h
            else:
                sand_20_h = 0

        # If SG-20 is masked, consider that its full


        # SG-40 calculation
        if Mask_Glass_40 == 'Y':
            sand_40_h = 440
            sand_y_lvl_dict['y_40'] = 915
        else:
            if total_sand_20_h > Min_20_Suggest_to_fill:
                if Min_40_to_fill <= total_sand_40_h <= Max_40_to_fill:
                    sand_40_h = 440
                    sand_20_h = 420
                elif 99 <= total_sand_40_h <= Min_40_to_fill:
                    sand_40_h = total_sand_40_h
                    sand_20_h = 420
                elif 0 <= total_sand_40_h <= Min_40_for_others_fill:
                    sand_40_h = total_sand_40_h
                else:
                    sand_40_h = 0
            else:
                sand_40_h = 0


        # SG-60 calculations
        if Mask_Glass_60 == 'Y':
            sand_60_h = 450
            sand_y_lvl_dict['y_60'] = 516
        else:
            if total_sand_40_h > Min_40_Suggest_to_fill:
                if Min_60_to_fill <= total_sand_60_h < Max_60_to_fill:
                    sand_60_h = 450
                    sand_20_h = 420
                    sand_40_h = 440
                elif Min_60_for_others_fill <= total_sand_60_h < Min_60_to_fill:
                    sand_60_h = total_sand_60_h
                    sand_20_h = 420
                    sand_40_h = 440
                else:
                    sand_60_h = total_sand_60_h
            else:
                sand_60_h = 0

        # SG-80 calculations
        # If Mask_Glass_80 is set to Y, consider that the SG-80 is empty.
        if Mask_Glass_80 == 'Y':
            sand_80_h = 0
            sand_y_lvl_dict['y_80'] = 0
        else:
            if total_sand_60_h >= Min_60_Suggest_to_fill:
                if Min_80_to_fill <= total_sand_80_h <= Max_80_to_fill:
                    sand_80_h = 450
                    sand_20_h = 420
                    sand_40_h = 440
                    sand_60_h = 450
                elif Min_80_for_others_fill <= total_sand_80_h <= Min_80_to_fill:
                    sand_80_h = total_sand_80_h
                    sand_20_h = 420
                    sand_40_h = 440
                    sand_60_h = 450
                elif 0 < total_sand_80_h <= Min_80_for_others_fill:
                    sand_80_h = total_sand_80_h
            else:
                sand_80_h = 0

        if len(ensure_inner_rects) == 4:
            print("  4 tubes ")

            print('Sand Y Dict:' + str(sand_y_lvl_dict))

            if len(sand_level) > 2:
                prev_sand_level = round(sand_level[-1], 2)

            if len(Yax_Algo_Lvl) > 2:
                prev_yax_lvl = round(Yax_Algo_Lvl[-1], 2)
                tmp_Algo_Yaxis_Lvl = round(Yax_Algo_Lvl[-1], 2)

            if sand_20_h == 0 and sand_40_h == 0 and sand_60_h == 0 and sand_80_h == 0:
                Total_Height_level = 0  # 4 tubes  filled
                Flow_level = Total_Height_level / 1760  # where  1760  is  the  actual  height range of  all the  4 tubes (1980-160 = 1760)
                Flow_level = Flow_level * 100
                print(" flow level is (4 filled )", Flow_level)
                sand_level.append(Flow_level)
                Db_Algo_Level = '0_0_0_0'
                Lvl_In_Tube = 'EMPTY'

                ####  if 20 , 40 , 60 , 80  all the  tubes  filled ####
            elif sand_20_h >= 420 and sand_40_h >= 420 and sand_60_h >= 450 and sand_80_h >= 450:
                Total_Height_level = sand_20_h + sand_40_h + sand_60_h + sand_80_h  # 4 tubes  filled
                Flow_level = Total_Height_level / 1760
                Flow_level = Flow_level * 100
                print(" flow level is (4 filled )", Flow_level)
                sand_level.append(Flow_level)
                Db_Algo_Level = str(sand_20_h) + "_" + str(sand_40_h) + "_" + str(sand_60_h) + "_" + str(
                    sand_80_h)
                tmp_Algo_Yaxis_Lvl = 99
                Yaxis_Lvl_Ind = 100
                Lvl_In_Tube = 'FULL'

                ####  if 20 , 40 , 60    tubes  filled  and 80 not filled  ####
            elif sand_20_h >= 420 and sand_40_h >= 420 and sand_60_h >= 450 and sand_80_h < 470:
                Total_Height_level = sand_20_h + sand_40_h + sand_60_h + sand_80_h  # 3 tubes filled
                Flow_level = Total_Height_level / 1760
                Flow_level = Flow_level * 100
                print(" flow level is (3 filled )  ", Flow_level)
                sand_level.append(Flow_level)
                Db_Algo_Level = str(sand_20_h) + "_" + str(sand_40_h) + "_" + str(sand_60_h) + "_" + str(
                    sand_80_h)
                # tmp_Algo_Yaxis_Lvl = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_80'])

                # Error handling condition where 80 is identified and 60 is emptyy
                if 9999 > Yaxis_Lvl_60 > Min_60T_Val_For_80_Select:
                    if 9999 > sand_y_lvl_dict['y_80'] > 0:
                        Yaxis_Lvl_Ind = sand_y_lvl_dict['y_80']
                        tmp_Algo_Yaxis_Lvl = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_80'])
                        Lvl_In_Tube = 'S-80'
                    else:
                        Yaxis_Lvl_Ind = sand_y_lvl_dict['y_60']
                        tmp_Algo_Yaxis_Lvl = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_60'])
                        Lvl_In_Tube = 'S-60'

                elif 9999 > Yaxis_Lvl_60 > 0 and 9999 > Yaxis_Lvl_40 > Min_40T_Val_For_60_Select:
                    Yaxis_Lvl_Ind = Yaxis_Lvl_60
                    tmp_Algo_Yaxis_Lvl = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_60'])
                    Lvl_In_Tube = 'S-60'
                # else:
                #    Yaxis_Lvl_Ind = Yaxis_Lvl_40
                #    tmp_Algo_Yaxis_Lvl = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_40'])

                # tmp_Algo_Yaxis_Lvl = Yaxis_Lvl_Ind

                ####  if 20 , 40   tubes  filled  and 60,  80 are  not filled  ####
            elif sand_20_h == 420 and sand_40_h >= 420 and sand_60_h < 450:
                Total_Height_level = sand_20_h + sand_40_h + sand_60_h  # 2 tubes filled
                Flow_level = Total_Height_level / 1760
                Flow_level = Flow_level * 100
                print(" flow level is (2 filled )", Flow_level)
                sand_level.append(Flow_level)
                Db_Algo_Level = str(sand_20_h) + "_" + str(sand_40_h) + "_" + str(sand_60_h) + "_" + str(0)
                #                tmp_Algo_Yaxis_Lvl = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_60'])
                #                Yaxis_Lvl_Ind = sand_y_lvl_dict['y_60']

                # Error handling condition where 40 is identified and 20 is empty
                if 9999 > Yaxis_Lvl_40 > Min_40T_Val_For_60_Select:
                    if 9999 > sand_y_lvl_dict['y_60'] > 0:
                        Yaxis_Lvl_Ind = sand_y_lvl_dict['y_60']
                        tmp_Algo_Yaxis_Lvl = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_60'])
                        Lvl_In_Tube = 'S-60'
                    else:
                        Yaxis_Lvl_Ind = sand_y_lvl_dict['y_40']
                        tmp_Algo_Yaxis_Lvl = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_40'])
                        Lvl_In_Tube = 'S-40'
                elif 9999 > Yaxis_Lvl_40 > 0 and 9999 > Yaxis_Lvl_20 > Min_20T_Val_For_40_Select:
                    Yaxis_Lvl_Ind = Yaxis_Lvl_40
                    tmp_Algo_Yaxis_Lvl = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_40'])
                    Lvl_In_Tube = 'S-40'
                # else:
                #    Yaxis_Lvl_Ind = Yaxis_Lvl_20
                #    tmp_Algo_Yaxis_Lvl = 0  # calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_20'])

                ####  if 20   tube  filled  and 40, 60, 80  are not filled  ####
            elif sand_20_h == 420 and sand_40_h < 430:
                Total_Height_level = sand_20_h + sand_40_h  # only 1 tube filled

                Db_Algo_Level = str(sand_20_h) + "_" + str(sand_40_h) + "_"  # + str(0) + "_" + str(0)
                # prev_flow_level = sand_level
                if 50 < sand_60_h < 120 and sand_40_h > 400:
                    Total_Height_level = Total_Height_level + (sand_60_h - 45)
                    Db_Algo_Level = Db_Algo_Level + str(sand_60_h - 45) + "_" + str(0)
                else:
                    Total_Height_level = Total_Height_level + (sand_40_h / 5)
                    Db_Algo_Level = Db_Algo_Level + str(0) + "_" + str(0)

                # tmp_Algo_Yaxis_Lvl = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_40'])
                # Yaxis_Lvl_Ind = sand_y_lvl_dict['y_40']

                Flow_level = Total_Height_level / 1760
                Flow_level = Flow_level * 100
                print(" flow level is (1 filled ) ", Flow_level)
                sand_level.append(Flow_level)

                # Error handling condition where 40 is identified and 20 is empty
                if 9999 > Yaxis_Lvl_20 > Min_20T_Val_For_40_Select and 9999 > Yaxis_Lvl_20 > 0:
                    if 9999 > sand_y_lvl_dict['y_40'] > 0:
                        Yaxis_Lvl_Ind = sand_y_lvl_dict['y_40']
                        tmp_Algo_Yaxis_Lvl = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_40'])
                        Lvl_In_Tube = 'S-40'
                    else:
                        Yaxis_Lvl_Ind = sand_y_lvl_dict['y_20']
                        tmp_Algo_Yaxis_Lvl = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_20'])
                        Lvl_In_Tube = 'S-20'
                elif 9999 > Yaxis_Lvl_20 > 0:
                    Yaxis_Lvl_Ind = Yaxis_Lvl_20
                    tmp_Algo_Yaxis_Lvl = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_20'])
                    Lvl_In_Tube = 'S-20'
                # else:
                #    Yaxis_Lvl_Ind = Yaxis_Lvl_20
                #    tmp_Algo_Yaxis_Lvl = 0 # calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_40'])

                #####  if  there no tube  fulled  with  sand #####
            elif sand_20_h < 320:
                Total_Height_level = sand_20_h  # only 1 tube filled
                Flow_level = Total_Height_level / 1760
                Flow_level = (Flow_level * 100) + 6  # Pratheep added 4 to account for the residue in tube-20
                print(" flow level is( no one filled) ", Flow_level)
                sand_level.append(Flow_level)
                Db_Algo_Level = str(sand_20_h) + "_" + str(0) + "_" + str(0) + "_" + str(0)
                tmp_Algo_Yaxis_Lvl = calc_Lvl_Algo_Yaxis(sand_y_lvl_dict['y_20'])
                Yaxis_Lvl_Ind = sand_y_lvl_dict['y_20']
                Lvl_In_Tube = 'S-20'
            else:
                Flow_level = sand_level[-1]
                print(" tube is  filled  with bitumen", Flow_level)
                sand_level.append(Flow_level)
                Db_Algo_Level = 'prev_level'
                Lvl_In_Tube = 'PREV'

            curr_sand_20 = level_calc(sand_20)
            curr_sand_40 = level_calc(sand_40)
            curr_sand_60 = level_calc(sand_60)
            curr_sand_80 = level_calc(sand_80)
            curr_flow_level = level_calc(sand_level)

            # Tower movement
            tube_mvmt = 0
            err_msg = ''
            if 'Lvl_In_Tube' in locals():
                curr_tube = tube_level_dict[Lvl_In_Tube]
                err_msg = 'prev_tube:' + prev_Lvl_In_Tube + '  curr_tube:' + Lvl_In_Tube

            # In a pandas array, accumalate the tube movements. If there are more than 15 siteglass switches in last one minute,
            # then hold the current ewma level until level stabilizes.
            if curr_flow_level == 0:
                tube_mvmt = 0

                data = pd.DataFrame({'curr_datetime': datetime.now(), ' tube_refr': 0, 'tube_mvmt_delta': 0},
                                    index=[0])
                df_tube_mvmt = df_tube_mvmt.append(data, ignore_index=True)
            else:
                prev_tube = tube_level_dict[prev_Lvl_In_Tube]
                tube_mvmt = abs(prev_tube - curr_tube)

                data = pd.DataFrame(
                    {'curr_datetime': datetime.now(), ' tube_refr': curr_tube, 'tube_mvmt_delta': tube_mvmt},
                    index=[0])
                df_tube_mvmt = df_tube_mvmt.append(data, ignore_index=True)

            df_tmp = df_tube_mvmt[df_tube_mvmt['curr_datetime'] > pd.Timestamp('now') - pd.Timedelta(1, 'minutes')]
            accum_tube_mvmt = sum(df_tmp['tube_mvmt_delta'])
            print(df_tmp)
            print(accum_tube_mvmt)

            if len(Yax_Algo_Lvl) > 2:
                print('*** YAX ***')
                print('prev_yax_lvl is:' + str(prev_yax_lvl))
                print('curr yax lvl is:' + str(tmp_Algo_Yaxis_Lvl))

                ##########################################################################
                Yax_Algo_Lvl_Before_Filt.append(tmp_Algo_Yaxis_Lvl)
                ##########################################################################

                if ((abs(tmp_Algo_Yaxis_Lvl - prev_yax_lvl) < PermitDeviation) or prev_yax_lvl == 0) \
                        and (tmp_Algo_Yaxis_Lvl > 0) and tube_mvmt < 2 \
                        and accum_tube_mvmt < 15:
                    #    (tmp_Algo_Yaxis_Lvl > 75 and prev_yax_lvl > 75) or \
                    Yax_Algo_Lvl.append(tmp_Algo_Yaxis_Lvl)
                    print('yax inside IF')
                else:
                    Yax_Algo_Lvl.append(prev_yax_lvl)
                    tmp_Algo_Yaxis_Lvl = prev_yax_lvl
                    print('yax inside ELSE')
                print('*** END YAX ***')
            else:
                Yax_Algo_Lvl.append(tmp_Algo_Yaxis_Lvl)

            if prev_sand_level > 0:
                pctng_diff = round(((abs(curr_flow_level - prev_sand_level) / prev_sand_level)) * 100, 2)
                Db_Value_Log = Db_Value_Log + ' pcntg_diff:' + str(pctng_diff) + ';'
                Db_Value_Log = Db_Value_Log + ' prev_lvl:' + str(prev_sand_level) + ";"
                Db_Value_Log = Db_Value_Log + ' act_lvl:' + str(round(curr_flow_level, 2))
                Db_Value_Log = Db_Value_Log + ' Lvl_Algo_YAxxis: ' + str(round(tmp_Algo_Yaxis_Lvl, 2))

            if (
                    prev_sand_ewma + PermitDeviation < curr_flow_level or curr_flow_level < prev_sand_ewma - PermitDeviation) \
                    and prev_sand_ewma > 0 and curr_flow_level > 0:
                sand_level[-1] = prev_sand_level
                curr_flow_level = prev_sand_level

            if ((prev_Yax_ewma + PermitDeviation < Yax_Algo_Lvl[-1] or Yax_Algo_Lvl[
                -1] < prev_Yax_ewma - PermitDeviation) and prev_Yax_ewma > 0 and
                    Yax_Algo_Lvl[-1] > 0):
                #    and ((tmp_Algo_Yaxis_Lvl + prev_yax_lvl) / 2 < 13):
                Yax_Algo_Lvl[-1] = prev_yax_lvl
                tmp_Algo_Yaxis_Lvl = prev_yax_lvl
                print('***Inside RETAIN PREVIOUS LEVEL****')

            ################################################################
            Yax_Algo_Lvl_After_Filt.append(tmp_Algo_Yaxis_Lvl)
            if len(Yax_Algo_Lvl_After_Filt) > 45:
                Yax_Algo_Lvl_After_Filt.clear()
            if len(Yax_Algo_Lvl_Before_Filt) > 45:
                Yax_Algo_Lvl_Before_Filt.clear()
            if len(Yax_Algo_Lvl_After_Filt) > List_Size and \
                    len(set(Yax_Algo_Lvl_After_Filt)) == 1 and \
                    Yax_Algo_Lvl_After_Filt[-1] == prev_yax_lvl:
                tmp_Algo_Yaxis_Lvl = Yax_Algo_Lvl_Before_Filt[-1]
                Yax_Algo_Lvl.append(tmp_Algo_Yaxis_Lvl)
                ################################################################

            curr_Sand_Level_Ewma = 0
            curr_Yax_Algo_Lvl_Ewma = 0

            Actual_Yax_Level.append(tmp_Algo_Yaxis_Lvl)

            if len(sand_level) > 40:
                curr_Sand_Level_Ewma = Find_Exp_Avg(sand_level)

            if len(Yax_Algo_Lvl) > 40:
                curr_Yax_Algo_Lvl_Ewma = Find_Exp_Avg(Yax_Algo_Lvl)

            if len(Actual_Yax_Level) > 40:
                curr_Actual_Yax_Level = Find_Exp_Avg(Actual_Yax_Level)
            else:
                curr_Actual_Yax_Level = 9999

            print(' Flow Levels are: ' + 'S_20: ' + str(curr_sand_20) + ' S_40: ' + str(curr_sand_40)
                  + ' S_60: ' + str(curr_sand_60) + ' S_80: ' + str(curr_sand_80))
            print('Sand Level: {0}'.format(str(round(sand_level[-1], 2))))

            try:
                db_msg = AccessSql.addFlowLevel(CvDb,
                                                f_curr_frame_no,
                                                round(curr_sand_20, 2),
                                                round(curr_sand_40, 2),
                                                round(curr_sand_60, 2),
                                                round(curr_sand_80, 2),
                                                round(curr_flow_level, 2),
                                                '',
                                                '',
                                                Db_Value_Log,
                                                Db_Algo_Level,
                                                tmp_Algo_Yaxis_Lvl,
                                                round(Video_Vibrating, 2),
                                                round(curr_Sand_Level_Ewma, 2),
                                                curr_Yax_Algo_Lvl_Ewma,
                                                Video_Name,
                                                Video_Vibrating,
                                                Moca_Kpi
                                                )

                print(db_msg)


            except Exception as e:
                print(e)

        print("  inner  rects  ensuring ", ensure_inner_rects)  # ensure inner  glass tubes  are  4  or not

        sand = cv2.resize(Masked_Site_Glasses, (360, 640))

        ret_flow_level = curr_flow_level
    else:
        ret_flow_level = 0
        tmp_Algo_Yaxis_Lvl = 0

    # Yax Algo Levels are captured below in the list

    try:
        print('Sand Level is:')
        print(sand_level)
        # cv2.putText(frame, 'Flow = ' + str(sand_level[-1]), (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 0), 3)
    except Exception as e:
        print('Exception event is:' + str(e))

    return ret_flow_level, flow_level_calc, tmp_Algo_Yaxis_Lvl, curr_Sand_Level_Ewma, curr_Yax_Algo_Lvl_Ewma, Lvl_In_Tube, curr_Actual_Yax_Level, tube_mvmt, df_tube_mvmt


def Motion_within_SG(Blue_Tube_Initiater, contours_motion, Lvl_In_Tube):
    border_adj_x = -25
    border_adj_y = -25
    new_frame = frame.copy()
    tube = []
    select_mowit_contours = []
    tube_area = 0
    contour_area = 0
    moca_contour_lvl_value = 0
    contour_coverage = 0

    if Lvl_In_Tube == 'S-20':
        tube = Blue_Tube_Initiater[0]
    elif Lvl_In_Tube == 'S-40':
        tube = Blue_Tube_Initiater[1]
    elif Lvl_In_Tube == 'S-60':
        tube = Blue_Tube_Initiater[2]
    elif Lvl_In_Tube == 'S-80':
        tube = Blue_Tube_Initiater[3]
    else:
        tube = []

    if tube:
        tube_area = (tube[2] - 100) * (tube[3] - 100)
        # cv2.drawContours(new_frame, contours_motion, -1, (255,255,255), 3)
        for contour in contours_motion:
            if cv2.contourArea(contour) > 200:
                (x, y, w, h) = cv2.boundingRect(contour)
                (moca_x, moca_y, moca_w, moca_h) = (x, y, w, h)
                # for tube in Blue_Tube_Initiater:
                (x, y, w, h) = (tube[0], tube[1], tube[2], tube[3])
                if (x - border_adj_x < moca_x < (x + w + border_adj_x) > (moca_x + moca_w)) and (
                        y - border_adj_y < moca_y < (y + h + border_adj_y) > (
                        moca_y + moca_h)):  # and ((moca_x + moca_w) < (x + w)) and ((moca_y + moca_h) < (y + h)) :
                    cv2.rectangle(new_frame, (moca_x + 2, moca_y + 2), (moca_x + moca_w - 2, moca_y + moca_h - 2),
                                  (255, 255, 255), 3)
                    select_mowit_contours.append(contour)
                # cv2.putText(frame, 'MoCo: ' + str(cv2.contourArea(contour)), (moca_x, moca_y),
                #            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    if select_mowit_contours:
        select_mowit_contours_sorted = sorted(select_mowit_contours,
                                              key=lambda obj_contour: cv2.contourArea(obj_contour))

        sel_arr_elem = len(select_mowit_contours_sorted) - 1
        print(sel_arr_elem)

        (c_x, c_y, c_w, c_h) = cv2.boundingRect(select_mowit_contours_sorted[sel_arr_elem])
        moca_contour_lvl_value = calc_Lvl_Algo_Yaxis(round(c_y + (c_h / 2)))
        contour_area = c_w * c_h

        contour_coverage = round((contour_area / tube_area) * 100)

    new_f_frame = cv2.resize(new_frame, (360, 640))
    # cv2.imshow('only_moca', new_f_frame)
    return new_f_frame, moca_contour_lvl_value, contour_coverage


def level_calc(sand_array):
    if len(sand_array) > 0:
        ret_value = sand_array[-1]
    else:
        ret_value = 0
    return ret_value


def defineRtspFeed(RtspVideoFeedName):
    player = vlc.MediaPlayer(RtspVideoFeedName)
    return player


def defineMkvFeed(camera_path):
    cap = cv2.VideoCapture(camera_path)
    frame_total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    return cap


def Flow_Level_Indicator(flow_level):
    Y_lvl = 0

    if flow_level > 80:
        Y_lvl = (Above_80_Multiplier * flow_level) + Above_80_Adder
    elif 60 <= flow_level <= 80:
        Y_lvl = (Above_60_Multiplier * flow_level) + Above_60_Adder
    elif 40 <= flow_level <= 60:
        Y_lvl = (Above_40_Multiplier * flow_level) + Above_40_Adder
    elif 20 <= flow_level <= 40:
        Y_lvl = (Above_20_Multiplier * flow_level) + Above_20_Adder
    else:
        Y_lvl = else_multiplier * flow_level

    Y_Line_Lvl = Total_Height - int(Y_lvl)

    # cv2.line(frame, (0, Y_Line_Lvl), (1080, Y_Line_Lvl), (0, 0, 255), 7,
    #         cv2.FONT_HERSHEY_SIMPLEX)

    return Y_Line_Lvl


def Write_To_OPC_Tbl(ConnObj, Write_Process_Name, OPC_Server_Name, OPC_Address, Write_Value):
    db_msg = ''
    try:
        db_msg = AccessSql.WriteToOPCTbl(ConnObj=ConnObj,
                                         Write_Process_name=Write_Process_Name,
                                         OPC_Server_name=OPC_Server_Name,
                                         OPC_Address=OPC_Address,
                                         OPC_Write_Value=Write_Value)

        print(db_msg)

    except Exception as e:
        print(e)

    return db_msg


def Apply_Black_Mask(frame, X_mask_list):
    for res in sg_res_blue:
        width_var = 120
        res_low, res_high = res
        if res_low and res_high != 0:  # empty array  stores the (0 , 0 ) value
            height = res_high - res_low
            height_axis = int(height * 17)  # use 16.7 ,  if 17  wont  work  properly
            x_axis = 0
            if 1 <= res_low and res_high <= 28:
                x_axis = X_mask_list[0] + 30
            if 25 <= res_low and res_high <= 52:
                x_axis = X_mask_list[2] + 30
            if 50 <= res_low and res_high <= 76:
                x_axis = X_mask_list[1] + 30
            if 72 <= res_low and res_high <= 100:
                x_axis = X_mask_list[3] + 30
            q = Flow_Level_Indicator(res_high)
            cv2.rectangle(frame, (x_axis, q), (int(x_axis + width_var), int(q + height_axis)),
                          (0, 0, 0), -1)
    return frame


if __name__ == '__main__':

    if execEvnr == 'prod':
        cap = defineRtspFeed(RtspVideoFeedName)
        Video_Name = RtspVideoFeedName
        cap.play()
    else:
        cap = defineMkvFeed(VideoFeedName)
        Video_Name = VideoFeedName.rsplit("/", 1)[1]

    # cap = cv2.VideoCapture(VideoFeedName)
    frame_count = 0  # increment  for the every 'n '  frames
    #    frame_total = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    local_No_of_Tubes_Identified = 0
    local_Site_Glass_Contours = []
    total_seconds = ((now.tm_min) * 60) + now.tm_sec

    # if Write_To_OPC == 'Y':
    # OPC_Conn_Obj, ret_value = AccessOPC.ConnectOPC(OPC_Server_Name)
    # if ret_value == 0:
    #    Write_To_OPC = 'N'

    Yax_Lvl_Display = 0
    old_image = []
    curr_frame = []
    prev_frame = []
    disp_frame = []

    prev_Lvl_In_Tube = 'INIT'
    Mask_list = []

    while True:  # cap.isOpened():
        try:
            # Diff environment settings
            if execEvnr == 'prod':
                time.sleep(1)
                cap.video_take_snapshot(0, 'feed_snapshot.png', 0, 0)
                frame = cv2.imread('feed_snapshot.png', cv2.IMREAD_UNCHANGED)
                now = time.localtime(time.time())
                total_seconds = (((now.tm_min) * 60) + now.tm_sec) % 3600
                f_curr_frame_no = total_seconds * 30  # Assuming thirty frames per second

                # if total_seconds % 86303 == 0: # Data purging in cvmetrics.db
                ret_Purge = AccessSql.PurgeHistData(CvDb, str(Purge_No_Of_Days))

                ret = True
            else:
                ret, frame = cap.read()
                # cv2.imwrite("feed_snapshot.png", frame) # 07112020

                # rot_frame = cv2.resize(rotated, (720, 1280))
                # cv2.imshow('rot_frame', rot_frame)

                # ret_Purge = AccessSql.PurgeHistData(CvDb, str(Purge_No_Of_Days))

                if StartFrameNo > 0:  # to control moving to a specific frame for debugging
                    cap.set(cv2.CAP_PROP_POS_FRAMES, StartFrameNo)
                    frame_total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    StartFrameNo = -99
                    prev_frame = frame.copy()

                f_curr_frame_no = cap.get(cv2.CAP_PROP_POS_FRAMES)

            # f_curr_frame_no = cap.get(cv2.CAP_PROP_POS_FRAMES)
            # ret, frame = cap.read()

            if ret:
                frame = imutils.rotate(frame, AngelOfRotation)
                curr_frame = frame.copy()
                disp_frame = frame.copy()
                cv2.putText(frame, 'F: ' + str(f_curr_frame_no) + ' / ' + str(frame_total), (10, 1900),
                            cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 3)

                if f_curr_frame_no % 60 == 0:
                    print(" current  frame is", f_curr_frame_no)
                    (H, W) = frame.shape[:2]
                    Initial_coordinates_Mask = findTubeCoordinates(frame)

                    # Clean up lists
                    if len(sand_20) > 25:
                        sand_20_tmp = sand_20[-25:]
                        sand_20.clear()
                        sand_20 = sand_20_tmp
                    if len(sand_40) > 25:
                        sand_40_tmp = sand_40[-25:]
                        sand_40.clear()
                        sand_40 = sand_40_tmp
                    if len(sand_60) > 25:
                        sand_60_tmp = sand_60[-25:]
                        sand_60.clear()
                        sand_60 = sand_60_tmp
                    if len(sand_80) > 25:
                        sand_80_tmp = sand_80[-25:]
                        sand_80.clear()
                        sand_80 = sand_80_tmp
                    if len(sand_level) > 200:
                        sand_level_tmp = sand_level[-200:]
                        sand_level.clear()
                        sand_level = sand_level_tmp
                    if len(Yax_Algo_Lvl) > 200:
                        Yax_Algo_Lvl_tmp = Yax_Algo_Lvl[-200:]
                        Yax_Algo_Lvl.clear()
                        Yax_Algo_Lvl = Yax_Algo_Lvl_tmp
                    if len(Actual_Yax_Level) > 50:
                        Actual_Yax_Level_tmp = Actual_Yax_Level[-50:]
                        Actual_Yax_Level.clear()
                        Actual_Yax_Level = Actual_Yax_Level_tmp

                if f_curr_frame_no % 10000 == 0 or local_No_of_Tubes_Identified != 4:
                    Config_Refresh()
                    Site_Glass_60_80_Mask = findSiteGlasses(frame, Site_Glass_60_80_lower_hsv,
                                                            Site_Glass_60_80_upper_hsv)  # Blue tube list

                    Masked_Image_60_80 = region_of_interest(frame, Site_Glass_60_80_Mask)  # masked  return

                    local_Site_Glass_Contours, local_No_of_Tubes_Identified = Find_All_SiteGlasses(
                        Masked_Image_60_80)  # new_contours  returned
                    print(type(Site_Glass_Contours))

                Flow_Level_Value = 0
                flow_level_calc = 0
                tmp_Algo_Yaxis_Lvl = 0
                Sand_Level_Ewma = 0
                curr_Yax_Algo_Lvl_Ewma = 0
                Video_Vibrating = 0
                Yax_Trend_val = 0
                Yax_Trend = ''
                moca_only_frame = []
                moca_lvl_value = 0
                moca_coverage = 0
                feed_quality = ''

                tube_mvmt = ''

                if f_curr_frame_no % 30 == 0 and \
                        local_No_of_Tubes_Identified == 4 and prev_frame != []:

                    Video_Vibrating, contours_motion, frame_vibration = Find_Video_Vibrations(prev_frame, curr_frame)

                    Yax_Trend_slope = calc_beta(Yax_Algo_Lvl)
                    if Yax_Trend_slope > 0:
                        Yax_Trend = 'INC'
                    elif Yax_Trend_slope < 0:
                        Yax_Trend = 'DEC'
                    else:
                        Yax_Trend = 'NA'

                    feed_quality = feed_condition

                    frame = Apply_Black_Mask(frame,
                                             sorted(Mask_list))  # Applying the  black mask  before finding  flow level

                    df_tube_mvmt = prev_df_tube_mvmt

                    Flow_Level_Value, flow_level_calc, tmp_Algo_Yaxis_Lvl, Sand_Level_Ewma, curr_Yax_Algo_Lvl_Ewma, Lvl_In_Tube, curr_Actual_Yax_Level, tube_mvmt, df_tube_mvmt = Clean_Site_Glass_Identifier(
                        Initial_coordinates_Mask, local_No_of_Tubes_Identified,
                        local_Site_Glass_Contours, curr_frame, prev_frame, Video_Vibrating, Yax_Trend, feed_quality,
                        prev_Lvl_In_Tube, df_tube_mvmt)

                    prev_df_tube_mvmt = df_tube_mvmt

                    if ((
                                Lvl_In_Tube != 'PREV' and Lvl_In_Tube != 'EMPTY') and tube_mvmt < 2) or prev_Lvl_In_Tube == 'INIT':
                        prev_Lvl_In_Tube = Lvl_In_Tube

                    # Write to OPC
                    # Curr_Actual_Yax_level is 0 when there's a plant downtime.
                    if Write_To_OPC == 'Y' and (
                            curr_Yax_Algo_Lvl_Ewma > 0 or curr_Actual_Yax_Level == 0) and f_curr_frame_no % int(
                            OPC_Write_Freq_In_Frames) == 0:
                        # ret_value_OPC = AccessOPC.WriteToOPC(OPC_Conn_Obj, OPC_Write_Address, curr_Yax_Algo_Lvl_Ewma)
                        if Write_To_OPC_Exec == 'Y':
                            ret = subprocess.Popen(
                                ['opcexec.exe', OPC_Server_Name, OPC_Write_Address, str(curr_Yax_Algo_Lvl_Ewma)])
                        # if ret_value_OPC == 'Fail':
                        # print('OPC Write Failed')

                        ret_msg = Write_To_OPC_Tbl(ConnObj=CvDb,
                                                   Write_Process_Name='PSV-1',
                                                   OPC_Server_Name=OPC_Server_Name,
                                                   OPC_Address=OPC_Write_Address,
                                                   Write_Value=curr_Yax_Algo_Lvl_Ewma)

                        if ret_msg != 'success':
                            print('****** OPC write failed ******')

                if len(sand_level) == 0:
                    nothing()
                else:
                    cv2.putText(frame,
                                'Org:' + str(round(Flow_Level_Value, 2)) + ' / Vib:' + str(Video_Vibrating) + '/' + str(
                                    Yax_Trend) + '/' + Lvl_In_Tube,
                                (10, 55),
                                cv2.FONT_HERSHEY_SIMPLEX, 2,
                                (255, 255, 255), 3)
                    # cv2.putText(frame, 'Calc Flow = ' + str(round(flow_level_calc, 2)), (150, 110),
                    #            cv2.FONT_HERSHEY_SIMPLEX, 2,
                    #            (255, 255, 0), 3)
                    cv2.putText(frame, 'Yax:' + str(tmp_Algo_Yaxis_Lvl) + ' / Ewma:' + str(curr_Yax_Algo_Lvl_Ewma),
                                (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 2,
                                (255, 255, 255), 3)
                    # cv2.putText(frame, 'moca lvl:' + str(moca_lvl_value) + 'cvg: ' + str(moca_coverage),(10, 160), cv2.FONT_HERSHEY_SIMPLEX, 2,(255, 255, 255), 3)
                    # cv2.putText(frame, 'Ewma Flow = ' + str(Sand_Level_Ewma), (150, 220), cv2.FONT_HERSHEY_SIMPLEX, 2,
                    #            (255, 255, 0), 3) moca_lvl_value
                    if Mask_Glass_20 == 'Y':
                        cv2.arrowedLine(frame, (200, 1500), (270, 1500), (0, 0, 255), 30)
                    if Mask_Glass_80 == 'Y':
                        cv2.arrowedLine(frame, (1020, 250), (950, 250), (0, 0, 255), 30)
                    Y_Line_Lvl = Flow_Level_Indicator(int(curr_Yax_Algo_Lvl_Ewma))

                    cv2.line(frame, (0, Y_Line_Lvl), (1080, Y_Line_Lvl), (0, 0, 255), 7,
                             cv2.FONT_HERSHEY_SIMPLEX)

                for siteglass in Blue_Tube_Initiater:
                    masked_frame = cv2.rectangle(frame, (siteglass[0], siteglass[1]),
                                                 (siteglass[0] + siteglass[2], siteglass[1] + siteglass[3]),
                                                 (255, 255, 255), 3)

                # Draw the scale to the side
                # cv2.line(frame, (50, 215), (50, 1845), (255, 255, 255), 5)

                # cv2.line(frame, )

                # scale_init = 1760
                # scale_cntr = 1
                #
                # while scale_init > 215:
                #     cv2.arrowedLine(frame, (50, scale_init), (50 + 50, scale_init), (255, 255, 0), 3)
                #     scale_init = scale_init - 50
                #     cv2.putText(frame, str(scale_cntr * 50), (150, scale_init), cv2.FONT_HERSHEY_SIMPLEX, 1,
                #                 (255, 255, 0), 2)
                #     scale_cntr = scale_cntr + 1

                for res in sg_res_blue:
                    width_var = 70
                    res_low, res_high = res
                    if res_low and res_high != 0:  # empty array  stores the (0 , 0 ) value
                        height = res_high - res_low
                        height_axis = int(height * 17)  # use 16.7 ,  if 17  wont  work  properly
                        x_axis = 0
                        if 1 <= res_low and res_high <= 28:
                            x_axis = 395
                        if 25 <= res_low and res_high <= 52:
                            x_axis = 735
                        if 50 <= res_low and res_high <= 76:
                            x_axis = 395
                        if 72 <= res_low and res_high <= 100:
                            x_axis = 735
                        q = Flow_Level_Indicator(res_high)
                        # cv2.rectangle(frame, (x_axis, q), (int(x_axis + width_var), int(q + height_axis)),
                        #              (255, 0, 0), -1)

                masked_frame = cv2.resize(frame, (360, 640))
                # masked_frame = cv2.resize(frame, (1300, 1780))
                disp_frame_resize = cv2.resize(disp_frame, (360, 640))

                if Show_Video == 'Y':
                    cv2.imshow('CVLevelStream', masked_frame)
                    cv2.imshow('DispFrame', disp_frame_resize)

                    if f_curr_frame_no % 30 == 0:
                        cv2.imshow('CVCalcScreen', masked_frame)

                        # frame_resized = cv2.resize(moca_only_frame, (360, 640))
                        # con = np.concatenate((frame_vibration, masked_frame), axis=1)
                        # con_frame = np.concatenate((con, frame_resized), axis=1)
                        # cv2.imshow('CVCalcScreen', con_frame)

                    # Motion Capture Reference frame
                    if f_curr_frame_no % Motion_Capture_Refr_Frame == 0:
                        prev_frame = curr_frame.copy()

                # frame_count += 1
                # print(" blue  tube  initiator list", Blue_Tube_Initiater)
            else:
                print('problem with the frame')
                if execEvnr == 'prod':
                    continue
                else:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, f_curr_frame_no + 10)
                    if (f_curr_frame_no + 25) > frame_total:
                        break

            #  print('Frame pos:' + str(f_curr_frame_no))
            #  print('Frame pos ag:' + str(cap.get(cv2.CAP_PROP_POS_FRAMES)))

            # shutil.copyfile('feed_snapshot.png','old_feed_snapshot.png')

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as err:
            print(err)
            continue
    # print(H, W)
    cap.release()
    cv2.destroyAllWindows()
