import re
import cv2
import yolov5
from easyocr import easyocr
import numpy as np

model = yolov5.load('keremberke/yolov5n-license-plate')
model.conf = 0.25
model.iou = 0.45
model.agnostic = False
model.multi_label = False
model.max_det = 1000

def remove_largest_colored_boxes(img):



    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])
    lower_blue = np.array([100, 80, 50])
    upper_blue = np.array([140, 255, 255])


    red_mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    def find_largest_contour(mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            return cv2.boundingRect(largest)
        return None


    red_box = find_largest_contour(red_mask)
    blue_box = find_largest_contour(blue_mask)

    for box in [red_box, blue_box]:
        if box:
            x, y, w, h = box
            roi = img[y:y + h, x:x + w]

            blurred = cv2.GaussianBlur(roi, (99, 99), 50)
            faded = cv2.addWeighted(blurred, 0.5, np.full_like(blurred, 255), 0.5, 0)
            img[y:y + h, x:x + w] = faded

    return img


def detect_plate_and_read_text(img): #image_path):


    # image_path = "viber_image_2025-06-13_23-11-30-996.jpg"
    # img = cv2.imread(image_path)

    if img is None:
        print("Se eba majkata nesto", img)#image_path)
        exit()

    results = model(img)
    predictions = results.pred[0]

    if predictions is None or len(predictions) == 0:
        print("problem a name")
        return None


    x1, y1, x2, y2 = predictions[0][:4].cpu().numpy().astype(int)

    plate_img = img[y1:y2, x1:x2]

    ksize = (5, 5)
    image = cv2.blur(plate_img, ksize)
    image=remove_largest_colored_boxes(image)
    ksize = (1, 1)
    image = cv2.blur(image, ksize)

    # cv2.imshow("Detected Plate", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    reader = easyocr.Reader(['en'])
    result = reader.readtext(image)
    string=""
    for each in result:
        string+=each[-2]

    cleaned = re.sub(r'[^A-Za-z0-9]', '', string)
    if len(cleaned) >= 3 and not cleaned[2].isdigit():
        cleaned=cleaned[:2] + cleaned[3:]
    if len(cleaned) >= 3 and all(c.isalpha() for c in cleaned[-3:]):
        cleaned = cleaned[:-1]
    string = cleaned.upper()

    print(string)
    return string




