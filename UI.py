import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk
import os
import threading
import cv2
from voice_assistant import call_sen  # Giả sử bạn đã có hàm này
from gesture_control import process_frame
os.environ['PYTHONIOENCODING'] = 'utf-8'
# Thiết lập giao diện tối
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class ChatbotUI:
    def __init__(self, parent):
        self.parent = parent

        # Tạo cửa sổ chat
        self.assistant_frame = ctk.CTkFrame(parent,width=600, height=800)
        self.assistant_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")  # Hàng 0

        # Load icons
        try:
            self.bot_icon = ctk.CTkImage(
                light_image=Image.open("./image/bot.png"),
                dark_image=Image.open("./image/bot.png"),
                size=(30, 30)
            )
            self.human_icon = ctk.CTkImage(
                light_image=Image.open("./image/human.png"),
                dark_image=Image.open("./image/human.png"),
                size=(30, 30)
            )
        except FileNotFoundError:
            print("Không tìm thấy file ảnh icon! Hãy đảm bảo có bot.png và human.png trong thư mục")
            self.bot_icon = None
            self.human_icon = None
        
        # Đảm bảo khởi tạo self.chat_frame là một frame của ctk
        self.chat_frame = ctk.CTkScrollableFrame(self.assistant_frame)  # Khởi tạo chat_frame với CTkScrollableFrame
        self.chat_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        # Lưu trữ các tin nhắn
        self.messages = []
        self.displayed_messages = set()
        self.last_modified_time = 0

        # Đọc và hiển thị tin nhắn từ file
        self.load_messages()

        # Kiểm tra cập nhật file
        self.check_for_updates()

    def calculate_text_height(self, text, width):
        """Tính toán chiều cao cần thiết cho text dựa trên độ rộng cho trước."""
        font = tk.font.Font(family="TkDefaultFont", size=10)
        lines = text.split("\n")
        
        # Tính số dòng và chiều cao cần thiết
        line_count = sum((font.measure(line) // width) + 1 for line in lines)
        height = line_count * font.metrics("linespace") + 20  # Thêm một chút không gian cho padding

        return height

    def create_chat_bubble(self, container, text, is_bot):
        """Tạo bong bóng chat."""
        width = 400
        height = self.calculate_text_height(text, width // 8)

        bubble_frame = ctk.CTkFrame(
            container,
            fg_color="#2B2B2B" if is_bot else "#1A4B8C",
            corner_radius=10,
            width=width,
            height=height
        )

        text_label = ctk.CTkLabel(
            bubble_frame,
            text=text,
            wraplength=width - 20,
            justify="left",
            anchor="w"
        )
        text_label.pack(padx=10, pady=10, fill="both", expand=True)

        return bubble_frame

    def create_message_bubble(self, text, is_bot=True):
        """Tạo frame cho từng tin nhắn."""
        msg_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        msg_frame.pack(fill="x", padx=10, pady=5)

        container = ctk.CTkFrame(msg_frame, fg_color="transparent")
        container.pack(side="left" if is_bot else "right")

        if is_bot:
            # Bot message: icon trước, text sau
            if self.bot_icon:
                icon_label = ctk.CTkLabel(
                    container,
                    text="",
                    image=self.bot_icon
                )
                icon_label.pack(side="left")
            
            bubble = self.create_chat_bubble(container, text, is_bot)
            bubble.pack(side="right", padx=(5, 0))
        else:
            # Human message: text trước, icon sau
            bubble = self.create_chat_bubble(container, text, is_bot)
            bubble.pack(side="left", padx=(0, 5))
            
            if self.human_icon:
                icon_label = ctk.CTkLabel(
                    container,
                    text="",
                    image=self.human_icon
                )
                icon_label.pack(side="right")

        self.messages.append((msg_frame, text))

        # Sau khi tin nhắn được thêm, cuộn xuống dưới cùng
        self.chat_frame._parent_canvas.yview_moveto(1.0)    


    def clear_chat(self):
        """Xóa tất cả tin nhắn."""
        for msg_frame, _ in self.messages:
            msg_frame.destroy()
        self.messages = []
        self.displayed_messages.clear()

    def load_messages(self):
        """Đọc tin nhắn từ file."""
        try:
            with open("chat.txt", "r", encoding="utf-8") as file:
                messages = []
                for line in file:
                    line = line.strip()
                    if line:
                        messages.append(line)

                # Kiểm tra tin nhắn mới
                new_messages = set(messages) - self.displayed_messages
                if new_messages:
                    self.clear_chat()
                    for message in messages:
                        is_bot = message.startswith("Bot:")
                        text = message[4:].strip() if is_bot else message[6:].strip()
                        self.create_message_bubble(text, is_bot)
                        self.displayed_messages.add(message)
        except FileNotFoundError:
            if not self.messages:
                self.create_message_bubble("Không tìm thấy file chat.txt", is_bot=True)

    def check_for_updates(self):
        """Kiểm tra và cập nhật tin nhắn mới."""
        try:
            current_modified_time = os.path.getmtime("chat.txt")
            if current_modified_time > self.last_modified_time:
                self.last_modified_time = current_modified_time
                self.load_messages()
        except FileNotFoundError:
            pass

        self.parent.after(1000, self.check_for_updates)


class AssistantApp:
    def __init__(self, parent):
        self.parent = parent
        self.alarm_triggered = threading.Event()
        # Frame chính cho trợ lý ảo (phần trên)
        self.assistant_frame = ctk.CTkFrame(parent)
        self.assistant_frame.grid(row=0, column=0, sticky="nsew")  # Hàng 0

        # Load GIF
        try:
            self.gif = Image.open("./image/ai.gif")
            self.frames = self.load_gif_frames(self.gif)
            self.gif_label = tk.Label(self.assistant_frame, width=750, height=300)  # Chỉnh lại từ gif_frame thành assistant_frame
            self.gif_label.pack()
        except FileNotFoundError:
            print("Không tìm thấy file ai.gif")
            self.frames = []

        # Trạng thái GIF
        self.playing_gif = False
        self.frame_index = 0
        self.animate()
        
    def load_gif_frames(self, gif):
        """Tải frame GIF."""
        frames = []
        try:
            while True:
                frame = ImageTk.PhotoImage(gif.copy())
                frames.append(frame)
                gif.seek(len(frames))
        except EOFError:
            pass
        return frames

    def animate(self):
        """Thread-safe animation."""
        if self.frames and self.playing_gif:
            frame = self.frames[self.frame_index]
            self.gif_label.config(image=frame)
            self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.parent.after(100, self.animate)

    def start_gif(self):
        self.playing_gif = True

    def stop_gif(self):
        self.playing_gif = False


class CameraUI:
    def __init__(self, parent):
        self.parent = parent

        # Tạo frame chứa video
        self.camera_frame = ctk.CTkFrame(parent)
        self.camera_frame.grid(row=1, column=0, sticky="nsew")

        # Tạo label để hiển thị video
        # Tạo label để hiển thị video
        self.label = ctk.CTkLabel(self.camera_frame, width=750, height=500)  # Kích thước lớn hơn
        self.label.pack(padx=10, pady=10)  # Căn giữa và mở rộng ra cả hai chiều # Tạo label và căn giữa nó

        # Mở camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Không thể mở camera")

        # Cập nhật hình ảnh video
        self.update_video()


    def update_video(self):
        def show_frames():
            ret, frame = self.cap.read()
            if ret:
                # Resize frame để khớp với kích thước của label
                frame = cv2.resize(frame, (self.label.winfo_width(), self.label.winfo_height()))
                processed_frame = process_frame(frame)  # hàm xử lý của bạn
                cv2image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.label.imgtk = imgtk  # Gắn hình ảnh mới vào label
                self.label.configure(image=imgtk)
            self.parent.after(10, show_frames)  # Cập nhật lại sau 10ms

        show_frames()

    def start_gesture_recognition(self):
        threading.Thread(target=self.update_video, daemon=True).start()
        
        


class MainApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Trợ lý ảo tích hợp")
        self.window.geometry("1400x700")

        self.window.grid_rowconfigure(0, weight=1)  # Giới hạn ô (0, 0)
        self.window.grid_rowconfigure(1, weight=1)  # Giới hạn ô (1, 0)
        self.window.grid_columnconfigure(0, weight=1)  # Giới hạn cột (0)
        self.window.grid_columnconfigure(1, weight=1)  # Giới hạn cột (1)
        # Tạo giao diện Chatbot và Assistant
        self.camera_ui = CameraUI(self.window)
        self.chatbot_ui = ChatbotUI(self.window)
        self.assistant_ui = AssistantApp(self.window)
        

        # Chạy trợ lý ảo
        threading.Thread(target=lambda: call_sen(self.assistant_ui), daemon=True).start()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def run(self):
        self.window.mainloop()
    
    def on_close(self):
        """Hàm xử lý khi đóng cửa sổ."""
        try:
            with open("chat.txt", "w", encoding="utf-8") as file:
                file.truncate(0)  # Xóa nội dung tệp
        except FileNotFoundError:
            pass
        finally:
            self.window.destroy()  # Đóng cửa sổ chính


if __name__ == "__main__":
    app = MainApp()
    app.run()
