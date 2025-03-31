# Description: This script captures an image from a webcam, extracts text from the image using OCR,
# and issues a mute command if the extracted text contains predefined keywords.
# The script runs in an infinite loop with a delay between iterations.
# The script uses pytesseract for OCR and OpenCV for image processing.
# The script also uses a predefined list of search strings to identify specific text patterns in the extracted text.
# The script sends a GET request to a predefined webhook URL to issue the mute command.
# The script also includes a function to unmute the system if it is currently muted.
# The script uses the requests library to send HTTP requests to the webhook URL.
# The script includes a global variable to track the mute status and a predefined webhook URL for muting the system.
# The script logs the date and time when the mute action is triggered and when the system is unmuted.
# The script is designed to run continuously in an infinite loop, with a delay between iterations.
# The script can be stopped by interrupting the execution (e.g., using Ctrl+C).
# The script is intended to be run on a system with a webcam and an active internet connection.
# The script requires the pytesseract, OpenCV, and requests libraries to be installed.
"""Imports"""

import time
import datetime
import sys
import cv2
import multiprocessing
import requests
import utils.constants as CONSTANTS


from utils.ocr_helper import get_gam_text, get_gag_text, get_otsu_text

MUTE_FLAG = False  # Global variable to track mute status
# Load environment variables from .env file


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


def get_camera_info(index) -> str:
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
    cam = cv2.VideoCapture(CONSTANTS.CAM_INDEX)

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
    return process_image(imagePath)


def run_algorithm(algorithm, data):
    start_time = time.time()
    result = algorithm(data)
    end_time = time.time()
    return algorithm.__name__, result, end_time - start_time


def run_algorithms_parallel(algorithms, data):
    with multiprocessing.Pool() as pool:
        results = pool.starmap(run_algorithm, [(algo, data) for algo in algorithms])
    return results


def process_image(image_path) -> bool:
    algorithms_to_test = [get_otsu_text, get_gam_text, get_gag_text]
    results = run_algorithms_parallel(algorithms_to_test, image_path)
    for name, result, runtime in results:
        result = result.strip()
        print(f"Algorithm: {name}, Result: {result}, Runtime: {runtime:.4f} seconds")
        flag = is_text_image(result)
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
    for search_string in CONSTANTS.search_string_list:
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
    if CONSTANTS.CAM_ENABLED:
        try:
            capture_image(CONSTANTS.IMAGE_NAME)
        except Exception as e:
            print("Error in capturing image", e)
            sys.exit()

    flag = getTextFromImage(CONSTANTS.IMAGE_NAME)

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
    else:
        print(f"nothing to do,{mycommand} is {MUTE_FLAG}")


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
        requests.get(CONSTANTS.UN_MUTE_WEBHOOK, timeout=CONSTANTS.HOMEASSISTANT_TIMEOUT)
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
            requests.get(
                CONSTANTS.UN_MUTE_WEBHOOK, timeout=CONSTANTS.HOMEASSISTANT_TIMEOUT
            )
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
    list_cameras()
    while True:
        run()
        time.sleep(CONSTANTS.SLEEP_TIME)

        # in future add keyboard event to stop the loop


if __name__ == "__main__":
    main()
