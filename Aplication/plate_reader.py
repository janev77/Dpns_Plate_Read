import re
import cv2
import yolov5
import numpy as np
from easyocr import Reader

# Load YOLO model and EasyOCR reader once (not on every function call)
model = yolov5.load('keremberke/yolov5n-license-plate')
model.conf = 0.3
model.iou = 0.45
model.max_det = 5

reader = Reader(['en'], gpu=False)

def remove_largest_colored_boxes(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    red_mask = cv2.inRange(hsv, (0, 70, 50), (10, 255, 255)) | \
               cv2.inRange(hsv, (170, 70, 50), (180, 255, 255))
    blue_mask = cv2.inRange(hsv, (100, 80, 50), (140, 255, 255))

    def blur_largest(mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
            roi = img[y:y + h, x:x + w]
            blur = cv2.GaussianBlur(roi, (99, 99), 50)
            faded = cv2.addWeighted(blur, 0.5, np.full_like(blur, 255), 0.5, 0)
            img[y:y + h, x:x + w] = faded

    blur_largest(red_mask)
    blur_largest(blue_mask)
    return img

def clean_text(text):
    cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
    if len(cleaned) >= 3 and not cleaned[2].isdigit():
        cleaned = cleaned[:2] + cleaned[3:]
    if len(cleaned) >= 3 and all(c.isalpha() for c in cleaned[-3:]):
        cleaned = cleaned[:-1]
    return cleaned[:8]

def detect_plate_and_read_text(img):
    if img is None:
        print("Empty frame")
        return None

    results = model(img)
    predictions = results.pred[0]

    if predictions is None or len(predictions) == 0:
        print("No plates detected")
        return None



    predictions = sorted(predictions, key=lambda x: x[4], reverse=True)

    for pred in predictions:
        x1, y1, x2, y2, conf, cls = pred.cpu().numpy()
        plate_img = img[int(y1):int(y2), int(x1):int(x2)]


        plate_img = remove_largest_colored_boxes(plate_img)
        plate_img = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        plate_img = cv2.equalizeHist(plate_img)
        plate_img = cv2.GaussianBlur(plate_img, (3, 3), 0)

        result = reader.readtext(plate_img)
        full_text = "".join([item[1] for item in result])
        final_text = clean_text(full_text)

        if len(final_text) >= 5:
            print("Detected:", final_text)
            return final_text

    return None
