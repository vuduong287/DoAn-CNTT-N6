# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 08:12:10 2024

@author: efdf
"""
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
# Đọc dữ liệu từ CSV
data = pd.read_csv('fer2013.csv')

# Chuyển đổi chuỗi pixels thành mảng NumPy
def process_data(data):
    pixels = data['pixels'].apply(lambda x: np.array(x.split(), dtype='float32'))
    images = np.stack(pixels.values) / 255.0  # Chia để chuẩn hóa ảnh (từ 0-255 thành 0-1)
    images = images.reshape(-1, 48, 48, 1)  # Định hình lại dữ liệu thành ảnh (48x48x1)
    labels = to_categorical(data['emotion'], num_classes=7)  # Chuyển nhãn thành one-hot encoding
    return images, labels

# Chia dữ liệu thành tập huấn luyện và kiểm tra
images, labels = process_data(data)
X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)

print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)
# Xây dựng mô hình CNN
model = Sequential()

# Thêm lớp Conv2D, MaxPooling, và Dropout
model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(48, 48, 1)))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

# Flatten các đặc trưng và thêm lớp Dense
model.add(Flatten())
model.add(Dense(1024, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(7, activation='softmax'))  # 7 nhãn cảm xúc

# Biên dịch mô hình
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Tóm tắt mô hình
model.summary()
# Huấn luyện mô hình
history = model.fit(X_train, y_train, epochs=25, batch_size=64, validation_data=(X_test, y_test))
# Đánh giá mô hình
test_loss, test_acc = model.evaluate(X_test, y_test)
print(f"Test accuracy: {test_acc}")
# Vẽ đồ thị độ mất mát và độ chính xác trong quá trình huấn luyện
plt.figure(figsize=(12, 6))

# Đồ thị độ chính xác
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Accuracy (train)')
plt.plot(history.history['val_accuracy'], label='Accuracy (val)')
plt.title('Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
# Định nghĩa emotion_dict để ánh xạ nhãn cảm xúc


# Đồ thị độ mất mát
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Loss (train)')
plt.plot(history.history['val_loss'], label='Loss (val)')
plt.title('Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

plt.show()
# Lưu mô hình vào tệp .h5
model.save('emotion_model1.h5')


# Dự đoán cảm xúc
