import pytesseract
import cv2
import numpy as np

fromQuesNum = 1
toQuesNum = 66
quesFrameShift = -30
leftCrop = 80

notSaved = []
for i in range(fromQuesNum, toQuesNum+1):
    img = cv2.imread(f"./output/{i}.png")
    data = pytesseract.image_to_data(
        img, output_type='dict', config="--psm 11", lang="eng")
    boxes = len(data['level'])
    lastQuesCoords = 0
    ok = False

    answerBox = []
    for j in range(boxes):
        (txt, x, y, w, h) = (data['text'][j], data['left'][j], data['top']
                             [j], data['width'][j], data['height'][j])
        if ('swer' in txt.lower()):
            ok = True
            answerBox.append(y)
    if (ok):
        y = answerBox[len(answerBox) - 1]
        img = img[0:y+quesFrameShift, leftCrop:]
        print(f"saving ques no. {i}")
        cv2.imwrite(f"./output/{i}.png", img)
    else:
        notSaved.append(i)

if (len(notSaved)):
    print("can't edit", notSaved)
