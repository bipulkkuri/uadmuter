# Description: This script captures an image from a webcam, extracts text from the image using OCR,
# and issues a mute command if the extracted text contains predefined keywords.
# The script runs in an infinite loop with a delay between iterations.  The script uses pytesseract for OCR and OpenCV for image processing.
# The script also uses a predefined list of search strings to identify specific text patterns in the extracted text.
# The script sends a GET request to a predefined webhook URL to issue the mute command.
# The script also includes a function to unmute the system if it is currently muted.    The script uses the requests library to send HTTP requests to the webhook URL.
# The script includes a global variable to track the mute status and a predefined webhook URL for muting the system.
# The script logs the date and time when the mute action is triggered and when the system is unmuted.
# The script is designed to run continuously in an infinite loop, with a delay between iterations.
# The script can be stopped by interrupting the execution (e.g., using Ctrl+C).
# The script is intended to be run on a system with a webcam and an active internet connection.
# The script requires the pytesseract, OpenCV, and requests libraries to be installed. 
""" Imports """
import time
import datetime
import sys
import os
import cv2
import pytesseract
from PIL import Image
import requests
from dotenv import load_dotenv
from utils.config_reader import read_config,read_config_int



MUTE_FLAG = False # Global variable to track mute status
# Load environment variables from .env file
load_dotenv()
UN_MUTE_WEBHOOK = os.getenv("UN_MUTE_WEBHOOK") 
CONFIG_FILE = os.getenv("CONFIG_FILE")
if not CONFIG_FILE:
    raise ValueError("CONFIG_FILE environment variable is not set.")
HOMEASSISTANT_TIMEOUT=read_config_int(CONFIG_FILE,'HOMEASSISTANT','HOMEASSISTANT_TIMEOUT')
IMAGE_NAME = read_config(CONFIG_FILE,'CAMERA','IMAGE_NAME')
CAM_INDEX = read_config_int(CONFIG_FILE,'CAMERA','CAM_INDEX')
SLEEP_TIME = read_config_int(CONFIG_FILE,'CAMERA','SLEEP_TIME')
SEARCH_STRING_LIST= read_config(CONFIG_FILE,'CAMERA','SEARCH_STRING_LIST')
search_string_list = SEARCH_STRING_LIST.split(",")

def list_cameras():
    """
    Lists all available cameras connected to the system along with their indexes.

    This function iterates through potential camera indexes, starting from 0, and
    checks if a camera is available at each index. If a camera is found, its index
    is added to the list of available cameras, and additional information about the
    camera is retrieved using the `get_camera_info` function. The process stops
    when no more cameras are detected.

    Returns:
        list: A list of integers representing the indexes of available cameras.
    """
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


def get_camera_info(index)  -> str:
    """
    Retrieves information about a camera device at the specified index.

    This function attempts to open a video capture device using the given index.
    If successful, it retrieves and prints the backend name of the video capture
    device. If the device cannot be opened, it returns None.

    Args:
        index (int): The index of the camera device to query.

    Returns:
        str or None: The backend name of the video capture device if successfully
        opened, otherwise None.
    """
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        return "None"

    backend_name = cap.getBackendName()
    print(f"Backend name: {backend_name}")


def capture_image(imagePath) -> None:
    """
    Captures an image from the webcam and saves it to the specified file path.

    Args:
        imagePath (str): The file path where the captured image will be saved.

    Notes:
        - If the webcam fails to read a frame, the function will return without saving an image.
        - The function ensures the release of the camera resource and closes any OpenCV windows after execution.
    """
    cam = cv2.VideoCapture(CAM_INDEX)

    # Check if the camera opened successfully
    if not cam.isOpened():
        raise IOError("Cannot open webcam")

    # Read a frame from the camera
    result, image = cam.read()

    # Check if the frame was read successfully
    if not result:
        # raise IOError("Cannot read frame from webcam")
        # if cam fails retry after time interval do not abort
        return

        # Save the image
    cv2.imwrite(imagePath, image)

    # Release the camera
    cam.release()
    cv2.destroyAllWindows()
    # print("Picture saved as, ", imagePath)


def getTextFromImage(imagePath: str) -> bool:
    """
    Extracts text from an image file and determines if the text meets certain criteria.

    This function uses OpenCV and Tesseract OCR to process the image and extract text.
    It applies various preprocessing techniques and OCR configurations to improve text
    recognition accuracy. The extracted text is then evaluated using the `is_Text_Image`
    function to determine if it meets specific conditions.

    Args:
        imagePath (str): The file path to the image from which text needs to be extracted.

    Returns:
        bool: True if the extracted text meets the criteria defined in `is_Text_Image`,
              otherwise False.

    Notes:
        - The function uses multiple OCR configurations (`--psm` and `tessedit_char_whitelist`)
          to enhance text recognition.
        - Preprocessing techniques such as grayscale conversion, noise removal, and thresholding
          are applied to improve OCR results.
        - The `is_Text_Image` function is assumed to be defined elsewhere and is used to evaluate
          the extracted text.
    """
    # Open the image file
    img = cv2.imread(imagePath)
    # Convert the image to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Use pytesseract to get the text from the image
    # text = pytesseract.image_to_string(gray)

    # LOGICS to get the text from the image via different algos and settings Enhance for future
    # remove noise
    img = cv2.medianBlur(img, 5)
    text = pytesseract.image_to_string(
        img,
        config="--psm 7 -c tessedit_char_whitelist=abdcefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    )
    flag = is_text_image(text)
    if flag:
        return flag

    text = pytesseract.image_to_string(
        Image.open(imagePath),
        config="--psm 6 -c tessedit_char_whitelist=abdcefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    )
    flag = is_text_image(text)
    if flag:
        return flag

    text = pytesseract.image_to_string(
        Image.open(imagePath),
        config="--psm 9 -c tessedit_char_whitelist=abdcefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    )
    flag = is_text_image(text)
    if flag:
        return flag

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # Reduce noise
    thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[
        1
    ]  # Apply thresholding
    text = pytesseract.image_to_string(thresh, lang="eng")
    flag = is_text_image(text)
    if flag:
        return flag

    return False


def is_text_image(image_text: str) -> bool:
    """
    Checks if any of the predefined search strings are present in the given image text.

    Args:
        image_text (str): The text extracted from an image.

    Returns:
        bool: True if any of the search strings are found in the image text, False otherwise.

    Notes:
        - The input text is stripped of leading/trailing whitespace and normalized by 
          replacing line breaks with spaces before performing the search.
        - The function relies on a predefined list of search strings (`search_string_list`).
    """
    # Normalize the text
    image_text = image_text.strip()
    image_text = " ".join(image_text.splitlines())
    # Check if any search string is in the image text
    for search_string in search_string_list:
        if search_string in image_text:
            print("Text found in the image -- ", search_string)
            return True
    return False


def run() -> None:
    """
    Executes the main workflow of the program.

    The function performs the following steps:
    1. Attempts to capture an image using the `capture_image` function.
       If an exception occurs during this process, it prints an error message
       and terminates the program.
    2. Extracts text from the captured image using the `getTextFromImage` function.
    3. Based on the result of the text extraction:
       - Issues a "mute" command if the flag is True.
       - Issues an "unmute" command if the flag is False.
    """

    try:
        capture_image(IMAGE_NAME)
    except Exception as e:
        print("Error in capturing image", e)
        sys.exit()

    flag = getTextFromImage(IMAGE_NAME)

    if flag:
        issue_command("mute")
    else:
        issue_command("unmute")


def issue_command(mycommand: str) -> None: 
    """
    Executes a command to mute or unmute based on the provided input.

    Args:
        mycommand (str): The command to execute. 
                         Acceptable values are:
                         - "mute": Mutes the system if it is not already muted.
                         - "unmute": Unmutes the system.

    Returns:
        None
    """
    # print("Issue command",mycommand)
    if mycommand == "mute" and not MUTE_FLAG:
        mute()
    elif mycommand == "unmute":
        unmute()


def mute():
    """
    Mutes the video by calling a predefined webhook.

    This function sends a GET request to the `UN_MUTE_WEBHOOK` URL to mute the video.
    It also sets the global `MUTE_FLAG` to `True` upon successful execution.
    The function logs the current date and time when the mute action is triggered.
    If an error occurs during the webhook call, it logs the error message.

    Raises:
        Exception: If there is an issue with the webhook call.
    """

    # call the webhook to mute the video
    try:
        now = datetime.datetime.now()
        formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        print("Mute the video", formatted_date_time)
        requests.get(UN_MUTE_WEBHOOK,timeout=HOMEASSISTANT_TIMEOUT)
        global MUTE_FLAG
        MUTE_FLAG = True
    except Exception as e:
        print("Error in calling the mute webhook", e)


def unmute():
    """
    Unmutes the video by calling a predefined webhook.

    This function checks the global `MUTE_FLAG` to determine if the video is currently muted.
    If muted, it sends a GET request to the `UN_MUTE_WEBHOOK` URL to unmute the video and
    updates the `MUTE_FLAG` to False. The function also logs the unmute action with a timestamp.

    Exceptions:
        Catches and logs any exceptions that occur during the webhook call.

    Global Variables:
        MUTE_FLAG (bool): A flag indicating whether the video is currently muted.
        UN_MUTE_WEBHOOK (str): The URL of the webhook to call for unmuting the video.

    Logs:
        Prints the unmute action with the current timestamp or an error message if the webhook call fails.
    """

    # call the webhook to unmute the video
    try:

        global MUTE_FLAG
        if MUTE_FLAG:
            now = datetime.datetime.now()
            formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
            print("UnMute the video", formatted_date_time)
            requests.get(UN_MUTE_WEBHOOK,timeout=HOMEASSISTANT_TIMEOUT)
            MUTE_FLAG = False
    except Exception as e:
        print("Error in calling the unmute webhook", e)


def main():
    """
    The main function that runs an infinite loop to repeatedly execute the `run` function
    with a delay specified by `SLEEP_TIME`. This function is intended to be the entry point
    of the program.

    Note:
        - The loop currently runs indefinitely.
        - Future enhancements may include adding a keyboard event to stop the loop.
    """
    while True:
        run()
        time.sleep(SLEEP_TIME)

        # in future add keyboard event to stop the loop


if __name__ == "__main__":
    main()
