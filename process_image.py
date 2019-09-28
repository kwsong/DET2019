import cv2
import numpy as np
from PIL import Image
import os

PROCESSED_IMAGES = "processed_images"


def make_greyscale(image):
    img_orig = Image.open(image)
    img_greyscale = img_orig.convert("L")
    image_name = f"processed_images/{image.rsplit('.')[0]}_p.jpg"
    img_greyscale.save(image_name)
    return image_name


def filter_image(image):

    img = cv2.imread(image, 0)

#    img = cv2.fastNlMeansDenoising(img, None, 20, 7, 21)
    img = cv2.medianBlur(img, 5)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY_INV, 7, 2)

#    img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    cv2.imwrite(image, img)


def crop_image(image):
    """Takes an image file and crops it in halves and stores it as the file name with 
    "_bottom" and "_top" added accordingly.

    Arguments:
        image {str} -- pathname of image in current directory

    Returns:
        (top_image_name: {str}, bottom_image_name: {str}) -- a tuple with the image names
    """
    img = Image.open(image)

    img_bbox = img.getbbox()

    top_bbox = (img_bbox[0], img_bbox[1], img_bbox[2], img_bbox[3] / 2)
    bottom_bbox = (img_bbox[0], img_bbox[3] / 2, img_bbox[2], img_bbox[3])

    top_img = img.crop(top_bbox)
    bottom_img = img.crop(bottom_bbox)
    top_image_name = f"{image.rsplit('.')[0]}_top.jpg"
    top_img.save(top_image_name)

    bottom_image_name = f"{image.rsplit('.')[0]}_bottom.jpg"
    bottom_img.save(bottom_image_name)

    return (top_image_name, bottom_image_name)


def process_image(original_image):
    """Preprocessing for images to prepare for GCV

    Arguments:
        image {str} -- pathname of image in current directory

    Returns:
        (dealer_image {str}, player_image {str}, image {str}) -- the relative paths to each image
    """

    try:
        os.mkdir(PROCESSED_IMAGES)
    except FileExistsError:
        pass

    image = make_greyscale(original_image)
    filter_image(image)
    dealer_image, player_image = crop_image(image)
    return dealer_image, player_image, image


if __name__ == '__main__':
    process_image("image.jpg")
