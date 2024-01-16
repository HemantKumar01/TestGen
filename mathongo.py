import pytesseract
import cv2
from pdf2image import convert_from_path
import numpy as np

pdf_file = "D:/Test Papers/JEE 2007 P1.pdf"
chapterName = "JEE-2007-P1"
fromPg = 1
toPg = 30


class config:
    questionBar = {"from": 0, "to": 200}
    border = {"left": 200, "right": -250, "top": 40, "bottom": -80}
    quesFrameShift = 10
    scaleFactor = 1.2
    downScaleFactor = 0.5
    blurFactor = 2


def preprocessImage(img_path):
    img = cv2.imread(img_path)
    # removing watermark
    img[np.all(img >= (210, 210, 210), axis=-1)] = (255, 255, 255)
    cv2.imwrite(img_path, img)


def pdfToImage():
    pages = convert_from_path(
        pdf_file,
        first_page=fromPg,
        last_page=toPg,
        poppler_path="./poppler/poppler-23.11.0/Library/bin/",
    )
    i = fromPg
    for page in pages:
        page.save(f"./raw_pages/page{i}.jpg", "JPEG")
        preprocessImage(f"./raw_pages/page{i}.jpg")
        i += 1


def getQuestionNum(txt):
    """
    parses question number (integer part) and return integer as a string
    """
    txt = txt.strip()
    if (not txt) or len(txt) == 0:
        return ""

    if txt[-1] in [".", ",", ";", ":", ")", "-"]:
        txt = txt[:-1]
        return getQuestionNum(txt)

    if txt[0] in [".", ",", ";", ":", ")", "-"]:
        txt = txt[1:]
        return getQuestionNum(txt)

    return txt


def isValidQuesNum(txt, lastQuesNum):
    txt = getQuestionNum(txt)
    return txt.isdigit() and int(txt) == lastQuesNum + 1


def getCoords():
    lastQuesNum = 0

    for i in range(fromPg, toPg + 1):
        img = cv2.imread(f"./raw_pages/page{i}.jpg")

        # ? if you are changing these end correction crop values then also note to change marginImg below
        img = img[config.border["top"] : config.border["bottom"], :].copy()

        marginImg = img.copy()
        marginImg = marginImg[:, config.questionBar["from"] : config.questionBar["to"]]

        marginImg = cv2.resize(
            marginImg, (0, 0), fx=config.scaleFactor, fy=config.scaleFactor
        )
        # also resizing img to remove any coordinate axis shift;
        img = cv2.resize(img, (0, 0), fx=config.scaleFactor, fy=config.scaleFactor)
        height, width, _ = img.shape

        marginImg = cv2.blur(marginImg, (config.blurFactor, config.blurFactor))

        data = pytesseract.image_to_data(
            marginImg, output_type="dict", config="--psm 6", lang="eng"
        )
        boxes = len(data["level"])
        lastQuesCoords = 0

        for j in range(boxes):
            (txt, x, y, w, h) = (
                data["text"][j],
                data["left"][j],
                data["top"][j],
                data["width"][j],
                data["height"][j],
            )
            x = x + config.questionBar["from"]

            # finalize and save last question;
            quesNum = getQuestionNum(txt)
            if isValidQuesNum(quesNum, lastQuesNum):
                if lastQuesCoords > 0:
                    print("saving ques. num.: ", lastQuesNum)
                    # end correction
                    lastQuesCoords = (
                        lastQuesCoords - config.quesFrameShift
                        if lastQuesCoords > config.quesFrameShift
                        else 0
                    )
                    y = y - config.quesFrameShift if y > config.quesFrameShift else y

                    cropAndSave(img, i, lastQuesNum, lastQuesCoords, y)

                lastQuesCoords = y
                lastQuesNum = int(quesNum)

        # for last question
        print("saving ques. num.: ", lastQuesNum)
        cropAndSave(img, i, lastQuesNum, lastQuesCoords, height)
        print(f"page {i} ends...")


def cropAndSave(img, pgNum, quesNum, y1, y2):
    imgCropped = img[y1:y2, config.border["left"] : config.border["right"]]

    imgCropped = cv2.resize(
        imgCropped, (0, 0), fx=config.downScaleFactor, fy=config.downScaleFactor
    )
    cv2.imwrite(f"./output/{quesNum}.png", imgCropped)


pdfToImage()
getCoords()
