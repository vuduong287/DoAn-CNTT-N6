import cv2
import mediapipe as mp
import pyautogui
from pynput.mouse import Button, Controller
import util
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import comtypes
import time

import tkinter as tk
from tkinter import Label

import threading
from PIL import Image, ImageTk

from nhandiencamxuc import nhandiencamxuc

mouse = Controller()
screen_width, screen_height = pyautogui.size()
pyautogui.FAILSAFE = False

mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)

previous_right_x = None
previous_left_x = None
active_hand = None  # Theo dõi tay đang hoạt động (trái hoặc phải)
previous_time = None  # Lưu thời gian trước đó

zoom_level = 1.0


def dieu_chinh_man_hinh(thumb_tip, middle_finger_tip):
    global zoom_level
    if thumb_tip and middle_finger_tip:
        # Tính khoảng cách giữa ngón cái và ngón giữa
        toa_do_ngon_cai = (thumb_tip.x, thumb_tip.y)
        toa_do_ngon_giua = (thumb_tip.x, middle_finger_tip.y)
        distance = util.get_distance([toa_do_ngon_cai, toa_do_ngon_giua])

        # Phóng to hoặc thu nhỏ màn hình
        if distance > 150 and zoom_level < 2.0:
            zoom_level += 0.1
            if zoom_level > 2.0:
                zoom_level = 2.0
            pyautogui.hotkey('ctrl', '+')
            print(f"Phóng to màn hình: {zoom_level * 100}%")
        
        elif distance < 100 and zoom_level > 1.0:
            zoom_level -= 0.1
            if zoom_level < 1.0:
                zoom_level = 1.0
            pyautogui.hotkey('ctrl', '-')
            print(f"Thu nhỏ màn hình: {zoom_level * 100}%")

def nhan_dien_vuot(index_finger_tip):
    global previous_right_x, previous_time, last_swipe_time

    x = index_finger_tip.x  # Tọa độ x của ngón trỏ hiện tại
    current_time = time.time()  # Thời gian hiện tại

    # Nếu đây là lần đầu tiên chạy, lưu lại thời gian và vị trí
    if previous_time is None:
        previous_time = current_time

    # Tính thời gian chênh lệch giữa các khung hình
    time_diff = current_time - previous_time

    if time_diff == 0:
        return None  # Đề phòng chia cho 0

    nguong_toc_do = 1.5  # Ngưỡng tốc độ 

    

    # Thời gian tối thiểu giữa các lần vuốt
    min_swipe_interval = 0.5  # 0.5 giây

    if previous_right_x is not None:
        # Tính tốc độ dựa trên sự thay đổi vị trí và thời gian
        tocdo = (x - previous_right_x) / time_diff
        
        # Kiểm tra vuốt sang phải
        if tocdo > nguong_toc_do:
            # Kiểm tra thời gian đã trôi qua kể từ lần vuốt cuối
            if current_time - last_swipe_time >= min_swipe_interval:
                last_swipe_time = current_time  # Cập nhật thời gian vuốt cuối
                previous_time = current_time  # Cập nhật thời gian mới
                return "Next"
        
        # Kiểm tra vuốt sang trái
        elif tocdo < -nguong_toc_do:
            # Kiểm tra thời gian đã trôi qua kể từ lần vuốt cuối
            if current_time - last_swipe_time >= min_swipe_interval:
                last_swipe_time = current_time  # Cập nhật thời gian vuốt cuối
                previous_time = current_time  # Cập nhật thời gian mới
                return "Previous"
        
        previous_right_x = x

    # Lưu lại vị trí và thời gian để so sánh với lần tiếp theo
    previous_right_x = x
    previous_time = current_time
    return None

# Khởi tạo biến last_swipe_time
last_swipe_time = time.time()  # Khởi tạo để không xảy ra lỗi



def dieu_chinh_am_luong(thumb_tip, index_finger_tip):
    if thumb_tip and index_finger_tip:
        toa_do_ngon_cai = (thumb_tip.x, thumb_tip.y)
        toa_do_ngon_tro = (index_finger_tip.x, index_finger_tip.y)
        
        distance = util.get_distance([toa_do_ngon_cai, toa_do_ngon_tro])
        
        # Lấy Audio Endpoint Volume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)

        # Lấy âm lượng hiện tại
        current_volume = volume.GetMasterVolumeLevelScalar()

        if distance > 200 and current_volume < 1.0:
            # Tăng âm lượng khi khoảng cách lớn hơn 200
            new_volume = min(current_volume + 0.1, 1.0)
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            print(f"Tăng âm lượng: {new_volume}")
        elif distance < 100 and current_volume > 0.0:
            # Giảm âm lượng khi khoảng cách nhỏ hơn 100
            new_volume = max(current_volume - 0.1, 0.0)
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            print(f"Giảm âm lượng: {new_volume}")

def find_finger_tip(processed):
    if processed.multi_hand_landmarks:
        hand_landmarks = processed.multi_hand_landmarks[0]
        index_finger_tip = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
        thumb_tip = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_TIP]
        middle_finger_tip = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_TIP]
        return index_finger_tip, thumb_tip, middle_finger_tip
    return None, None, None

def ngon_cai_gap(landmark_list):
    thumb_tip = landmark_list[4]
    palm_base = landmark_list[17]
    thumb_palm_dist = util.get_distance([thumb_tip, palm_base])
    return thumb_palm_dist < 100  

def move_mouse(index_finger_tip, thumb_folded):
    if index_finger_tip is not None and not thumb_folded:
        x = int(index_finger_tip.x *1.5* screen_width)
        y = int(index_finger_tip.y *2 * screen_height)
        pyautogui.moveTo(x, y)

def is_left_click(landmark_list, thumb_index_dist):
    return (
            util.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and
            util.get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) > 90 and
            thumb_index_dist > 50
    )

def nhan_dien_cu_chi(frame, landmark_list, processed):
    if len(landmark_list) >= 21:
        index_finger_tip, thumb_tip, middle_finger_tip = find_finger_tip(processed)
        thumb_folded = ngon_cai_gap(landmark_list)
        thumb_index_dist = util.get_distance([landmark_list[4], landmark_list[5]])


        hand_label = processed.multi_handedness[0].classification[0].label
        if hand_label == "Left":
            dieu_chinh_am_luong(thumb_tip, index_finger_tip)
            dieu_chinh_man_hinh(thumb_tip, middle_finger_tip)
        
        

        move_mouse(index_finger_tip, thumb_folded)

        # Kiểm tra điều kiện click
        if thumb_folded and is_left_click(landmark_list, thumb_index_dist):
            mouse.press(Button.left)
            mouse.release(Button.left)
            cv2.putText(frame, "Left Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            print("Left Click")
            time.sleep(0.5)

        # Hiển thị thông báo nếu ngón cái bị gập
        if thumb_folded:
            cv2.putText(frame, "Ngon Cai Gap - Dung Chuot", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        


        # Nhận diện cử chỉ vuốt nhanh để Next/Previous
        hand_label = processed.multi_handedness[0].classification[0].label
        swipe_direction =nhan_dien_vuot(index_finger_tip)

        # Nếu phát hiện cử chỉ vuốt, xuất kết quả ra màn hình
        if swipe_direction:
            cv2.putText(frame, swipe_direction, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            if swipe_direction == "next":
                # Tổ hợp phím chuyển tab sang phải (Ctrl + Tab)
                pyautogui.hotkey("ctrl", "tab")
            elif swipe_direction == "previous":
                # Tổ hợp phím chuyển tab sang trái (Ctrl + Shift + Tab)
                pyautogui.hotkey("ctrl", "shift", "tab")
            print(f"{swipe_direction} detected")


def process_frame(frame):
    frame = cv2.flip(frame, 1)
    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    processed = hands.process(frameRGB)

    landmark_list = []
    if processed.multi_hand_landmarks:
        hand_landmarks = processed.multi_hand_landmarks[0]
        mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mpHands.HAND_CONNECTIONS)
        for lm in hand_landmarks.landmark:
            landmark_list.append((lm.x, lm.y))

    emotion = nhandiencamxuc(frame)
    if emotion:
        cv2.putText(frame, f"Emotion: {emotion}", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    nhan_dien_cu_chi(frame, landmark_list, processed)
    return frame


