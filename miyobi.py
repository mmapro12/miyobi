#!/usr/bin/env python

import cv2
import cvzone
import time
import platform
import subprocess
import psutil
import screen_brightness_control as sbc
from cvzone.FaceMeshModule import FaceMeshDetector

IS_LINUX = platform.system() == "Linux"

BRIGHTNESS = 1
NORMAL_BRIGHTNESS = 100
CURRENT_BRIGHTNESS = -1

if not IS_LINUX:
    try:
        NORMAL_BRIGHTNESS = sbc.get_brightness()
        if isinstance(NORMAL_BRIGHTNESS, list):
            NORMAL_BRIGHTNESS = NORMAL_BRIGHTNESS[0]
    except:
        NORMAL_BRIGHTNESS = 100

def get_camera():
    for cam_num in range(6):
        cap = cv2.VideoCapture(cam_num)
        if cap.isOpened():
            return cam_num, cap
    raise ValueError("Kullanılabilir kamera bulunamadı!")

def calculate_distance(w, W=6.3, f=600):
    return W * f / w

def set_brightness(distance, threshold=45):
    global CURRENT_BRIGHTNESS
    level = BRIGHTNESS if distance < threshold else NORMAL_BRIGHTNESS

    if level == CURRENT_BRIGHTNESS:
        return  # Aynı parlaklık zaten ayarlıysa değişiklik yapma

    CURRENT_BRIGHTNESS = level
    if IS_LINUX:
        try:
            subprocess.run(["brightnessctl", "s", f"{level}%"], check=True)
        except Exception as e:
            print(f"brightnessctl hatası: {e}")
    else:
        try:
            sbc.set_brightness(level)
        except Exception as e:
            print(f"Parlaklık ayarlanamadı: {e}")

def print_resource_usage():
    process = psutil.Process()
    cpu = process.cpu_percent(interval=0.1)
    ram = process.memory_info().rss / 1024 / 1024
    print(f"[KAYNAK KULLANIMI] CPU: {cpu:.2f}%, RAM: {ram:.2f} MB")

def main(cam=0, quit_button='q'):
    cap = None
    try:
        if cam is not None:
            cap = cv2.VideoCapture(cam)
        else:
            _, cap = get_camera()

        detector = FaceMeshDetector(maxFaces=1)
        last_time = time.time()
        fps_limit = 10
        frame_counter = 0
        skip_frames = 2

        while True:
            if time.time() - last_time < 1 / fps_limit:
                continue
            last_time = time.time()
            frame_counter += 1

            success, frame = cap.read()
            if not success:
                print("Kamera görüntüsü alınamıyor.")
                break

            if frame_counter % skip_frames == 0:
                frame, faces = detector.findFaceMesh(frame, draw=False)

                if faces:
                    face = faces[0]
                    pointLeft = face[145]
                    pointRight = face[374]

                    w, _ = detector.findDistance(pointLeft, pointRight)
                    d = calculate_distance(w)

                    set_brightness(d)

                    cvzone.putTextRect(
                        frame,
                        f"{int(d)} cm",
                        (face[10][0] - 100, face[10][1] - 50),
                        scale=2
                    )

            if frame_counter % 10 == 0:
                print_resource_usage()

            cv2.imshow("Miyobi", frame)
            if cv2.waitKey(1) & 0xFF == ord(quit_button):
                break

    except Exception as e:
        print(f"Hata: {e}")
    finally:
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Welcome to Miyobi!")
    main(0, "q")
