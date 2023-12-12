import cv2
import numpy as np
import os
import os.path
import pandas as pd

'''
This code takes in images of outlet streams with material components that are blue, yellow, green, and orange and calculates the relative
fractions of each component present. Color ranges should be adjusted for the user's lighting and color choices. Images should be saved in 
the following format where a "scoop" represents an outlet stream. User should take multiple images of a scoop to get a more accurate estimate.
Code will export .xlsx file titled 'Trial_{trial_number}_ScoopAvgs.xlsx' which saves the average component fraction from each scoop.

Example of folder structure for saving images:

>Cyclone Trials
    >Trial 1
        >Scoop 1
            IMG1.jpg
            IMG2.jpg
            IMG3.jpg
        >Scoop 2
            IMG4.jpg
            IMG5.jpg
            IMG6.jpg
        ...

'''

## INPUTS

# input actual measured total weight for each scoop here in a list format
actual_total_weights = [x, x, x] # grams 

# input trial number
trial_number = 1

# input feed rate
feed_rate = 'Input'

# input air flow rate
air_rate = 'Input'

# input feed composition
feed_comp = 'Input'

# Define the main folder containing subfolders with images
trial_folder_path = f'C:/....../Cyclone Trials/Trial {trial_number}'

# set your color ranges and other parameters here
blue_lower = np.array([100, 0, 0], np.uint8)
blue_upper = np.array([130, 255, 255], np.uint8)

yellow_lower = np.array([24, 54, 0], np.uint8)
yellow_upper = np.array([30, 248, 255], np.uint8)

orange_lower = np.array([0, 126, 0], np.uint8)
orange_upper = np.array([23, 255, 255], np.uint8)

green_lower = np.array([35, 10, 0], np.uint8)
green_upper = np.array([90, 255, 255], np.uint8)


# input length of scale bar here
scalebar_length = 50.8 # mm

# FUNCTIONS
# function to find the average of a list of values
def Average(lst):
    return sum(lst) / len(lst)


####

df = pd.DataFrame(columns = ['Scoop #', 'PP Avg', 'PET Avg', 'HDPE Avg', 'Glass Avg', 'Scoop Weight'])

for scoop_folder_name in os.listdir(trial_folder_path):
    scoop_folder_path = os.path.join(trial_folder_path, scoop_folder_name)

    if os.path.isfile(scoop_folder_path) == True:
        continue

    # initiate counter for number of scoops
    scoop_number = int(scoop_folder_name[-1])
    print(scoop_number)

    image_counter = 0

    # INITIALIZATIONS
    # Initialize arrays for the estimated weights
    orange_pixel_weight = []
    blue_pixel_weight = []
    green_pixel_weight = []
    yellow_pixel_weight = []

    # Intialized arrays for the normalized estimated weights
    normalized_orange_pixel_weight = []
    normalized_blue_pixel_weight = []
    normalized_green_pixel_weight = []
    normalized_yellow_pixel_weight = []

    for file_name in os.listdir(scoop_folder_path):
        if file_name.endswith('.jpg'):
            file_path = os.path.join(scoop_folder_path, file_name)
            

            # import image
            img = cv2.imread(file_path)
            # convert image from BGR to HSV
            hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

            # create mask for each color
            blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
            yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
            orange_mask = cv2.inRange(hsv, orange_lower, orange_upper)
            green_mask = cv2.inRange(hsv, green_lower, green_upper)

            # count number of pixels of each color
            blue_pixels = cv2.countNonZero(blue_mask)
            yellow_pixels = cv2.countNonZero(yellow_mask)
            orange_pixels = cv2.countNonZero(orange_mask)
            green_pixels = cv2.countNonZero(green_mask)

            # sum up total number of pixels 
            total_pixels = blue_pixels + yellow_pixels + orange_pixels + green_pixels

            # __________________________________________________________________________
            # select two coordinates to scale pixels 
            # https://www.geeksforgeeks.org/displaying-the-coordinates-of-the-points-clicked-on-the-image-using-python-opencv/
        
            clicked_points = []
            annotated_image = img.copy()

            cv2.namedWindow(f'{file_name}', cv2.WINDOW_NORMAL)
            cv2.setWindowProperty(f'{file_name}',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
            # cv2.resizeWindow(f'{file_name}', 700, 900)
            cv2.imshow(f'{file_name}', img)

            def click_event(event,x,y,flags,params):
            
                if event == cv2.EVENT_LBUTTONDOWN: 
                    clicked_points.append((x,y))

                    cv2.circle(annotated_image, (x, y), 5, (191, 0, 255), -1)
                    if len(clicked_points) >=2:
                        cv2.destroyAllWindows()
        
            cv2.setMouseCallback(f'{file_name}', click_event)
            while len(clicked_points) < 2:
                cv2.imshow(f'{file_name}', annotated_image)
                cv2.waitKey(1)

            p1, p2 = clicked_points
            cv2.destroyAllWindows()

            # Calculate 'length' of a single pixel (pixel_length)
            vector_btwn_coordinates = np.array(p2) - np.array(p1) #vector between two selected points
            dist = np.linalg.norm(vector_btwn_coordinates)
            unit_vector = vector_btwn_coordinates / dist
            pixels_in_scale = dist  # renaming for easy remembering
       
            pixel_length = scalebar_length/pixels_in_scale

            # _____________________________________________________________________________
            # Calculate volume and weight of each pixel
            orange_height = 0.5 #mm
            orange_density = 0.9 #g/cm^3
            blue_height = 1.07 #mm
            blue_density = 2.7 #g/cm^3
            yellow_height = 0.85 #0.4 #mm
            yellow_density = 0.9 #g/cm^3
            green_height = 0.3 #mm
            green_density = 1.34 #g/cm^3

            orange_pixel_volume = orange_pixels * np.square(pixel_length) * orange_height/1000 #cm^3
            orange_pixel_weight.append(orange_pixel_volume * orange_density) 
            # print(f"Image {image_counter} Estimated orange Weight (g): {orange_pixel_weight[image_counter]}")

            blue_pixel_volume = blue_pixels * np.square(pixel_length) * blue_height/1000 #cm^3
            blue_pixel_weight.append(blue_pixel_volume * blue_density) 
            # print(f"Image {image_counter} Estimated Blue Weight (g): {blue_pixel_weight[image_counter]}")

            yellow_pixel_volume = yellow_pixels * np.square(pixel_length) * yellow_height/1000 #cm^3
            yellow_pixel_weight.append(yellow_pixel_volume * yellow_density) 
            # print(f"Image {image_counter} Estimated Yellow Weight (g): {yellow_pixel_weight[image_counter]}")

            green_pixel_volume = green_pixels * np.square(pixel_length) * green_height/1000 #cm^3
            green_pixel_weight.append(green_pixel_volume * green_density) 
            # print(f"Image {image_counter} Estimated Green Weight (g): {green_pixel_weight[image_counter]}")

            estimated_total_weight = orange_pixel_weight[image_counter] + yellow_pixel_weight[image_counter] + blue_pixel_weight[image_counter] + green_pixel_weight[image_counter]
        
            # print(f"Image {image_counter} PP wt%: {100*orange_pixel_weight/actual_total_weight}")
            # print(f"Image {image_counter} Glass wt%: {100*blue_pixel_weight/actual_total_weight}")
            # print(f"Image {image_counter} HDPE wt%: {100*yellow_pixel_weight/actual_total_weight}")
            # print(f"Image {image_counter} PET wt%: {100*green_pixel_weight/actual_total_weight}")

            scaling = estimated_total_weight/actual_total_weights[scoop_number-1]
            normalized_orange_pixel_weight.append(orange_pixel_weight[image_counter]/scaling)
            # print(f"Image {counter} Estimated Normalized Orange Weight (g): {normalized_orange_pixel_weight[counter]}")
            normalized_blue_pixel_weight.append(blue_pixel_weight[image_counter]/scaling)
            # print(f"Image {counter} Estimated Normalized Blue Weight (g): {normalized_blue_pixel_weight[counter]}")
            normalized_yellow_pixel_weight.append(yellow_pixel_weight[image_counter]/scaling)
            # print(f"Image {counter} Estimated Normalized Yellow Weight (g): {normalized_yellow_pixel_weight[counter]}")
            normalized_green_pixel_weight.append(green_pixel_weight[image_counter]/scaling)
            # print(f"Image {counter} Estimated Normalized Green Weight (g): {normalized_green_pixel_weight[counter]}")


            image_counter = image_counter + 1
    scoop_norm_average_orange_weight = round(Average(orange_pixel_weight),2)
    scoop_norm_average_yellow_weight = round(Average(normalized_yellow_pixel_weight),2)
    scoop_norm_average_green_weight = round(Average(normalized_green_pixel_weight),2)
    scoop_norm_average_blue_weight = round(Average(normalized_blue_pixel_weight),2)


    # save new row of data to excel workbook
    new_row = [scoop_number, scoop_norm_average_orange_weight, scoop_norm_average_green_weight, scoop_norm_average_yellow_weight, scoop_norm_average_blue_weight, actual_total_weights[scoop_number-1]]
    df.loc[len(df.index)] = new_row

## save dataframe to xlsx file

# specify condition folder name
condition_folder_name = f'{feed_rate}_{air_rate}_{feed_comp}'
export_folder_path = os.path.join('C:/.../Cyclone Trials/Scoop Averages', condition_folder_name)

# check if folder directory exists or not
isExist = os.path.exists(export_folder_path)
if not isExist:
    # Create a new directory because it does not exist
    os.makedirs(export_folder_path)

# specify export xlsx file name
xlsx_file_name = f'Trial_{trial_number}_ScoopAvgs.xlsx'
export_file_path = os.path.join(export_folder_path, xlsx_file_name)

# export dataframe to xlsx file
df.to_excel(export_file_path)



