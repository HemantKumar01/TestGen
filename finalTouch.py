import cv2
import os

arr = os.listdir("./allen/")
for i in arr:
    img = cv2.imread(f"./allen/{i}")
    h, w, c = img.shape
    img = img[0:h, 0 : int(w / 2)]
    cv2.imwrite(f"./allen/{i}", img)
