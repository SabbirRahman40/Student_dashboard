import json
import os
import random
import shutil
import copy
from datetime import datetime
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.resources import resource_find
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.animation import Animation

# The packaged JSON is read-only on Android. Runtime changes must be saved in
# App.user_data_dir, which is writable and persists between app launches.
DATA_FILE_NAME = "student_data.json"


def get_data_file():
    app = App.get_running_app()
    if app is not None:
        return os.path.join(app.user_data_dir, DATA_FILE_NAME)
    # Fallback for running this file directly in a desktop Python environment.
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE_NAME)


DEFAULT_DATA = {
    "users": {},
    "routine": [
        {"id": 1, "day": "Saturday", "time": "1:10-2:10 PM", "subject": "CSE 2391 - Data Structures", "room": "1004", "reminder_min": 30, "reminder_on": True},
        {"id": 2, "day": "Saturday", "time": "2:15-3:15 PM", "subject": "ENG 2203 - Advanced English", "room": "924", "reminder_min": 30, "reminder_on": True},
        {"id": 3, "day": "Sunday", "time": "10:40-11:40 AM", "subject": "EEN 2103 - Circuit Analysis I", "room": "504", "reminder_min": 30, "reminder_on": True},
        {"id": 4, "day": "Sunday", "time": "1:10-2:10 PM", "subject": "CSE 2391 - Data Structures", "room": "1004", "reminder_min": 30, "reminder_on": True},
        {"id": 5, "day": "Sunday", "time": "2:15-3:15 PM", "subject": "ENG 2203 - Advanced English", "room": "924", "reminder_min": 30, "reminder_on": True},
        {"id": 6, "day": "Monday", "time": "8:30-9:30 AM", "subject": "ACC 1305 - Accounting", "room": "501", "reminder_min": 30, "reminder_on": True},
        {"id": 7, "day": "Monday", "time": "10:40-11:40 AM", "subject": "EEN 2103 - Circuit Analysis I", "room": "607", "reminder_min": 30, "reminder_on": True},
        {"id": 8, "day": "Monday", "time": "11:45-12:45 PM", "subject": "EEN 2103 - Circuit Analysis I", "room": "607", "reminder_min": 30, "reminder_on": True},
        {"id": 9, "day": "Monday", "time": "1:10-2:10 PM", "subject": "CSE 2391 - Data Structures", "room": "1004", "reminder_min": 30, "reminder_on": True},
        {"id": 10, "day": "Tuesday", "time": "8:30-9:30 AM", "subject": "ACC 1305 - Accounting", "room": "503", "reminder_min": 30, "reminder_on": True},
        {"id": 11, "day": "Tuesday", "time": "2:15-3:15 PM", "subject": "ENG 2203 - Advanced English", "room": "924", "reminder_min": 30, "reminder_on": True},
        {"id": 12, "day": "Wednesday", "time": "8:30-9:30 AM", "subject": "ACC 1305 - Accounting", "room": "310", "reminder_min": 30, "reminder_on": True},
        {"id": 13, "day": "Wednesday", "time": "10:40-11:40 AM", "subject": "EEN 2104 - Circuit Lab", "room": "EEE lab-01", "reminder_min": 30, "reminder_on": True},
        {"id": 14, "day": "Wednesday", "time": "11:45-12:45 PM", "subject": "EEN 2104 - Circuit Lab", "room": "EEE lab-01", "reminder_min": 30, "reminder_on": True},
        {"id": 15, "day": "Wednesday", "time": "1:10-2:10 PM", "subject": "CSE 2392 - Data Structures Lab", "room": "Com lab-08", "reminder_min": 30, "reminder_on": True},
        {"id": 16, "day": "Wednesday", "time": "2:15-3:15 PM", "subject": "CSE 2392 - Data Structures Lab", "room": "Com lab-08", "reminder_min": 30, "reminder_on": True}
    ],
    "exams": [],
    "tasks": [],
    "albums": {}
}

def _normalize_data(data):
    """Fill missing data sections and normalize legacy user records."""
    if not isinstance(data, dict):
        data = {}
    normalized = copy.deepcopy(DEFAULT_DATA)
    normalized.update(data)

    if not isinstance(normalized.get("users"), dict):
        normalized["users"] = {}
    for username, user in list(normalized["users"].items()):
        if isinstance(user, str):
            normalized["users"][username] = {
                "password": user,
                "phone": "",
            }
        elif isinstance(user, dict):
            user.setdefault("password", "")
            user.setdefault("phone", "")
        else:
            normalized["users"].pop(username, None)

    for key in ("routine", "exams", "tasks"):
        if not isinstance(normalized.get(key), list):
            normalized[key] = []
    if not isinstance(normalized.get("albums"), dict):
        normalized["albums"] = {}
    return normalized


def load_data():
    data_path = get_data_file()
    if not os.path.exists(data_path):
        # On first Android launch, seed the writable file from the bundled JSON.
        bundled_path = resource_find(DATA_FILE_NAME)
        if not bundled_path:
            bundled_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), DATA_FILE_NAME
            )
        if bundled_path and os.path.isfile(bundled_path):
            try:
                os.makedirs(os.path.dirname(data_path), exist_ok=True)
                shutil.copyfile(bundled_path, data_path)
            except OSError:
                pass

    if os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = _normalize_data(json.load(f))
            return data
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            # Keep the app usable if the saved file is damaged; replace it below.
            pass

    data = _normalize_data(DEFAULT_DATA)
    save_data(data)
    return data


def save_data(data):
    data_path = get_data_file()
    data_dir = os.path.dirname(data_path)
    os.makedirs(data_dir, exist_ok=True)
    temp_path = data_path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    os.replace(temp_path, data_path)

class CardBox(BoxLayout):
    def __init__(self, bg_color=(0.88, 0.93, 0.98, 1), **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.padding = dp(10)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(75)
        
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

# Perfectly Centered Auth Card with Modern Square/Rounded Look
class AuthCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(25)
        self.spacing = dp(12)
        self.size_hint = (None, None)
        self.width = dp(380)
        self.height = dp(520)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        with self.canvas.before:
            Color(1, 1, 1, 0.97) # Clean White Card
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[20])
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

class AsmaniButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.1, 0.55, 0.85, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = '15sp'
        self.bold = True
        self.size_hint_y = None
        self.height = dp(45)

class AccentButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.15, 0.7, 0.5, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = '14sp'
        self.size_hint_y = None
        self.height = dp(40)

class StudentApp(App):
    def build(self):
        self.title = "Sabbir's Smart Student Dashboard"
        self.data = load_data()
        self.current_user = None
        self.dark_mode = False
        self.routine_view_mode = "today"
        
        self.temp_reg_data = {}
        self.temp_forgot_data = {}
        
        # A fixed Window.size is useful on desktop but should not be forced on Android.
        if not hasattr(self, "_android_window_configured") and "ANDROID_ARGUMENT" not in os.environ:
            Window.size = (450, 720)
        self.root_layout = FloatLayout() # FloatLayout ensures absolute centering
        
        with self.root_layout.canvas.before:
            self.bg_color_inst = Color(0.72, 0.88, 0.98, 1) # Rich Asmani Background
            self.bg_rect = Rectangle(size=(1000, 1000), pos=(0, 0))
        self.root_layout.bind(size=self._update_bg, pos=self._update_bg)

        self.show_login_screen()
        return self.root_layout

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def clear(self):
        self.root_layout.clear_widgets()

    def animate_pop_in(self, widget):
        # Kivy widgets do not have a built-in `scale` property. Fade the card in
        # without assigning an unsupported attribute (which caused a crash).
        widget.opacity = 0
        Animation(opacity=1, duration=0.35, t="out_back").start(widget)

    def show_login_screen(self):
        self.clear()
        card = AuthCard()
        self.animate_pop_in(card)
        
        title = Label(text="🎓 Sabbir's Portal", font_size="24sp", bold=True, color=(0.1, 0.4, 0.7, 1), size_hint_y=None, height=dp(45))
        card.add_widget(title)
        
        self.username_input = TextInput(hint_text="Username", multiline=False, size_hint_y=None, height=dp(45))
        self.password_input = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height=dp(45))
        self.msg_label = Label(text="", color=(0.9, 0.2, 0.2, 1), size_hint_y=None, height=dp(25))
        
        card.add_widget(self.username_input)
        card.add_widget(self.password_input)
        card.add_widget(self.msg_label)
        
        btn_login = AsmaniButton(text="🚀 Login")
        btn_login.bind(on_press=self.handle_login)
        card.add_widget(btn_login)
        
        btn_reg = AccentButton(text="✨ Create New Account")
        btn_reg.bind(on_press=lambda x: self.show_register_screen())
        card.add_widget(btn_reg)
        
        btn_forgot = Button(text="🔑 Forgot Password?", background_color=(0,0,0,0), color=(0.1, 0.4, 0.8, 1), size_hint_y=None, height=dp(35))
        btn_forgot.bind(on_press=lambda x: self.show_forgot_screen())
        card.add_widget(btn_forgot)
        
        self.root_layout.add_widget(card)

    def show_register_screen(self):
        self.clear()
        card = AuthCard()
        self.animate_pop_in(card)
        
        title = Label(text="📝 Register Account", font_size="22sp", bold=True, color=(0.1, 0.4, 0.7, 1), size_hint_y=None, height=dp(40))
        card.add_widget(title)
        
        self.reg_user = TextInput(hint_text="Choose Username", multiline=False, size_hint_y=None, height=dp(42))
        self.reg_phone = TextInput(hint_text="Mobile Number (e.g. 017XXXXXXXX)", multiline=False, size_hint_y=None, height=dp(42))
        self.reg_pass = TextInput(hint_text="Choose Password", password=True, multiline=False, size_hint_y=None, height=dp(42))
        self.reg_cpass = TextInput(hint_text="Confirm Password", password=True, multiline=False, size_hint_y=None, height=dp(42))
        self.reg_msg = Label(text="", color=(0.9, 0.2, 0.2, 1), size_hint_y=None, height=dp(25))
        
        card.add_widget(self.reg_user)
        card.add_widget(self.reg_phone)
        card.add_widget(self.reg_pass)
        card.add_widget(self.reg_cpass)
        card.add_widget(self.reg_msg)
        
        btn_send_otp = AsmaniButton(text="📤 Send Verification Code")
        btn_send_otp.bind(on_press=self.send_reg_otp)
        card.add_widget(btn_send_otp)
        
        btn_back = AccentButton(text="🔙 Back to Login")
        btn_back.bind(on_press=lambda x: self.show_login_screen())
        card.add_widget(btn_back)
        
        self.root_layout.add_widget(card)

    def send_reg_otp(self, instance):
        u = self.reg_user.text.strip()
        ph = self.reg_phone.text.strip()
        p = self.reg_pass.text
        cp = self.reg_cpass.text
        
        if not u or not ph or not p:
            self.reg_msg.text = "⚠️ All fields are required!"
            return
        if u in self.data["users"]:
            self.reg_msg.text = "⚠️ Username already exists!"
            return
        if p != cp:
            self.reg_msg.text = "⚠️ Passwords don't match!"
            return
            
        otp = str(random.randint(1000, 9999))
        self.temp_reg_data = {"username": u, "phone": ph, "password": p, "otp": otp}
        
        print(f"\n================================")
        print(f"[SMS OTP] Your Reg Code is: {otp}")
        print(f"================================\n")
        
        self.show_verify_reg_screen()

    def show_verify_reg_screen(self):
        self.clear()
        card = AuthCard()
        self.animate_pop_in(card)
        
        title = Label(text="🔒 Verify Phone Number", font_size="22sp", bold=True, color=(0.1, 0.4, 0.7, 1), size_hint_y=None, height=dp(45))
        card.add_widget(title)
        
        info_lbl = Label(text=f"Code sent to terminal for:\n{self.temp_reg_data.get('phone')}", font_size="13sp", color=(0.3, 0.3, 0.3, 1), size_hint_y=None, height=dp(45), halign='center')
        card.add_widget(info_lbl)
        
        self.otp_input = TextInput(hint_text="Enter 4-digit Code", multiline=False, size_hint_y=None, height=dp(45))
        self.verify_msg = Label(text="", color=(0.9, 0.2, 0.2, 1), size_hint_y=None, height=dp(25))
        
        card.add_widget(self.otp_input)
        card.add_widget(self.verify_msg)
        
        btn_confirm = AsmaniButton(text="✅ Confirm & Register")
        btn_confirm.bind(on_press=self.confirm_reg_otp)
        card.add_widget(btn_confirm)
        
        btn_back = AccentButton(text="🔙 Back")
        btn_back.bind(on_press=lambda x: self.show_register_screen())
        card.add_widget(btn_back)
        
        self.root_layout.add_widget(card)

    def confirm_reg_otp(self, instance):
        entered_otp = self.otp_input.text.strip()
        if entered_otp == self.temp_reg_data.get("otp"):
            u = self.temp_reg_data["username"]
            p = self.temp_reg_data["password"]
            ph = self.temp_reg_data["phone"]
            
            self.data["users"][u] = {"password": p, "phone": ph}
            save_data(self.data)
            self.show_login_screen()
        else:
            self.verify_msg.text = "❌ Incorrect Verification Code!"

    def show_forgot_screen(self):
        self.clear()
        card = AuthCard()
        self.animate_pop_in(card)
        
        title = Label(text="🔑 Reset Password", font_size="22sp", bold=True, color=(0.1, 0.4, 0.7, 1), size_hint_y=None, height=dp(45))
        card.add_widget(title)
        
        self.f_user = TextInput(hint_text="Enter Username", multiline=False, size_hint_y=None, height=dp(42))
        self.f_phone = TextInput(hint_text="Enter Registered Phone No", multiline=False, size_hint_y=None, height=dp(42))
        self.f_pass = TextInput(hint_text="New Password", password=True, multiline=False, size_hint_y=None, height=dp(42))
        self.f_msg = Label(text="", color=(0.9, 0.2, 0.2, 1), size_hint_y=None, height=dp(25))
        
        card.add_widget(self.f_user)
        card.add_widget(self.f_phone)
        card.add_widget(self.f_pass)
        card.add_widget(self.f_msg)
        
        btn_send_otp = AsmaniButton(text="📤 Send Reset Code")
        btn_send_otp.bind(on_press=self.send_forgot_otp)
        card.add_widget(btn_send_otp)
        
        btn_back = AccentButton(text="🔙 Back to Login")
        btn_back.bind(on_press=lambda x: self.show_login_screen())
        card.add_widget(btn_back)
        
        self.root_layout.add_widget(card)

    def send_forgot_otp(self, instance):
        u = self.f_user.text.strip()
        ph = self.f_phone.text.strip()
        p = self.f_pass.text
        
        if not u or not ph or not p:
            self.f_msg.text = "⚠️ All fields are required!"
            return
        if u not in self.data["users"] or self.data["users"][u]["phone"] != ph:
            self.f_msg.text = "❌ Username or Phone doesn't match!"
            return
            
        otp = str(random.randint(1000, 9999))
        self.temp_forgot_data = {"username": u, "password": p, "otp": otp}
        
        print(f"\n================================")
        print(f"[SMS OTP] Your Reset Code is: {otp}")
        print(f"================================\n")
        
        self.show_verify_forgot_screen()

    def show_verify_forgot_screen(self):
        self.clear()
        card = AuthCard()
        self.animate_pop_in(card)
        
        title = Label(text="🔒 Verify Reset Code", font_size="22sp", bold=True, color=(0.1, 0.4, 0.7, 1), size_hint_y=None, height=dp(45))
        card.add_widget(title)
        
        self.f_otp_input = TextInput(hint_text="Enter 4-digit Code", multiline=False, size_hint_y=None, height=dp(45))
        self.f_verify_msg = Label(text="", color=(0.9, 0.2, 0.2, 1), size_hint_y=None, height=dp(25))
        
        card.add_widget(self.f_otp_input)
        card.add_widget(self.f_verify_msg)
        
        btn_confirm = AsmaniButton(text="✅ Confirm New Password")
        btn_confirm.bind(on_press=self.confirm_forgot_otp)
        card.add_widget(btn_confirm)
        
        btn_back = AccentButton(text="🔙 Back")
        btn_back.bind(on_press=lambda x: self.show_forgot_screen())
        card.add_widget(btn_back)
        
        self.root_layout.add_widget(card)

    def confirm_forgot_otp(self, instance):
        entered_otp = self.f_otp_input.text.strip()
        if entered_otp == self.temp_forgot_data.get("otp"):
            u = self.temp_forgot_data["username"]
            p = self.temp_forgot_data["password"]
            
            self.data["users"][u]["password"] = p
            save_data(self.data)
            self.show_login_screen()
        else:
            self.f_verify_msg.text = "❌ Incorrect Verification Code!"

    def handle_login(self, instance):
        u = self.username_input.text.strip()
        p = self.password_input.text
        if u in self.data["users"] and self.data["users"][u]["password"] == p:
            self.current_user = u
            self.show_dashboard()
        else:
            self.msg_label.text = "❌ Invalid username or password!"

    def show_dashboard(self):
        self.clear()
        
        # Switch root layout to BoxLayout for dashboard contents
        dash_layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        
        top_layout = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        top_layout.add_widget(Label(text=f"👋 Welcome, {self.current_user}!", font_size="15sp", bold=True, color=(0.1, 0.3, 0.5, 1)))
        
        btn_logout = Button(text="🚪 Logout", size_hint_x=None, width=dp(75), background_color=(0.8, 0.2, 0.2, 1))
        btn_logout.bind(on_press=lambda x: self.show_login_screen())
        top_layout.add_widget(btn_logout)
        
        dash_layout.add_widget(top_layout)
        
        nav_layout = GridLayout(cols=4, size_hint_y=None, height=dp(42), spacing=dp(4))
        
        btn_routine = AsmaniButton(text="📅 Edit Routine")
        btn_routine.bind(on_press=lambda x: self.show_routine_screen())
        nav_layout.add_widget(btn_routine)
        
        btn_exams = AsmaniButton(text="📝 Exams")
        btn_exams.bind(on_press=lambda x: self.show_exam_screen())
        nav_layout.add_widget(btn_exams)
        
        btn_tasks = AsmaniButton(text="📌 Tasks")
        btn_tasks.bind(on_press=lambda x: self.show_task_screen())
        nav_layout.add_widget(btn_tasks)
        
        btn_albums = AsmaniButton(text="🖼️ Albums")
        btn_albums.bind(on_press=lambda x: self.show_album_screen())
        nav_layout.add_widget(btn_albums)
        
        dash_layout.add_widget(nav_layout)
        
        toggle_layout = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(5))
        btn_today = Button(text="📅 Today's Routine", background_color=(0.1, 0.6, 0.4, 1) if self.routine_view_mode=="today" else (0.4, 0.4, 0.4, 1))
        btn_today.bind(on_press=lambda x: self.set_routine_view("today"))
        toggle_layout.add_widget(btn_today)
        
        btn_all = Button(text="📚 All Routine", background_color=(0.1, 0.6, 0.4, 1) if self.routine_view_mode=="all" else (0.4, 0.4, 0.4, 1))
        btn_all.bind(on_press=lambda x: self.set_routine_view("all"))
        toggle_layout.add_widget(btn_all)
        dash_layout.add_widget(toggle_layout)
        
        current_day_name = datetime.now().strftime("%A")
        header_text = f"🔥 Routine for Today ({current_day_name}):" if self.routine_view_mode=="today" else "📚 Complete Weekly Routine:"
        dash_layout.add_widget(Label(text=header_text, font_size="14sp", bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(28)))
        
        scroll = ScrollView()
        routine_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6), padding=dp(2))
        routine_layout.bind(minimum_height=routine_layout.setter('height'))
        
        filtered_routine = self.data["routine"]
        if self.routine_view_mode == "today":
            filtered_routine = [item for item in self.data["routine"] if item['day'].lower() == current_day_name.lower()]
        
        if not filtered_routine:
            routine_layout.add_widget(Label(text="No classes scheduled for today!", font_size="13sp", color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(40)))
        else:
            for item in filtered_routine:
                card = CardBox(bg_color=(0.88, 0.93, 0.98, 1))
                rem_status = f"🔔 {item.get('reminder_min', 30)}m" if item.get('reminder_on', True) else "🔕 Off"
                txt = f"[b]{item['day']}[/b] | {item['time']}\n[color=224466]{item['subject']}[/color]\nRoom: {item['room']} | {rem_status}"
                lbl = Label(text=txt, markup=True, font_size="12sp", color=(0.15, 0.15, 0.15, 1), halign='left', valign='middle')
                lbl.bind(size=lbl.setter('text_size'))
                card.add_widget(lbl)
                routine_layout.add_widget(card)
            
        scroll.add_widget(routine_layout)
        dash_layout.add_widget(scroll)
        
        self.root_layout.add_widget(dash_layout)

    def set_routine_view(self, mode):
        self.routine_view_mode = mode
        self.show_dashboard()

    def show_routine_screen(self):
        self.clear()
        screen = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        screen.add_widget(Label(text="📅 Manage Class Routine & Reminders", font_size="18sp", bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(35)))
        
        self.r_day = TextInput(hint_text="Day (Saturday / Sunday / ...)", multiline=False, size_hint_y=None, height=dp(36))
        self.r_time = TextInput(hint_text="Time (e.g. 1:10-2:10 PM)", multiline=False, size_hint_y=None, height=dp(36))
        self.r_sub = TextInput(hint_text="Subject Name", multiline=False, size_hint_y=None, height=dp(36))
        self.r_room = TextInput(hint_text="Room No", multiline=False, size_hint_y=None, height=dp(36))
        self.r_rem = TextInput(hint_text="Reminder Mins (e.g. 30)", multiline=False, size_hint_y=None, height=dp(36))
        
        for widget in [self.r_day, self.r_time, self.r_sub, self.r_room, self.r_rem]:
            screen.add_widget(widget)
            
        btn_add = AsmaniButton(text="➕ Add Class")
        btn_add.bind(on_press=self.add_class)
        screen.add_widget(btn_add)
        
        scroll = ScrollView()
        list_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=dp(2))
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for index, item in enumerate(self.data["routine"]):
            card = CardBox(bg_color=(0.88, 0.93, 0.98, 1))
            status_text = "ON" if item.get('reminder_on', True) else "OFF"
            txt = f"[b]{item['day']} ({item['time']})[/b]\n{item['subject']} | Remind: {item.get('reminder_min', 30)}m [{status_text}]"
            lbl = Label(text=txt, markup=True, font_size="11sp", color=(0.15, 0.15, 0.15, 1), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            card.add_widget(lbl)
            
            btn_toggle = Button(text="Toggle", size_hint_x=None, width=dp(60), background_color=(0.2, 0.6, 0.8, 1))
            btn_toggle.bind(on_press=lambda inst, idx=index: self.toggle_reminder(idx))
            card.add_widget(btn_toggle)
            
            btn_del = Button(text="Delete", size_hint_x=None, width=dp(60), background_color=(0.9, 0.2, 0.2, 1))
            btn_del.bind(on_press=lambda inst, idx=index: self.delete_class(idx))
            card.add_widget(btn_del)
            
            list_layout.add_widget(card)
            
        scroll.add_widget(list_layout)
        screen.add_widget(scroll)
        
        btn_back = AccentButton(text="🔙 Back to Dashboard")
        btn_back.bind(on_press=lambda x: self.show_dashboard())
        screen.add_widget(btn_back)
        self.root_layout.add_widget(screen)

    def add_class(self, instance):
        d = self.r_day.text.strip()
        t = self.r_time.text.strip()
        s = self.r_sub.text.strip()
        r = self.r_room.text.strip()
        rm = self.r_rem.text.strip()
        if d and t and s:
            rem_val = int(rm) if rm.isdigit() else 30
            self.data["routine"].append({"day": d, "time": t, "subject": s, "room": r, "reminder_min": rem_val, "reminder_on": True})
            save_data(self.data)
            self.show_routine_screen()

    def toggle_reminder(self, index):
        if 0 <= index < len(self.data["routine"]):
            current_status = self.data["routine"][index].get("reminder_on", True)
            self.data["routine"][index]["reminder_on"] = not current_status
            save_data(self.data)
            self.show_routine_screen()

    def delete_class(self, index):
        if 0 <= index < len(self.data["routine"]):
            self.data["routine"].pop(index)
            save_data(self.data)
            self.show_routine_screen()

    def show_exam_screen(self):
        self.clear()
        screen = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        screen.add_widget(Label(text="📝 CT, Mid & Final Exam Manager", font_size="18sp", bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(35)))
        
        self.e_type = TextInput(hint_text="Exam Type (e.g. CT-1 / Mid / Final)", multiline=False, size_hint_y=None, height=dp(38))
        self.e_sub = TextInput(hint_text="Subject Name", multiline=False, size_hint_y=None, height=dp(38))
        self.e_date = TextInput(hint_text="Date (e.g. 2026-04-15)", multiline=False, size_hint_y=None, height=dp(38))
        self.e_time = TextInput(hint_text="Time (e.g. 10:00 AM)", multiline=False, size_hint_y=None, height=dp(38))
        
        for widget in [self.e_type, self.e_sub, self.e_date, self.e_time]:
            screen.add_widget(widget)
            
        btn_add_exam = AsmaniButton(text="➕ Add Exam / CT")
        btn_add_exam.bind(on_press=self.add_exam)
        screen.add_widget(btn_add_exam)
        
        scroll = ScrollView()
        exam_list_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=dp(2))
        exam_list_layout.bind(minimum_height=exam_list_layout.setter('height'))
        
        for index, item in enumerate(self.data.get("exams", [])):
            card = CardBox(bg_color=(0.88, 0.93, 0.98, 1))
            txt = f"[b]{item['type']} : {item['subject']}[/b]\n📅 Date: {item['date']} | ⏰ {item['time']}"
            lbl = Label(text=txt, markup=True, font_size="12sp", color=(0.15, 0.15, 0.15, 1), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            card.add_widget(lbl)
            
            btn_del = Button(text="Delete", size_hint_x=None, width=dp(70), background_color=(0.9, 0.2, 0.2, 1))
            btn_del.bind(on_press=lambda inst, idx=index: self.delete_exam(idx))
            card.add_widget(btn_del)
            
            exam_list_layout.add_widget(card)
            
        scroll.add_widget(exam_list_layout)
        screen.add_widget(scroll)
        
        btn_back = AccentButton(text="🔙 Back to Dashboard")
        btn_back.bind(on_press=lambda x: self.show_dashboard())
        screen.add_widget(btn_back)
        self.root_layout.add_widget(screen)

    def add_exam(self, instance):
        t = self.e_type.text.strip()
        s = self.e_sub.text.strip()
        d = self.e_date.text.strip()
        tm = self.e_time.text.strip()
        if t and s:
            if "exams" not in self.data:
                self.data["exams"] = []
            self.data["exams"].append({"type": t, "subject": s, "date": d, "time": tm})
            save_data(self.data)
            self.show_exam_screen()

    def delete_exam(self, index):
        if "exams" in self.data and 0 <= index < len(self.data["exams"]):
            self.data["exams"].pop(index)
            save_data(self.data)
            self.show_exam_screen()

    def show_task_screen(self):
        self.clear()
        screen = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        screen.add_widget(Label(text="📌 Subject-wise Task & Assignment Manager", font_size="16sp", bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(35)))
        
        self.t_sub = TextInput(hint_text="Subject Name (e.g. CSE 2391)", multiline=False, size_hint_y=None, height=dp(38))
        self.t_text = TextInput(hint_text="Task Details / Assignment", multiline=False, size_hint_y=None, height=dp(38))
        
        for w in [self.t_sub, self.t_text]:
            screen.add_widget(w)
            
        btn_add = AsmaniButton(text="➕ Add Task")
        btn_add.bind(on_press=self.add_task)
        screen.add_widget(btn_add)
        
        scroll = ScrollView()
        self.task_list_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=dp(2))
        self.task_list_layout.bind(minimum_height=self.task_list_layout.setter('height'))
        
        for idx, t in enumerate(self.data["tasks"]):
            card = CardBox(bg_color=(0.88, 0.93, 0.98, 1))
            txt = f"[b]{t.get('subject', 'General')}[/b]\n• {t.get('text', '')}"
            lbl = Label(text=txt, markup=True, font_size="12sp", color=(0.15, 0.15, 0.15, 1), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            card.add_widget(lbl)
            
            btn_done = Button(text="Done", size_hint_x=None, width=dp(70), background_color=(0.2, 0.7, 0.3, 1))
            btn_done.bind(on_press=lambda inst, i=idx: self.delete_task(i))
            card.add_widget(btn_done)
            
            self.task_list_layout.add_widget(card)
            
        scroll.add_widget(self.task_list_layout)
        screen.add_widget(scroll)
        
        btn_back = AccentButton(text="🔙 Back to Dashboard")
        btn_back.bind(on_press=lambda x: self.show_dashboard())
        screen.add_widget(btn_back)
        self.root_layout.add_widget(screen)

    def add_task(self, instance):
        sub = self.t_sub.text.strip()
        text = self.t_text.text.strip()
        if text:
            self.data["tasks"].append({"subject": sub if sub else "General", "text": text})
            save_data(self.data)
            self.show_task_screen()

    def delete_task(self, index):
        if 0 <= index < len(self.data["tasks"]):
            self.data["tasks"].pop(index)
            save_data(self.data)
            self.show_task_screen()

    def show_album_screen(self):
        self.clear()
        screen = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        screen.add_widget(Label(text="🖼️ Subject-wise Albums & Gallery Notes", font_size="18sp", bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(35)))
        
        self.a_sub = TextInput(hint_text="Subject Name (e.g. CSE 2391)", multiline=False, size_hint_y=None, height=dp(38))
        self.a_note = TextInput(hint_text="Note / Description", multiline=False, size_hint_y=None, height=dp(38))
        self.a_img = TextInput(hint_text="Image Path (e.g. C:/Users/.../pic.jpg)", multiline=False, size_hint_y=None, height=dp(38))
        
        for w in [self.a_sub, self.a_note, self.a_img]:
            screen.add_widget(w)
            
        btn_add = AsmaniButton(text="➕ Save Image & Note to Album")
        btn_add.bind(on_press=self.add_album_item)
        screen.add_widget(btn_add)
        
        scroll = ScrollView()
        album_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10), padding=dp(2))
        album_layout.bind(minimum_height=album_layout.setter('height'))
        
        albums = self.data.get("albums", {})
        if not albums:
            album_layout.add_widget(Label(text="No subject albums added yet.", font_size="13sp", color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(40)))
        else:
            for sub, items in albums.items():
                album_layout.add_widget(Label(text=f"📂 Subject: {sub}", font_size="14sp", bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(30)))
                for idx, item in enumerate(items):
                    card = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(100), padding=dp(5), spacing=dp(10))
                    
                    img_path = item.get('image_path', '')
                    if img_path and os.path.exists(img_path):
                        img = AsyncImage(source=img_path, size_hint_x=None, width=dp(90))
                        card.add_widget(img)
                    else:
                        lbl_img = Label(text="[No Image]", font_size="10sp", size_hint_x=None, width=dp(80), color=(0.5,0.5,0.5,1))
                        card.add_widget(lbl_img)
                        
                    txt = f"📅 {item['date']}\n📝 {item['note']}"
                    lbl = Label(text=txt, markup=True, font_size="12sp", color=(0.15, 0.15, 0.15, 1), halign='left', valign='middle')
                    lbl.bind(size=lbl.setter('text_size'))
                    card.add_widget(lbl)
                    
                    btn_del = Button(text="Delete", size_hint_x=None, width=dp(60), background_color=(0.9, 0.2, 0.2, 1))
                    btn_del.bind(on_press=lambda inst, s=sub, i=idx: self.delete_album_item(s, i))
                    card.add_widget(btn_del)
                    
                    album_layout.add_widget(card)
            
        scroll.add_widget(album_layout)
        screen.add_widget(scroll)
        
        btn_back = AccentButton(text="🔙 Back to Dashboard")
        btn_back.bind(on_press=lambda x: self.show_dashboard())
        screen.add_widget(btn_back)
        self.root_layout.add_widget(screen)

    def add_album_item(self, instance):
        sub = self.a_sub.text.strip()
        note = self.a_note.text.strip()
        img_path = self.a_img.text.strip()
        if sub and note:
            if "albums" not in self.data:
                self.data["albums"] = {}
            if sub not in self.data["albums"]:
                self.data["albums"][sub] = []
            
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            self.data["albums"][sub].append({
                "date": current_date,
                "note": note,
                "image_path": img_path
            })
            save_data(self.data)
            self.show_album_screen()

    def delete_album_item(self, subject, index):
        if subject in self.data["albums"] and 0 <= index < len(self.data["albums"][subject]):
            self.data["albums"][subject].pop(index)
            if not self.data["albums"][subject]:
                del self.data["albums"][subject]
            save_data(self.data)
            self.show_album_screen()

if __name__ == "__main__":
    StudentApp().run()