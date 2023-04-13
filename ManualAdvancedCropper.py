# this version checks the keyword "Answer" instead of numbers

import pytesseract
import cv2
from pdf2image import convert_from_path
import numpy as np

pdf_file = 'D:/Test Papers/JEE Adv 2012 P2.pdf'
chapterName = "JEE-2012-P2"
# set this to be false if you have already saved the pages #!if false then also set config.totalPages
savePagesFirst = True


img = None
cachedImg = None
height = 0
width = 0
channel = 0
cropHeight = -1  # y1
quesNum = 1
windowHeight = 720  # height of cv2 window in which image will be displayed


class config:
    border = {
        "left": 0,
        "right": -1,
    }
    # will be automatically set. i#!if savePagesFirst = False then manually adjust it
    totalPages = 24
    downScaleFactor = 0.5


def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)


def pdfToImage():
    pages = convert_from_path(pdf_file,
                              poppler_path='./poppler/poppler-22.04.0/Library/bin/')
    i = 1
    for page in pages:
        page.save(f'./raw_pages/page{i}.jpg', 'JPEG')
        i += 1
    config.totalPages = i


def cropManager(image, newY):
    global quesNum, cropHeight
    if (cropHeight != -1):
        print("Saving Ques. no. ", quesNum)

        cropAndSave(image, quesNum, cropHeight+2, newY-2)
        cropHeight = -1
        quesNum += 1
    else:
        cropHeight = newY

# function to get the coordinates of
# of the points clicked on the image


def click_event(event, x, y, flags, params):
    global cropHeights, cachedImg, img, quesNum, height
    # checking for left mouse clicks for drawing reference line
    if event == cv2.EVENT_MOUSEMOVE:

        img = cachedImg.copy()
        img = ResizeWithAspectRatio(img, height=windowHeight)
        line_thickness = 2

        cv2.line(img, (0, y), (width, y),
                 (200, 200, 230), thickness=line_thickness)
        cv2.imshow('Image', img)

    # checking for left mouse clicks for setting point
    if event == cv2.EVENT_LBUTTONDOWN:
        img = cachedImg.copy()
        img = ResizeWithAspectRatio(img, height=windowHeight)

        line_thickness = 2
        cv2.line(img, (0, y), (width, y),
                 (200, 200, 230), thickness=line_thickness)
        cv2.line(cachedImg, (0, round((y/windowHeight)*height)), (width, round((y/windowHeight)*height)),
                 (200, 200, 230), thickness=line_thickness)
        cropManager(cachedImg,  round((y/windowHeight)*height))

        cv2.imshow('Image', img)


def getCoords():
    global img, height, width, channel, cachedImg, quesNum

    for i in range(1, config.totalPages + 1):
        print("starting pg no. ", i)

        img = cv2.imread(f"./raw_pages/page{i}.jpg")
        cachedImg = img.copy()
        height, width, channel = img.shape

        img = ResizeWithAspectRatio(img, height=windowHeight)
        cv2.imshow(f"Image", img)

        # setting mouse handler for the image
        # and calling the click_event() function
        cv2.setMouseCallback(f'Image', click_event)

        # wait for a key to be pressed to exit
        cv2.waitKey(0)

        # close the window
        cv2.destroyAllWindows()


def cropAndSave(image, quesNum, y1, y2):
    imgCropped = image[y1:y2, config.border["left"]:config.border["right"]]

    imgCropped = cv2.resize(
        imgCropped, (0, 0), fx=config.downScaleFactor, fy=config.downScaleFactor)
    cv2.imwrite(f'./output/{quesNum}.png', imgCropped)


if (savePagesFirst):
    pdfToImage()
getCoords()
