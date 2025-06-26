from threading import Event
import time

from sympy import false

stop_event = Event()
def start_camera_loop():
    import cv2
    from Aplication.models import Plate
    from .pleatReader import detect_plate_and_read_text

    cap = cv2.VideoCapture(0)
    first=True
    last=""
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Kamera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break

        plate_text = detect_plate_and_read_text(frame)

#TODO: treba da proveri dali ja ima vo baza
        # ako ja ima da pravi nesto i
        # da zapise prisustvo vo drug model
        # so ova https://www.w3schools.com/nodejs/nodejs_raspberrypi_led_pushbutton.asp
        # ce napravime da dava signal ili semafor crveno i zeleno ja ce sredam za ova
        if plate_text and len(plate_text) > 4:
            print("Табличка:", plate_text)

            if first:
                first=False
                last=plate_text
            elif(last!=plate_text):
                last = plate_text
                Plate.objects.create(plate_number=plate_text)
                print("Ново различно:", plate_text)
            else:
                Plate.objects.filter(plate_number=plate_text).update(plate_text)



        time.sleep(3)# ovde menuvas kolku brzo da fati slika



    cap.release()
    cv2.destroyAllWindows()
