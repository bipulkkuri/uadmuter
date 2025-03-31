import cv2 as cv
import numpy as np
import pytesseract
from PIL import Image


def global_threshold(image, threshold=127):
    """
    Apply a global threshold to the image.

    Args:
        image (numpy.ndarray): The input image.
        threshold (int): The threshold value. Default is 127.

    Returns:
        numpy.ndarray: The thresholded image.
    """
    _, binary_image = cv.threshold(image, threshold, 255, cv.THRESH_BINARY)
    return binary_image


def adaptive_mean_threshold(image, block_size=11, C=2):
    """
    Applies adaptive mean thresholding to an input image.
    Adaptive mean thresholding calculates the threshold for a pixel based on
    the mean of the neighborhood area defined by the block size, and then
    subtracts a constant value (C) from it. This method is useful for images
    with varying lighting conditions.
    Args:
        image (numpy.ndarray): The input grayscale image to be thresholded.
        block_size (int, optional): Size of the neighborhood area used to
            calculate the threshold for each pixel. Must be an odd number.
            Default is 11.
        C (int, optional): Constant subtracted from the mean to fine-tune the
            thresholding. Default is 2.
    Returns:
        numpy.ndarray: The binary image resulting from adaptive mean thresholding.
    """

    binary_image = cv.adaptiveThreshold(
        image, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, block_size, C
    )
    return binary_image


def adaptive_gaussian_threshold(image, block_size=11, C=2):
    """
    Applies adaptive Gaussian thresholding to an input image.
    This function converts a grayscale image into a binary image using the
    adaptive Gaussian thresholding method. The threshold value is calculated
    for smaller regions of the image, which allows for better handling of
    varying lighting conditions.
    Args:
        image (numpy.ndarray): The input grayscale image to be thresholded.
        block_size (int, optional): Size of the neighborhood area used to
            calculate the threshold value for each pixel. Must be an odd number.
            Default is 11.
        C (int, optional): A constant subtracted from the mean or weighted mean
            calculated for the neighborhood of a pixel. Default is 2.
    Returns:
        numpy.ndarray: The binary image resulting from the adaptive Gaussian
        thresholding process.
    """

    binary_image = cv.adaptiveThreshold(
        image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, block_size, C
    )
    return binary_image


def otsu_threshold(image):
    """
    Apply Otsu's thresholding to the image.

    Args:
        image (numpy.ndarray): The input image.

    Returns:
        numpy.ndarray: The thresholded image.
    """
    _, binary_image = cv.threshold(image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    return binary_image


def get_blur_image(image):
    gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred_image = cv.GaussianBlur(gray_image, (5, 5), 0)
    return blurred_image


def get_adaptive_mean_threshold(image):
    blurred_image = get_blur_image(image)
    binary_image = adaptive_gaussian_threshold(blurred_image)
    return binary_image


def get_adaptive_gaussian_threshold(image):
    blurred_image = get_blur_image(image)
    binary_image = adaptive_gaussian_threshold(blurred_image)
    return binary_image


def get_otsu_threshold(image):
    blurred_image = get_blur_image(image)
    binary_image = otsu_threshold(blurred_image)
    return binary_image


def get_gam_text(image_path) -> str:
    image = cv.imread(image_path)
    bimage = get_adaptive_mean_threshold(image)
    text = get_text_image(bimage)
    return text


def get_gag_text(image_path) -> str:
    image = cv.imread(image_path)
    bimage = get_adaptive_gaussian_threshold(image)
    text = get_text_image(bimage)
    return text


def get_otsu_text(image_path) -> str:
    image = cv.imread(image_path)
    bimage = get_otsu_threshold(image)
    text = get_text_image(bimage)
    return text


def get_text_image(image) -> str:
    ALPHA_NUM_TEXT = "tessedit_char_whitelist=abdcefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    custom_config = "--psm 6 -c " + ALPHA_NUM_TEXT
    # Extract text using Tesseract OCR
    text = pytesseract.image_to_string(image, config=custom_config)
    text = text.replace("\r\n", "").replace("\n", "")

    return text


def main():
    image_path = "images/picture.png"
    text = get_otsu_text(image_path)
    print(text)


if __name__ == "__main__":
    main()
