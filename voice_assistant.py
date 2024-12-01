import os
import speech_recognition as sr
import time
import pygame
import wikipedia
import datetime
import re
import webbrowser
import requests
import urllib
from playsound import playsound
from webdriver_manager.chrome import ChromeDriverManager
from time import strftime
from gtts import gTTS
from youtube_search import YoutubeSearch
import threading
from PIL import ImageGrab
from pynput import mouse, keyboard
import platform
import tkinter as tk
from tkinter import messagebox
import subprocess
from PIL import Image, ImageTk

language = 'vi'
path = ChromeDriverManager().install()
wikipedia.set_lang('vi')
# Biến để theo dõi trạng thái ngủ
is_sleeping = False

sleep_time = 10
  # Thời gian "ngủ" sau 10 giây không nhận giọng nói
def speak(t, app):
    try:
        # Bắt đầu GIF
        app.start_gif()

        # Tạo file âm thanh từ văn bản
        tts = gTTS(t, lang='vi')
        tts.save("speak.mp3")

        with open("chat.txt", "a", encoding="utf-8") as f:
            f.write("Bot:"+t + "\n")
        # Phát âm thanh
        playsound("speak.mp3")

        # Dừng GIF
        app.stop_gif()
        # Xóa file âm thanh
        os.remove("speak.mp3")
    except Exception as e:
        print(f"Lỗi: {e}")
  
def get_voice(timeout=15):
    """
    Capture voice input within a set timeout. Returns 0 if no voice detected.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Me: ", end='')
        
        # Lưu thời gian bắt đầu
        start_time = time.time()
        
        while True:
            # Kiểm tra xem đã hết thời gian chờ chưa
            if time.time() - start_time > timeout:
                print("Đi ngủ sau 15 giây không nhận được giọng nói.")
                return 0  # Trả về 0 khi đã hết thời gian chờ
            
            try:
                # Lắng nghe âm thanh
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                text = r.recognize_google(audio, language="vi-VN")
                print(text)
                
                with open("chat.txt", "a", encoding="utf-8") as f:
                    f.write("Human: " + text + "\n")
                return text
            
            except sr.WaitTimeoutError:
                # Không có đầu vào trong thời gian
                print("... (timeout)")
                continue  # Tiếp tục vòng lặp
            
            except sr.UnknownValueError:
                # Giọng nói không được nhận diện
                print("...")
                with open("chat.txt", "a", encoding="utf-8") as f:
                    f.write("Human: ...\n")  # Ghi "..." vào tệp khi giọng nói không được nhận diện
                continue  # Tiếp tục vòng lặp
            
            except Exception as e:
                print(f"Error: {e}")
                return 0

def stop(app):
      speak("Hẹn gặp lại bạn nhé!",app) 
      app.root.destroy()
      

def sleep(app):
    global is_sleeping
    is_sleeping = True
    speak("Tui đi ngủ. Bạn có thể chạm bàn phím để kêu tui.",app)
    
def wake_up(app):
    global is_sleeping
    if is_sleeping:
        is_sleeping = False
        speak("tui đã thức dậy rùi!",app)

def on_keyboard_activity(key, app):
    # Xử lý khi có hoạt động nhấn phím
    wake_up(app)

# Thêm listener cho các sự kiện chuột và bàn phím
def start_activity_listeners(app):
    # Sử dụng lambda để truyền biến app vào hàm
    keyboard_listener = keyboard.Listener(on_press=lambda key: on_keyboard_activity(key, app))
    keyboard_listener.start()

# Updated get_text function with sleep functionality
def get_text(app):
    global is_sleeping
    start_time = time.time()
    for i in range(3):
        text = get_voice()
        if text:
            return text.lower()  # Reset sleep state if text received
        elif time.time() - start_time > 5:
            # Enter sleep mode after 15 seconds of inactivity
            sleep(app)
            return 0
        else:
            speak("Chat box nghe không nghe rõ, bạn nói lại đi?",app)
    return 0  


def talk(name,app):
    # Danh sách các câu hỏi cần hỏi người dùng
    questions = [
        ("Chào buổi sáng {}. Chúc bạn ngày mới tốt lành!", "Chào buổi chiều {}!", "Chào buổi tối {}!"),
        ("Bạn có khỏe không ?", "có", "khoẻ", "mệt"),
        ("Bạn ăn gì chưa ?", "rồi", "chưa", "ăn rồi"),
        ("Bạn thích làm gì vào thời gian rảnh?", "đọc sách", "xem phim", "chơi thể thao", "ngủ"),
        ("Công việc/học tập của bạn thế nào?", "bận", "rất tốt", "hơi căng thẳng", "không tốt"),
        ("Thời tiết hôm nay thế nào nhỉ? Có quá nóng hay quá lạnh không?", "nóng", "lạnh", "mát mẻ", "dễ chịu")
    ]
    
    while True:
        day_time = int(strftime('%H'))
        # Tùy thuộc vào thời gian trong ngày, chọn câu hỏi thích hợp
        if day_time < 12:
            speak(questions[0][0].format(name),app)  # Buổi sáng
        elif day_time < 18:
            speak(questions[0][1].format(name),app)  # Buổi chiều
        else:
            speak(questions[0][2].format(name),app)  # Buổi tối

        time.sleep(1)

        # Duyệt qua danh sách các câu hỏi và hỏi người dùng
        for question in questions[1:]:
            speak(question[0],app)
            time.sleep(1)
            ans = get_voice()
            if ans:
                # Kiểm tra các lệnh dừng
                if "thôi" in ans or "dừng" in ans:
                    speak("Tạm biệt! Hẹn gặp lại!",app)
                    return  # Dừng hàm khi người dùng nói "thôi" hoặc "dừng"
                
                # Trả lời tự nhiên dựa trên các lựa chọn có sẵn
                if "có" in ans or 'khoẻ' in ans:
                    speak("Thật là tốt! Mình cũng rất vui khi bạn khỏe mạnh!",app)
                elif "mệt" in ans:
                    speak("Ồ, bạn mệt hả? Nghỉ ngơi một chút nhé!",app)
                elif "rồi" in ans or "ăn rồi" in ans:
                    speak("Thật là tốt! Chúc bạn ăn ngon miệng!",app)
                elif "chưa" in ans:
                    speak("Chắc bạn nên ăn gì đó để có sức nhé!",app)
                elif "xem phim" in ans:
                    speak("Ồ, xem phim hay đấy! Bạn thích thể loại phim gì?",app)
                elif "đọc sách" in ans:
                    speak("Đọc sách là một thói quen tuyệt vời! Bạn thích thể loại sách nào?",app)
                elif "chơi thể thao" in ans:
                    speak("Chơi thể thao rất tốt cho sức khỏe! Bạn chơi môn gì?",app)
                elif "ngủ" in ans:
                    speak("Ngủ là rất quan trọng để phục hồi năng lượng. Chúc bạn ngủ ngon nếu bạn cần nghỉ ngơi!",app)
                elif "bận" in ans:
                    speak("Công việc/học tập bận rộn là điều bình thường. Hãy cố gắng thư giãn khi có thể!",app)
                elif "rất tốt" in ans:
                    speak("Thật tuyệt vời! Chúc bạn luôn thành công!",app)
                elif "hơi căng thẳng" in ans:
                    speak("Nếu bạn thấy căng thẳng, hãy nghỉ ngơi một chút. Đôi khi nghỉ ngơi là cách tốt nhất để làm mới bản thân!",app)
                elif "không tốt" in ans:
                    speak("Có vẻ như bạn không vui. Nếu cần, hãy chia sẻ với tôi nhé!",app)
                elif "nóng" in ans:
                    speak("Nóng thì chắc chắn sẽ cảm thấy không thoải mái, hãy uống nhiều nước nhé!",app)
                elif "lạnh" in ans:
                    speak("Lạnh thì cũng phải mặc ấm nhé, đừng để cảm lạnh!",app)
                elif "mát mẻ" in ans:
                    speak("Thời tiết mát mẻ thì thật dễ chịu, đúng không?",app)
                elif "dễ chịu" in ans:
                    speak("Thời tiết dễ chịu thế này là lý tưởng để đi dạo, bạn có ý định đi đâu không?",app)
                else:
                    speak(f"Ồ, bạn nói là {ans}. Thật thú vị!",app)
        
        # Khi hết câu hỏi, kết thúc trò chuyện tự động
        speak("Cảm ơn bạn đã trò chuyện với tôi! Hẹn gặp lại!",app)
        break

def open_website(text,app):
    regex = re.search ('mở (.+)', text)
    if regex:
        domain = regex.group(1)
        url = 'https://www.' + domain
        webbrowser.open(url)
        speak("Trang web của bạn đã được mở lên!",app)
        return True
    else:
        return False
def google_search(text,app):
    # Trích xuất cụm từ tìm kiếm sau từ "kiếm"
    search_for = text.split("kiếm", 1)[1].strip()
    speak("Đang tìm kiếm kết quả cho bạn...",app)

    # Tạo URL tìm kiếm Google
    url = f"https://www.google.com/search?q={urllib.parse.quote(search_for)}"

    # Mở URL tìm kiếm trên trình duyệt mặc định
    webbrowser.open(url)
    speak("Kết quả tìm kiếm của bạn đã được mở trên trình duyệt.",app)
   
def play_youtube(app):
    speak("Xin mời bạn chọn bài hát", app)
    time.sleep(3)
    my_song = get_text(app)
    
    if not my_song or my_song == 0:
        speak("Tôi không nghe rõ tên bài hát. Bạn có thể thử lại không?", app)
        return
    
    try:
        result = YoutubeSearch(my_song, max_results=10).to_dict()
        if result:
            url = 'https://www.youtube.com' + result[0]['url_suffix']
            webbrowser.open(url)
            speak("Bài hát của bạn đã được mở, hãy thưởng thức nó!", app)
        else:
            speak("Tôi không tìm thấy bài hát nào phù hợp. Vui lòng thử lại.", app)
    except Exception as e:
        print(f"Lỗi khi tìm kiếm bài hát: {e}")
        speak("Đã xảy ra lỗi khi mở bài hát. Vui lòng thử lại.", app)
        
def weather(app):
    speak("Bạn muốn xem thời tiết ở đâu ạ!",app)
    time.sleep(3)
    url = "http://api.openweathermap.org/data/2.5/weather?"
    city = get_text(app)
    if not city:
        pass
    api_key = "fe8d8c65cf345889139d8e545f57819a"
    call_url = url + "appid=" + api_key + "&q=" + city + "&units=metric"
    response = requests.get(call_url)
    data = response.json()
    if data["cod"] != "404":
        city_res = data["main"]
        current_temp = city_res["temp"]
        current_pressure = city_res["pressure"]
        current_humidity = city_res["humidity"]
        sun_time  = data["sys"]
        sun_rise = datetime.datetime.fromtimestamp(sun_time["sunrise"])
        sun_set = datetime.datetime.fromtimestamp(sun_time["sunset"])
        wther = data["weather"]
        weather_des = wther[0]["description"]
        now = datetime.datetime.now()
        content = """
        Bot:Hôm nay là ngày {day} tháng {month} năm {year}
        Bot:Mặt trời mọc vào {hourrise} giờ {minrise} phút
        Bot:Mặt trời lặn vào {hourset} giờ {minset} phút
        Bot:Nhiệt độ trung bình là {temp} độ C
        Bot:Áp suất không khí là {pressure} héc tơ Pascal
        Bot:Độ ẩm là {humidity}%
        Bot:Trời hôm nay quang mây. Dự báo mưa rải rác ở một số nơi.""".format(day = now.day, month = now.month, year= now.year, hourrise = sun_rise.hour, minrise = sun_rise.minute,
                                                                           hourset = sun_set.hour, minset = sun_set.minute, 
                                                                           temp = current_temp, pressure = current_pressure, humidity = current_humidity)
        speak(content,app)
        time.sleep(18)
    else:
        speak("Không tìm thấy thành phố!",app)
def open_app_by_voice(app):
    speak("Bạn muốn mở ứng dụng nào?",app)
    voice_input = get_voice()

    if "Chrome" in voice_input:
        speak("Đang mở Google Chrome",app)
        os.startfile("C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Google Chrome.lnk")  # Đường dẫn tới Google Chrome
    elif "Microsoft Word" in voice_input:
        speak("Đang mở Microsoft Word",app)
        os.startfile("C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE")  # Đường dẫn tới Microsoft Word
    elif "Microsoft Excel" in voice_input:
        speak("Đang mở Microsoft Excel",app)
        os.startfile("C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE")  # Đường dẫn tới Microsoft Excel
    elif "Notepad" in voice_input:
        speak("Đang mở Notepad",app)
        os.startfile("notepad.exe")  # Notepad không cần đường dẫn
    else:
        speak("Không tìm thấy ứng dụng yêu cầu. Vui lòng thử lại.")
def validate_alarm_time(alarm_time):
    """
    Validates and parses the alarm time.
    Returns True and parsed time if valid, else False and None.
    """
    try:
        # Check if alarm_time matches HH:MM format
        if re.match(r"^\d{1,2}:\d{2}$", alarm_time):
            # Convert alarm_time to a datetime object to check if it's valid
            parsed_time = datetime.datetime.strptime(alarm_time, "%H:%M").time()
            return True, parsed_time
        else:
            return False, None
    except ValueError:
        return False, None
def set_alarm(alarm_time, app):
    is_valid, parsed_time = validate_alarm_time(alarm_time)
    if not is_valid:
        speak("Thời gian báo thức không hợp lệ. Vui lòng nhập lại theo định dạng HH:MM.", app)
        return  # Thoát hàm nếu thời gian không hợp lệ

    speak(f"Báo thức đã được đặt vào lúc {parsed_time.strftime('%H:%M')}.", app)

    while not app.alarm_triggered.is_set():
        current_time = datetime.datetime.now().time()
        if current_time.hour == parsed_time.hour and current_time.minute == parsed_time.minute:
            speak("Dậy thôi, đến giờ rồi!", app)
            play_sound("baothuc.mp3")  # Phát âm thanh báo thức
            break
        time.sleep(30)  # Kiểm tra mỗi 30 giây
    
pygame.mixer.init()    
def play_sound(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1) 
def shutdown_computer():
    if platform.system() == "Windows":
        os.system("shutdown /s /t 1")  # Tắt máy tính ngay lập tức
    else:
        print("Hệ điều hành không được hỗ trợ.")    
def call_sen(app):
    global is_sleeping
    speak("Xin chào, bạn tên là gì nhỉ?",app)
    name = get_text(app)
    if name:
        speak(f"Chào bạn {name}",app)
        time.sleep(0.5)
        speak("Bạn cần Sen giúp gì ạ!",app)
        time.sleep(0.5)

        start_activity_listeners(app)

        while True:
            if not is_sleeping:
                text = get_text(app)
                if not text:
                    continue  # Retry if no input detected
                # Commands and functionalities
                if "dừng" in text or "stop" in text:
                    stop(app)
                    break
                elif "trò chuyện" in text or "nói chuyện" in text:
                    talk(name,app)
                elif "mở" in text:
                    if "mở google và tìm kiếm" in text:
                        google_search(text,app)
                    elif "." in text:
                        open_website(text,app)
                    elif "mở ứng dụng" in text:
                        open_app_by_voice(app)
                elif "chơi nhạc" in text:
                    play_youtube(app)
                elif "thời tiết" in text:
                    weather(app)
                elif "tắt máy" in text:
                    speak("Bạn có chắc muốn tắt máy chứ?", app)
                    text1 = get_text(app)  
                    if isinstance(text1, int):
                        text1 = str(text1) 
                    if "có" in text1.lower() or "chắc" in text1:  
                        shutdown_computer()
                    else:
                        speak("Đã hủy lệnh tắt máy.", app)             
                elif "báo thức" in text:
                    speak("Bạn muốn đặt báo thức vào lúc nào?",app)
  
                    while True:
                        alarm_time = get_text(app)
                        is_valid, _ = validate_alarm_time(alarm_time)
                        if is_valid:
                            threading.Thread(target=set_alarm, args=(alarm_time,app)).start()
                            speak("Báo thức của bạn đã được đặt.",app)
                            break
                        else:
                            speak("Thời gian không hợp lệ. Vui lòng nhập lại theo định dạng HH:MM.",app)   
                elif "chụp màn hình" in text:
                    capture_screen(app)
            else:
                time.sleep(0.5)


def capture_screen(app):
    # Define the path for the screenshot folder
    folder_path = "screenshots"
    
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Capture the screen
    screenshot = ImageGrab.grab()
    
    # Get the current date and time for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Define the filename and full path
    filename = f"screenshot_{timestamp}.png"
    file_path = os.path.join(folder_path, filename)
    
    # Save the screenshot
    screenshot.save(file_path)
    
    # Notify the user
    print(f"Screenshot saved as {file_path}")
    speak("Ảnh chụp màn hình đã được lưu",app)  




