import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
import platform
import subprocess
import screen_brightness_control as sbc

IS_LINUX = platform.system() == "Linux"

BRIGHTNESS = 5
NORMAL_BRIGHTNESS = 100

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

def set_brightness(distance, threshold=35):
    level = BRIGHTNESS if distance < threshold else NORMAL_BRIGHTNESS
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

def main(cam=0, quit_button='q'):
    cap = None
    try:
        if cam is not None:
            cap = cv2.VideoCapture(cam)
        else:
            _, cap = get_camera()
        
        detector = FaceMeshDetector(maxFaces=1)

        while True:
            success, frame = cap.read()
            if not success:
                print("Kamera görüntüsü alınamıyor.")
                break

            frame, faces = detector.findFaceMesh(frame, draw=False)

            if faces:
                face = faces[0]
                pointLeft = face[145]
                pointRight = face[374]

                w, _ = detector.findDistance(pointLeft, pointRight)
                d = calculate_distance(w)

                # Uyarı ve parlaklık
                if d <= 35:
                    cvzone.putTextRect(frame, "Ekrana Cok Yakin!", (20, 70), 5, 3, (0, 0, 255))
                else:
                    cvzone.putTextRect(frame, "Mesafe Iyi", (20, 70), 5, 3, (0, 255, 0))

                set_brightness(d)

                cvzone.putTextRect(
                    frame,
                    f"{int(d)} cm",
                    (face[10][0] - 100, face[10][1] - 50),
                    scale=2
                )

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

