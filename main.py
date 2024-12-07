import cv2
import pandas as pd
from ultralytics import YOLO
import cvzone
from picamera2 import Picamera2 
import RPi.GPIO as GPIO
import time
def main():
    def draw_zones(img, rows, cols, zone_names):
        height, width, _ = img.shape
        zone_height = height // rows
        zone_width = width // cols

        # Draw horizontal lines
        for r in range(1, rows):
            y = r * zone_height
            cv2.line(img, (0, y), (width, y), (255, 0, 0), 2)

        # Draw vertical lines
        for c in range(1, cols):
            x = c * zone_width
            cv2.line(img, (x, 0), (x, height), (255, 0, 0), 2)

        # Add zone labels
        for r in range(rows):
            for c in range(cols):
                x = c * zone_width
                y = r * zone_height
                zone_index = r * cols + c + 1
                zone_name = zone_names.get(zone_index, f"Zone {zone_index}")
                cvzone.putTextRect(img, zone_name, (x, y), 1, 1)

    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (1280, 720)
    picam2.preview_configuration.main.format = 'RGB888'
    picam2.preview_configuration.align()
    picam2.configure("preview")
    picam2.start()
    model = YOLO('yolov8n.pt')
    with open("coco.txt", "r") as my_file:
        class_list = my_file.read().split("\n")
    while True:
        frame = picam2.capture_array()
        rows, cols = 2, 2
        zone_names = {}
        zone_indices = {}

        # Generate zone names
        for r in range(rows):
            for c in range(cols):
                zone_index = r * cols + c + 1
                zone_names[zone_index] = f"Zone {zone_index}"
                zone_indices[zone_index] = (r, c)

        # Draw zones on the frame
        draw_zones(frame, rows, cols, zone_names)

        # Calculate zone dimensions
        zone_height = frame.shape[0] // rows
        zone_width = frame.shape[1] // cols

        # Initialize LED pin and GPIO
        ledpin = 3
        ledpin1 = 5
        ledpin2=7
        ledpin3=11
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(ledpin, GPIO.OUT)
        GPIO.setup(ledpin1, GPIO.OUT)
        GPIO.setup(ledpin2, GPIO.OUT)
        GPIO.setup(ledpin3, GPIO.OUT)

        # Initialize a list to store detected zones
        detected_zones = []

        # Loop through each zone and perform object detection
        for zone_index in range(1, rows * cols + 1):
            zone_row, zone_col = zone_indices.get(zone_index, (0, 0))
            y1 = zone_row * zone_height
            y2 = (zone_row + 1) * zone_height
            x1 = zone_col * zone_width
            x2 = (zone_col + 1) * zone_width

            zone = frame[y1:y2, x1:x2]

            # Perform object detection with YOLO
            results = model.predict(zone)
            a = results[0].boxes.data.cpu().numpy()
            px = pd.DataFrame(a).astype("float")

            # Process detected objects
            for index, row in px.iterrows():
                x1_zone = int(row[0])
                y1_zone = int(row[1])
                x2_zone = int(row[2])
                y2_zone = int(row[3])
                d = int(row[5])
                c = class_list[d]

                # Check if the detected object is a person
                if 'person' in c:
                    x1 = x1 + x1_zone
                    y1 = y1 + y1_zone
                    x2 = x1 + x2_zone
                    y2 = y1 + y2_zone
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
                    cvzone.putTextRect(frame, f'{c}', (x1, y1), 1, 1)

                    # Store the detected zone
                    detected_zones.append(zone_index)

        # If a person is detected, blink the LED
        if detected_zones:
            print("Person detected in the following zones:")
            for zone_index in detected_zones:
                print(f"Zone {zone_index}")
            person_detected_in_zone1 = 1 in detected_zones
            person_detected_in_zone2 = 2 in detected_zones
            person_detected_in_zone3 = 3 in detected_zones
            person_detected_in_zone4 = 4 in detected_zones
            

            if person_detected_in_zone1 and person_detected_in_zone2 and person_detected_in_zone3 and person_detected_in_zone4 :
                # Turn on both LED pins
                GPIO.output(ledpin, False)
                GPIO.output(ledpin1, False)
                GPIO.output(ledpin2, False)
                GPIO.output(ledpin3, False)
            elif person_detected_in_zone1 and person_detected_in_zone2:
                GPIO.output(ledpin,False)
                GPIO.output(ledpin1,False)
                GPIO.output(ledpin2,True)
                GPIO.output(ledpin3,True)
            elif person_detected_in_zone1 and person_detected_in_zone3:
                GPIO.output(ledpin,False)
                GPIO.output(ledpin1,True)
                GPIO.output(ledpin2,False)
                GPIO.output(ledpin3,True)
            elif person_detected_in_zone1 and person_detected_in_zone4:
                GPIO.output(ledpin,False)
                GPIO.output(ledpin1,True)
                GPIO.output(ledpin2,True)
                GPIO.output(ledpin3,False)
            elif person_detected_in_zone2 and person_detected_in_zone3:
                GPIO.output(ledpin,True)
                GPIO.output(ledpin1,False)
                GPIO.output(ledpin2,False)
                GPIO.output(ledpin3,True)
            elif person_detected_in_zone2 and person_detected_in_zone4:
                GPIO.output(ledpin,True)
                GPIO.output(ledpin1,False)
                GPIO.output(ledpin2,True)
                GPIO.output(ledpin3,False)
            elif person_detected_in_zone3 and person_detected_in_zone4:
                GPIO.output(ledpin,True)
                GPIO.output(ledpin1,True)
                GPIO.output(ledpin2,False)
                GPIO.output(ledpin3,False)
            elif person_detected_in_zone1 and person_detected_in_zone2 and person_detected_in_zone3 :
                GPIO.output(ledpin,False)
                GPIO.output(ledpin1,False)
                GPIO.output(ledpin2,False)
                GPIO.output(ledpin3,True)
            elif person_detected_in_zone1 and person_detected_in_zone2 and person_detected_in_zone4 :
                GPIO.output(ledpin,False)
                GPIO.output(ledpin1,False)
                GPIO.output(ledpin2,True)
                GPIO.output(ledpin3,False)
            elif person_detected_in_zone2 and person_detected_in_zone3 and person_detected_in_zone4 :
                GPIO.output(ledpin,True)
                GPIO.output(ledpin1,False)
                GPIO.output(ledpin2,False)
                GPIO.output(ledpin3,False)
            elif person_detected_in_zone3 and person_detected_in_zone4 and person_detected_in_zone1 :
                GPIO.output(ledpin,False)
                GPIO.output(ledpin1,True)
                GPIO.output(ledpin2,False)
                GPIO.output(ledpin3,False)
            
           elif person_detected_in_zone2 and person_detected_in_zone3 and person_detected_in_zone4 :
                GPIO.output(ledpin,True)
                GPIO.output(ledpin1,False)
                GPIO.output(ledpin2,False)
                GPIO.output(ledpin3,False) 
            elif person_detected_in_zone1:
                # Turn on LED pin 3
                GPIO.output(ledpin,False)
                GPIO.output(ledpin1, True)
                GPIO.output(ledpin2, True)
                GPIO.output(ledpin3, True)
            elif person_detected_in_zone2:
                # Turn on LED pin 3
                GPIO.output(ledpin1,False)
                GPIO.output(ledpin, True)
                GPIO.output(ledpin2, True)
                GPIO.output(ledpin3, True)
            elif person_detected_in_zone3:
                # Turn on LED pin 7
                GPIO.output(ledpin1,True)
                GPIO.output(ledpin, True)
                GPIO.output(ledpin2, False)
                GPIO.output(ledpin3, True)
            elif person_detected_in_zone4:
                # Turn on LED pin 11
                GPIO.output(ledpin1,True)
                GPIO.output(ledpin, True)
                GPIO.output(ledpin2, True)
                GPIO.output(ledpin3, False)
        else:
            GPIO.output(ledpin, True)
            GPIO.output(ledpin1,True)
            GPIO.output(ledpin2, True)
            GPIO.output(ledpin3, True)

        cv2.imshow("picam", frame)

                # Wait for 10 seconds and check for 'q' key press
        start_time = time.time()
        while time.time() - start_time < 10:
            if cv2.waitKey(1) == ord('q'):
                 break

                # Close the OpenCV window
        cv2.destroyAllWindows()
        # Wait for 20 seconds before repeating the process
        time.sleep(10)

if _name_ == "_main_":
    main()
