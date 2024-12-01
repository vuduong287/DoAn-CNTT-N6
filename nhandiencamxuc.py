import cv2
import numpy as np
from tensorflow.keras.models import load_model
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Tải mô hình đã huấn luyện
emotion_model = load_model('emotion_model.h5')

# Tạo từ điển để ánh xạ nhãn dự đoán với tên cảm xúc
emotion_dict = {0: "Angry", 1: "Disgust", 2: "Fear", 3: "Happy", 4: "Sad", 5: "Surprise" ,6: "Neutral"}

# Tải bộ phân loại khuôn mặt của OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Hàm nhận diện cảm xúc từ một ảnh đầu vào
def nhandiencamxuc(frame):
    gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        roi_gray = gray_img[y:y+h, x:x+w]
        roi_gray = cv2.resize(roi_gray, (48, 48))
        roi_gray = roi_gray / 255.0
        roi_gray = np.expand_dims(roi_gray, axis=0)
        roi_gray = np.expand_dims(roi_gray, axis=-1)

        # Dự đoán cảm xúc
        prediction = emotion_model.predict(roi_gray)
        emotion_label = np.argmax(prediction)
        return emotion_dict[emotion_label]

    return None  # Nếu không phát hiện khuôn mặt
