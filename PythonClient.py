import cv2
import mediapipe as mp
import numpy as np
import socket

def send_data(data,host = "127.0.0.1", port=25001):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode("utf-8"),(host,port))
    except Exception as e:
        print(f"Error: {e}")

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence = 0.5,
    min_tracking_confidence=0.5
)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print(" ignoring empty camera frame.")
        continue

    frame = cv2.resize(frame, (320, 240))
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        data_list = []
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_drawing.draw_landmarks(frame,hand_landmarks, mp_hands.HAND_CONNECTIONS)
            handedness_label = results.multi_handedness[i].classification[0].label

            index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
            pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]

            handposx = (index_mcp.x + pinky_mcp.x) / 2
            handposy = (index_mcp.y + pinky_mcp.y) / 2

            data_list.extend([handedness_label, handposx, handposy])
        
        data = " ".join(map(str,data_list))
        print(data)      
        send_data(data)
    cv2.imshow("Hand Tracking", frame)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
            
            