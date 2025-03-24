import cv2
import pytesseract
from PIL import Image 
import requests
import time
import datetime

search_string_list = ["skip", "Sponsored", "Ad","skip in" ]
SLEEP_TIME = 5
CAM_INDEX=1 # this is my old iphone camera
IMAGE_NAME='picture.png'
#MUTE UNMUTE WEBHOOK
UN_MUTE_WEBHOOK = '<<FILL YOUR WEBHOOK URL>>' 
MUTE_FLAG = False
def list_cameras():
    """Lists available cameras and their indexes."""
    index = 0
    available_cameras = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            break
        else:
            available_cameras.append(index)
            get_camera_info(index)
            cap.release()
        index += 1
    return available_cameras

def get_camera_info(index):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        return None
    
    backend_name = cap.getBackendName()
    print(f"Backend name: {backend_name}")

  
    
def captureImage(imagePath) -> None:
    cam = cv2.VideoCapture(CAM_INDEX)

        # Check if the camera opened successfully
    if not cam.isOpened():
        raise IOError("Cannot open webcam")

    # Read a frame from the camera
    result, image = cam.read()

        # Check if the frame was read successfully
    if not result:
        #raise IOError("Cannot read frame from webcam")
        # if cam fails retry after time interval do not abort
        return

        # Save the image
    cv2.imwrite(imagePath, image)

        # Release the camera
    cam.release()
    cv2.destroyAllWindows()
    #print("Picture saved as, ", imagePath)


def getTextFromImage(imagePath: str) -> bool:
    # Open the image file
    img = cv2.imread(imagePath) 
    # Convert the image to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
   
    # Use pytesseract to get the text from the image
    #text = pytesseract.image_to_string(gray)

    #LOGICS to get the text from the image via different algos and settings Enhance for future
    # remove noise
    img = cv2.medianBlur(img, 5)
    text = pytesseract.image_to_string(img,config='--psm 7 -c tessedit_char_whitelist=abdcefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    flag= isTextInImage(text)
    if flag:
        return flag
    
    text = pytesseract.image_to_string(Image.open(imagePath),config='--psm 6 -c tessedit_char_whitelist=abdcefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    flag= isTextInImage(text)
    if flag:
        return flag

    text = pytesseract.image_to_string(Image.open(imagePath),config='--psm 9 -c tessedit_char_whitelist=abdcefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    flag= isTextInImage(text)
    if flag:
        return flag

    blurred = cv2.GaussianBlur(gray, (5, 5), 0) # Reduce noise
    thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1] # Apply thresholding
    text = pytesseract.image_to_string(thresh, lang='eng')
    flag= isTextInImage(text)
    if flag:
        return flag    


    return False

def isTextInImage(imageText: str) -> bool:
    # Get the text from the image
    # imageText = getTextFromImage(imagePath)
    imageText=imageText.strip()
    imageText =' '.join(imageText.splitlines())
    # Check if the search string is in the image text
    for search_string in search_string_list:
        if search_string in imageText:
            print('Text found in the image -- ',search_string)
            return True
    return False
    

def run() -> None:
   
    try:
        captureImage(IMAGE_NAME)
    except Exception as e:  
        print("Error in capturing image",e)
        quit()
   
    flag = getTextFromImage(IMAGE_NAME)
    
    if flag:
        issueCommand('mute')
    else:
        issueCommand('unmute')
        
  

def issueCommand(mycommand: str) -> None:
    #print("Issue command",mycommand)
    if mycommand == 'mute' and MUTE_FLAG==False:
        mute()
    elif mycommand == 'unmute':    
        unmute()
        


def mute():
   
    # call the webhook to mute the video
    try:
        now = datetime.datetime.now()
        formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        print("Mute the video",formatted_date_time)
        x=requests.get(UN_MUTE_WEBHOOK)
        global MUTE_FLAG
        MUTE_FLAG=True
        #print(x.text)
    except Exception as e:
        print("Error in calling the mute webhook",e)


def unmute():   

    # call the webhook to unmute the video
    try:

        global MUTE_FLAG
        if  MUTE_FLAG==True:
            now = datetime.datetime.now()
            formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
            print("UnMute the video",formatted_date_time)
            requests.get(UN_MUTE_WEBHOOK)
            MUTE_FLAG=False
    except Exception as e:
        print("Error in calling the unmute webhook",e)

def main():
    while True:
        run()
        time.sleep(SLEEP_TIME)
        
        #in future add keyboard event to stop the loop
        
     
if __name__ == '__main__':
  main()

