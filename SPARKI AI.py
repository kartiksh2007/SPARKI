import customtkinter as ctk
import json, os, threading, requests, time, re, base64
from datetime import datetime
from openai import OpenAI
from PIL import Image
from io import BytesIO
from tkinter import filedialog, messagebox, Menu
import PyPDF2
import keyboard 
from gtts import gTTS
import pygame
import speech_recognition as sr
from googlesearch import search
from bs4 import BeautifulSoup
import psutil  # For System & Battery Monitoring
import ctypes
import webbrowser
try:
    myappid = 'sparkiedix.sparkiai.v1' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

# Audio initialization
pygame.mixer.init()

class Config:
    MEMORY_FILE = "sparki_memory.json"
    HISTORY_FILE = "chat_history_db.json"
    IMAGE_INVOKE_URL = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-dev"
    CHAT_MODEL = "arcee-ai/trinity-large-preview:free"
    
    # Inhe pehle None rakhte hain
    nvidia_client = None 
    USER_NAME = "User"

    @classmethod
    def load_config(cls):
        if os.path.exists(cls.MEMORY_FILE):
            with open(cls.MEMORY_FILE, "r") as f:
                data = json.load(f)
                cls.OPENROUTER_KEY = data.get("openrouter_key", "")
                cls.IMAGE_API_KEY = data.get("nvidia_key", "")
                cls.TELEGRAM_TOKEN = data.get("tg_token", "")
                cls.TELEGRAM_CHAT_ID = data.get("tg_chat_id", "")
                cls.USER_NAME = data.get("user_name", "User")
        else:
            cls.OPENROUTER_KEY = ""
            cls.IMAGE_API_KEY = ""
            cls.TELEGRAM_TOKEN = ""
            cls.TELEGRAM_CHAT_ID = ""
            cls.USER_NAME = "User"

        # 🔥 NVIDIA Client ko yahan initialize karo (Taki updated key use ho)
        # Agar key file mein nahi hai, toh teri backup key use hogi
        api_to_use = cls.IMAGE_API_KEY if cls.IMAGE_API_KEY else "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"
        
        cls.nvidia_client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_to_use
        )

    # Dynamic System Identity (Taaki User Name update hota rahe)
    @classmethod
    def get_system_identity(cls):
        return (
            f"Your name is sparki. You are a professional AI assistant. "
            f"You were developed by Kartik. "
            f"User's name is {cls.USER_NAME}. "
            f"IMPORTANT: Today is {datetime.now().strftime('%A, %B %d, %Y')}. "
            "STRICT RULE: Respond ONLY in Hinglish using Roman Script (English Alphabets). "
            "DO NOT use Devanagari (Hindi characters)."
        )
class SetupWizard(ctk.CTkToplevel):
    def __init__(self, on_success):
        super().__init__()
        self.title("SPARKI AI - First Time Setup")
        try:
            self.iconbitmap("sparki.ico")
        except:
            pass
            
        self.geometry("650x600")
        
        
        self.on_success = on_success
        self.attributes('-topmost', True) # Setup window hamesha upar rahegi
        self.protocol("WM_DELETE_WINDOW", lambda: os._exit(0)) # Bina setup ke close nahi hoga
        
        self.data = {}
        self.current_step = 1
        self.build_ui()

    def build_ui(self):
        for widget in self.winfo_children(): widget.destroy()
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)

        if self.current_step == 1:
            self.step_one(main_frame)
        elif self.current_step == 2:
            self.step_two(main_frame)
        elif self.current_step == 3:
            self.step_three(main_frame)

    def step_one(self, frame):
        ctk.CTkLabel(frame, text="🚀 Step 1: OpenRouter Setup", font=("Orbitron", 22, "bold"), text_color="#00E5FF").pack(pady=10)
        
        instr = ("Namaste! Sparki ka dimaag chalane ke liye OpenRouter API Key chahiye.\n"
                 "1. Niche diye link pe click karein.\n"
                 "2. 'Create Key' pe click karke copy karein aur yahan paste karein.")
        ctk.CTkLabel(frame, text=instr, font=("Segoe UI", 13), justify="center", wraplength=500).pack(pady=10)
        
        ctk.CTkButton(frame, text="🌐 Get OpenRouter Key (Click Here)", fg_color="#1f538d", 
                      command=lambda: webbrowser.open("https://openrouter.ai/keys")).pack(pady=5)
        
        self.name_entry = ctk.CTkEntry(frame, placeholder_text="Aapka Naam...", width=400)
        self.name_entry.pack(pady=10)
        
        self.key_entry = ctk.CTkEntry(frame, placeholder_text="Paste OpenRouter Key (sk-or-v1-...)", width=400)
        self.key_entry.pack(pady=5)
        
        ctk.CTkButton(frame, text="Next Step →", command=self.save_step_one).pack(pady=20)

    def step_two(self, frame):
        ctk.CTkLabel(frame, text="🎨 Step 2: Image Generation (NVIDIA)", font=("Orbitron", 22, "bold"), text_color="#00FF7F").pack(pady=10)
        
        instr = ("Ab AI Images banane ke liye NVIDIA API key chahiye.\n"
                 "1. Link pe jaake login karein.\n"
                 "2. 'Get API Key' pe click karke copy-paste karein.")
        ctk.CTkLabel(frame, text=instr, font=("Segoe UI", 13), justify="center", wraplength=500).pack(pady=10)
        
        ctk.CTkButton(frame, text="🖼️ Get NVIDIA Key (Click Here)", fg_color="#28a745", 
                      command=lambda: webbrowser.open("https://build.nvidia.com/black-forest-labs/flux-1-dev")).pack(pady=5)
        
        self.nv_entry = ctk.CTkEntry(frame, placeholder_text="Paste NVIDIA API Key (nvapi-...)", width=400)
        self.nv_entry.pack(pady=10)
        
        ctk.CTkButton(frame, text="Next Step →", command=self.save_step_two).pack(pady=20)

    def step_three(self, frame):
        ctk.CTkLabel(frame, text="☁️ Step 3: Telegram Cloud Backup", font=("Orbitron", 22, "bold"), text_color="#FFD700").pack(pady=10)
        
        instr = ("Sparki ki memory cloud pe save karne ke liye Telegram setup karein.\n"
                 "1. @BotFather se 'Token' lein.\n"
                 "2. @userinfobot se apni 'Chat ID' lein.")
        ctk.CTkLabel(frame, text=instr, font=("Segoe UI", 13), justify="center", wraplength=500).pack(pady=10)
        
        self.tk_entry = ctk.CTkEntry(frame, placeholder_text="Telegram Bot Token", width=400)
        self.tk_entry.pack(pady=5)
        self.id_entry = ctk.CTkEntry(frame, placeholder_text="Telegram Chat ID", width=400)
        self.id_entry.pack(pady=5)
        
        ctk.CTkButton(frame, text="Finish Setup 🎉", fg_color="#cc0000", command=self.finish_all).pack(pady=20)

    def save_step_one(self):
        self.data["user_name"] = self.name_entry.get()
        self.data["openrouter_key"] = self.key_entry.get()
        self.current_step = 2
        self.build_ui()

    def save_step_two(self):
        self.data["nvidia_key"] = self.nv_entry.get()
        self.current_step = 3
        self.build_ui()

    def finish_all(self):
        self.data["tg_token"] = self.tk_entry.get()
        self.data["tg_chat_id"] = self.id_entry.get()
        self.data["setup_done"] = True
        
        with open("sparki_memory.json", "w") as f:
            json.dump(self.data, f, indent=4)
        
        self.welcome_animation()

    def welcome_animation(self):
        for widget in self.winfo_children(): widget.destroy()
        
        # Welcome Animation Text
        lbl = ctk.CTkLabel(self, text=f"WELCOME {self.data['user_name'].upper()}\nSPARKI IS READY", 
                           font=("Orbitron", 30, "bold"), text_color="#00E5FF")
        lbl.pack(expand=True)
        
        # Ek choti sound play kar sakte ho yahan
        self.after(3000, self.complete)

    def complete(self):
        self.withdraw() # Pehle window chupao
        self.after(200, self.destroy) # Thoda gap dekar destroy karo
        self.on_success()  

class SPARKI_AI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- 1. Basic Window Setup ---
        self.title("SPARKI AI - Developed by Kartik")
        self.geometry("1300x850")
        ctk.set_appearance_mode("dark")
        try:
            self.iconbitmap("sparki.ico") 
        except:
            # Agar .ico file nahi mili toh error nahi aayega
            pass
        
        # --- 2. Theme & State Initialization (ERROR FIX HERE) ---
        # Inhe hamesha buttons se pehle define karna hota hai
        self.themes = ["dark", "grey", "3d_blue", "3d_purple"]
        self.current_theme_index = 0
        
        # Memory and Logic
        self.memory = self.load_memory() # Make sure this function exists in your code
        self.pdf_context = ""
        self.pdf_name = ""
        self.conversation = []
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.web_memory = ""  # Ye hamara RAM storage hai website code ke liye
        self.apps_visible = True # Apps ki visibility state
        # App Ecosystem
        self.added_apps = self.memory.get("added_apps", {})
        self.app_notifications = {app: 0 for app in self.added_apps}
        self.all_sessions = self.load_all_sessions()
        
        # Voice & Control States
        self.voice_mode_active = False
        self.is_speaking = False
        self.recognizer = sr.Recognizer()
        self.last_bubble_label = None 

        # --- 3. Grid Layout (Professional Architecture) ---
        self.grid_columnconfigure(0, weight=0) # Left Sidebar
        self.grid_columnconfigure(1, weight=1) # Main Chat
        self.grid_columnconfigure(2, weight=0) # Right Apps
        self.grid_rowconfigure(0, weight=1)

        # --- 4. LEFT SIDEBAR (History & Core) ---
        self.build_sidebar() # Ensure this creates self.sidebar
        
        # Theme Switcher (Inside Left Sidebar)
        self.theme_btn = ctk.CTkButton(self.sidebar, text="🎨 Change Theme", 
                                       fg_color="#2B2B2B", hover_color="#3D3D3D",
                                       font=("Segoe UI", 12, "bold"),
                                       command=self.change_theme_logic)
        self.theme_btn.pack(side="bottom", pady=20, padx=20, fill="x")
        # Button setup (Purana wala hi rahega)
        self.stop_button = ctk.CTkButton(
            self.sidebar, 
            text="STOP SPARKI 🛑", 
            fg_color="#cc0000", 
            hover_color="#990000",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.stop_sparki
        )

        # 🔥 AB YE LINE UPDATE KARO (pack ki jagah place use karo)
        self.stop_button.place(relx=0.5, rely=0.92, anchor="s", relwidth=0.8)

        # --- 5. MAIN CHAT VIEW ---
        self.build_main_view() # Central part
        

        # --- 6. RIGHT SIDEBAR (Modern App Panel) ---
        # --- 6. RIGHT SIDEBAR (Modern App Panel with Hide/Unhide) ---
        self.sidebar_right = ctk.CTkFrame(self, width=170, corner_radius=0, fg_color="#121212", border_width=1, border_color="#1F1F1F")
        self.sidebar_right.grid(row=0, column=2, sticky="nsew")
        
        # Header Frame taaki Label aur Button ek hi line mein rahein
        self.app_header_frame = ctk.CTkFrame(self.sidebar_right, fg_color="transparent")
        self.app_header_frame.pack(pady=(25, 10), fill="x", padx=10)

        # APPS Label
        ctk.CTkLabel(self.app_header_frame, text="APPS", font=("Orbitron", 16, "bold"), text_color="#00E5FF").pack(side="left", padx=5)

        # 👁️ Toggle Button (Hide/Unhide)
        self.toggle_apps_btn = ctk.CTkButton(self.app_header_frame, text="👁️", width=30, height=25, 
                                             fg_color="transparent", hover_color="#1F1F1F", 
                                             font=("Arial", 14), command=self.toggle_apps_visibility)
        self.toggle_apps_btn.pack(side="right")
        
        # Apps Container
        self.apps_container = ctk.CTkScrollableFrame(self.sidebar_right, fg_color="transparent", width=150)
        self.apps_container.pack(fill="both", expand=True, padx=5)
        
        # Add App Button
        self.add_app_btn = ctk.CTkButton(self.sidebar_right, text="+ Add App", 
                                         fg_color="#28a745", hover_color="#218838", 
                                         font=("Segoe UI", 12, "bold"),
                                         command=self.open_app_selector, height=35)
        self.add_app_btn.pack(pady=20, padx=15, fill="x")
        
        # --- 7. Final Checks & Threads ---
        self.refresh_sidebar()
        self.build_voice_overlay() 
        self.refresh_history_ui()
        
        if not os.path.exists("sparki_images"):
            os.makedirs("sparki_images")
            
        # Background Dashboard Updates
        threading.Thread(target=self.update_dashboard, daemon=True).start()

        # Global Hotkey
        keyboard.add_hotkey('f9', lambda: self.after(0, self.stop_and_listen))
    def toggle_apps_visibility(self):
        """Apps container ko hide ya unhide karne ke liye"""
        if self.apps_visible:
            # Apps ko chhupao
            self.apps_container.pack_forget()
            self.toggle_apps_btn.configure(text="🙈", text_color="gray")
            self.apps_visible = False
        else:
            # Apps ko wapas lao (Add App button se PEHLE pack karna hai)
            self.apps_container.pack(fill="both", expand=True, padx=5, before=self.add_app_btn)
            self.toggle_apps_btn.configure(text="👁️", text_color="#00E5FF")
            self.apps_visible = True    
    def change_theme_logic(self):
        self.current_theme_index = (self.current_theme_index + 1) % len(self.themes)
        theme = self.themes[self.current_theme_index]
        
        if theme == "dark":
            self.configure(fg_color="#000000")
            self.main_view.configure(fg_color="#171717")
            self.sidebar.configure(fg_color="#121212")
            self.sidebar_right.configure(fg_color="#121212") # Right side wala bhi fix
            
            
        elif theme == "grey":
            self.configure(fg_color="#2c2c2c")
            self.main_view.configure(fg_color="#3d3d3d")
            self.sidebar.configure(fg_color="#262626")
            self.sidebar_right.configure(fg_color="#262626")
            
        elif theme == "3d_blue":
            self.main_view.configure(fg_color="#0f172a") # Dark Blue
            self.sidebar.configure(fg_color="#1e293b")
            self.sidebar_right.configure(fg_color="#1e293b")
            
        elif theme == "3d_purple":
            self.main_view.configure(fg_color="#1e1b4b") # Deep Purple
            self.sidebar.configure(fg_color="#312e81")
            self.sidebar_right.configure(fg_color="#312e81")
            
    def load_memory(self):
        # Default structure agar file na mile
        default_data = {
            "user_info": "Not known yet", 
            "preferences": "Not set", 
            "added_apps": {} # Naya section apps ke liye
        }
        
        if os.path.exists(Config.MEMORY_FILE):
            try:
                with open(Config.MEMORY_FILE, "r") as f:
                    data = json.load(f)
                    # Check karo ki purani memory mein 'added_apps' key hai ya nahi
                    if "added_apps" not in data:
                        data["added_apps"] = {}
                    return data
            except Exception as e:
                print(f"Memory load error: {e}")
                return default_data
        return default_data
    
    def save_memory(self):
        with open(Config.MEMORY_FILE, "w") as f: json.dump(self.memory, f)

    # --- FEATURE: LIVE DASHBOARD (Stats, Battery, Time) ---
    def update_dashboard(self):
        while True:
            # Stats calculation
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            # Battery check
            battery = psutil.sensors_battery()
            batt_status = f"{battery.percent}%" if battery else "N/A"
            charging = " (⚡)" if battery and battery.power_plugged else ""
            
            # Time check
            current_time = datetime.now().strftime("%I:%M:%S %p")
            
            stat_text = f"CPU: {cpu}%  |  RAM: {ram}%\nBATT: {batt_status}{charging}\n{current_time}"
            
            try:
                self.after(0, lambda: self.stat_label.configure(text=stat_text))
            except: break
            time.sleep(1) # Har second update hoga
    def upload_to_cloud_direct(self, data, filename, caption="Sparki Cloud File"):
        url = f"https://api.telegram.org/bot{Config.TELEGRAM_TOKEN}/sendDocument"
        try:
            bio = BytesIO(data)
            bio.name = filename 
            res = requests.post(url, data={"chat_id": Config.TELEGRAM_CHAT_ID, "caption": caption}, files={"document": bio})
            
            if res.status_code == 200:
                # 🔥 Ye line sabse zaroori hai
                return res.json()['result']['document']['file_id']
        except Exception as e:
            print(f"❌ Cloud Upload Error: {e}")
        return None  

    def google_search_engine(self, query):
        try:
            results_list = []
            for url in search(query, num_results=3):
                results_list.append(url)
            if not results_list: return "No direct results found on Google."
            headers = {'User-Agent': 'Mozilla/5.0'}
            page = requests.get(results_list[0], headers=headers, timeout=5)
            soup = BeautifulSoup(page.content, 'html.parser')
            paragraphs = soup.find_all('p')
            snippet = "\n".join([p.get_text() for p in paragraphs[:2]])
            return f"Source: {results_list[0]}\nLive Info: {snippet}"
        except Exception as e:
            return f"Search Error: {str(e)}"

    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#121212")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="⚡ SPARKI AI", font=("Segoe UI", 32, "bold"), text_color="#00E5FF").pack(pady=(30, 5))
        ctk.CTkLabel(self.sidebar, text="BY KARTIK", font=("Segoe UI", 10, "bold"), text_color="gray").pack(pady=(0, 10))
        
        # --- ENHANCED DASHBOARD UI ---
        self.stat_frame = ctk.CTkFrame(self.sidebar, fg_color="#1e1e1e", corner_radius=10)
        self.stat_frame.pack(padx=20, fill="x", pady=5)
        self.stat_label = ctk.CTkLabel(self.stat_frame, text="Loading Stats...", font=("Consolas", 13, "bold"), text_color="#00FF7F", justify="center")
        self.stat_label.pack(pady=10)

        ctk.CTkButton(self.sidebar, text="+ New Chat", fg_color="#1e1e1e", command=self.new_chat).pack(pady=10, padx=20, fill="x")
        self.v_mode_btn = ctk.CTkButton(self.sidebar, text="Start Voice Mode", fg_color="#007AFF", command=self.toggle_voice_mode)
        self.v_mode_btn.pack(padx=20, fill="x")
        self.hist_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", label_text="Recent History")
        self.hist_scroll.pack(fill="both", expand=True, padx=5, pady=20)

    def build_main_view(self):
        self.main_view = ctk.CTkFrame(self, corner_radius=0, fg_color="#171717")
        self.main_view.grid(row=0, column=1, sticky="nsew")
        self.main_view.grid_rowconfigure(0, weight=1); self.main_view.grid_columnconfigure(0, weight=1)

        self.chat_area = ctk.CTkScrollableFrame(self.main_view, fg_color="transparent")
        self.chat_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.input_parent = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.input_parent.grid(row=1, column=0, sticky="ew", padx=100, pady=(0, 30))

        self.pdf_bar = ctk.CTkFrame(self.input_parent, fg_color="#1e1e1e", height=0, corner_radius=10)
        self.pdf_bar.pack(fill="x", pady=(0, 8))
        self.pdf_lbl = ctk.CTkLabel(self.pdf_bar, text="", font=("Segoe UI", 12), text_color="#00E5FF")
        self.pdf_lbl.pack(side="left", padx=15)

        # --- ENTRY BOX (TOOLS ON RIGHT FIX) ---
        self.entry_box = ctk.CTkFrame(self.input_parent, fg_color="#262626", corner_radius=25, border_width=1, border_color="#333333")
        self.entry_box.pack(fill="x", ipady=7)

        # 1. Floating Tools Menu (Sabse pehle define karo taaki AttributeError na aaye)
        self.tools_menu = ctk.CTkFrame(self.main_view, fg_color="#1a1a1a", border_width=1, border_color="#333333", corner_radius=10)
        ctk.CTkButton(self.tools_menu, text="🌐 SPARKI Web", fg_color="transparent", hover_color="#333333", 
                      command=self.activate_web_mode).pack(padx=10, pady=10)

        # 2. Paperclip (📎) - Left Side
        ctk.CTkButton(self.entry_box, text="📎", width=45, fg_color="transparent", 
                      font=("Arial", 22), command=self.upload_pdf).pack(side="left", padx=10)

        # 3. Main Entry Field - Middle
        self.entry = ctk.CTkEntry(self.entry_box, placeholder_text="Ask SPARKI AI...", 
                                  fg_color="transparent", border_width=0, font=("Segoe UI", 16))
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", lambda e: self.process_chat())

        # 4. Send Button (↑) - Right Edge
        ctk.CTkButton(self.entry_box, text="↑", width=38, height=38, corner_radius=19, 
                      fg_color="white", text_color="black", command=self.process_chat).pack(side="right", padx=(5, 12))

        # 5. Art Button (🎨)
        ctk.CTkButton(self.entry_box, text="🎨", width=45, fg_color="transparent", 
                      font=("Arial", 20), command=self.process_image).pack(side="right", padx=5)

        # 6. Tools Button (🛠️) - Right Side
        self.tools_btn = ctk.CTkButton(self.entry_box, text="🛠️", width=40, fg_color="transparent", 
                                       font=("Arial", 18), command=self.toggle_tools_menu)
        self.tools_btn.pack(side="right", padx=5)

        # 7. Mode Display Frame (Initial Hidden)
        self.mode_frame = ctk.CTkFrame(self.entry_box, fg_color="#1f538d", corner_radius=15)
        self.mode_lbl = ctk.CTkLabel(self.mode_frame, text="🌐 SPARKI Web 💻", font=("Segoe UI", 11, "bold"), text_color="white")
        self.mode_lbl.pack(side="left", padx=(10, 5))
        self.close_mode_btn = ctk.CTkButton(self.mode_frame, text="✕", width=25, fg_color="transparent", 
                                            hover_color="#cc0000", command=self.reset_to_default)
        self.close_mode_btn.pack(side="left", padx=(0, 5))
        self.mode_frame.pack_forget()
    def toggle_tools_menu(self):
        """Menu ko Right side button ke theek upar dikhayega"""
        if not hasattr(self, 'menu_visible') or not self.menu_visible:
            # Right side button ke liye relx 0.8-0.9 perfect hai
            self.tools_menu.place(relx=0.88, rely=0.88, anchor="se")
            self.menu_visible = True
        else:
            self.tools_menu.place_forget()
            self.menu_visible = False

    def activate_web_mode(self):
        """Web Mode ON: Tools hatega, Blue Label wahi aayega"""
        self.tools_btn.pack_forget()
        self.tools_menu.place_forget()
        self.menu_visible = False
        self.current_mode = "Web"
        
        # Wahi position (Right side) pe pack karo
        self.mode_frame.pack(side="right", padx=5)
        
        self.entry.delete(0, 'end')
        self.entry.configure(placeholder_text="Make a website with SPARKI...")
        self.focus_set()

    def reset_to_default(self):
        """Normal Mode: Blue Label hatega, Tools wapas aayega"""
        self.mode_frame.pack_forget()
        self.tools_btn.pack(side="right", padx=5)
        self.current_mode = "Default"
        
        self.entry.delete(0, 'end')
        self.entry.configure(placeholder_text="Ask SPARKI AI...")
        self.focus_set()    
    # --- SESSION HANDLING ---
    def open_session(self, session_id):
        self.new_chat()
        self.current_session_id = session_id
        session_data = self.all_sessions.get(session_id, {})
        self.conversation = session_data.get("messages", [])

        for msg in self.conversation:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system": continue 

            # F फालतू lines saaf karna
            

            if not content: continue

            # 🔥 CORRECT SEQUENCE: Jis order mein chat thi wahi dikhegi
            if content.startswith("TG_IMAGE:"):
                file_id = content.replace("TG_IMAGE:", "")
                self.load_image_from_tg(file_id)
            
            elif content.startswith("LOCAL_IMAGE:"):
                img_path = content.replace("LOCAL_IMAGE:", "")
                if os.path.exists(img_path):
                    try:
                        img = Image.open(img_path)
                        with open(img_path, "rb") as f: 
                            img_data = f.read()
                        self.display_image_from_history(img, img_data)
                    except: pass
            
            else:
                self.add_bubble(role, content)

    def load_image_from_tg(self, file_id):
        def fetch():
            try:
                # 1. Telegram se path lo
                res = requests.get(f"https://api.telegram.org/bot{Config.TELEGRAM_TOKEN}/getFile?file_id={file_id}").json()
                if not res.get('ok'): return
                
                file_path = res['result']['file_path']
                
                # 2. RAM mein download karo
                img_url = f"https://api.telegram.org/file/bot{Config.TELEGRAM_TOKEN}/{file_path}"
                img_data = requests.get(img_url).content
                img = Image.open(BytesIO(img_data))
                
                # 3. UI update (Threading fix ke saath)
                self.after(0, lambda i=img, d=img_data: self.display_image_from_history(i, d))
            except Exception as e:
                print(f"Cloud Load Error: {e}")
        
        threading.Thread(target=fetch, daemon=True).start()

    def display_image_from_history(self, img, data):
        """Is function mein ab Download Button bhi hai!"""
        row = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        row.pack(fill="x", pady=10, padx=25)
        
        bubble = ctk.CTkFrame(row, fg_color="#2b2b2b", corner_radius=20)
        bubble.pack(anchor="w")
        
        # Image display
        ctk_img = ctk.CTkImage(img, size=(480, 480))
        label = ctk.CTkLabel(bubble, image=ctk_img, text="")
        label.pack(padx=10, pady=10)

        # 🔥 FIXED: Download Button jo history images ke liye bhi kaam karega
        download_btn = ctk.CTkButton(
            bubble, 
            text="💾 Save to Laptop", 
            font=("Segoe UI", 12, "bold"),
            fg_color="#1f538d",
            hover_color="#14375e",
            command=lambda d=data: self.save_img(d) # 'data' ko yahan capture kiya
        )
        download_btn.pack(pady=(0, 15))
        
        self.scroll_to_bottom()

    def delete_session(self, session_id):
        if session_id in self.all_sessions:
            # 1. Dictionary se hatao
            del self.all_sessions[session_id]
            
            try:
                # 2. JSON mein write karo (Clean tarike se)
                with open(Config.HISTORY_FILE, "w") as f:
                    json.dump(self.all_sessions, f, indent=4)
                
                # 3. UI se wo button gayab karo
                self.refresh_history_ui()
                
                # 4. Agar wahi chat khuli thi, toh screen clear karo
                if self.current_session_id == session_id:
                    self.new_chat()
                    
                print(f"✅ Session {session_id} permanent delete ho gaya!")
            except Exception as e:
                print(f"❌ File save karne mein error: {e}")

    def load_all_sessions(self):
        if os.path.exists(Config.HISTORY_FILE):
            try:
                with open(Config.HISTORY_FILE, "r") as f: return json.load(f)
            except: return {}
        return {}

    def refresh_history_ui(self):
        for child in self.hist_scroll.winfo_children(): child.destroy()
        for sid, data in reversed(list(self.all_sessions.items())):
            container = ctk.CTkFrame(self.hist_scroll, fg_color="transparent")
            container.pack(fill="x", pady=2, padx=5)
            ctk.CTkButton(container, text=data['title'], anchor="w", fg_color="transparent", 
                         command=lambda s=sid: self.open_session(s)).pack(side="left", fill="x", expand=True)
            ctk.CTkButton(container, text="×", width=30, fg_color="transparent", text_color="gray", 
                         hover_color="#ff4b4b", command=lambda s=sid: self.delete_session(s)).pack(side="right")
    def web_agent_executor(self, url):
        # UI update ke liye 'after' use karenge
        self.after(0, lambda: self.add_bubble("assistant", f"Bhai, seedha rasta mil gaya! Khol raha hoon: {url} 🚀"))
        
        # Default browser kholne ke liye threading ki zaroorat nahi hai
        # Ye turant browser ko command bhej deta hai
        try:
            webbrowser.open(url)
        except Exception as e:
            self.after(0, lambda: self.add_bubble("assistant", f"Bhai browser khulne mein error hai: {str(e)[:30]}"))
    def process_chat(self, manual_text=None):
        text = manual_text if manual_text else self.entry.get().strip()
        if not manual_text: self.entry.delete(0, "end")
        if not text: return
        if hasattr(self, 'current_mode') and self.current_mode == "Web":
            self.add_bubble("user", text)
            self.sparki_web_builder(text)
            return
        
        self.add_bubble("user", text)

        def smart_decision():
            try:
                client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=Config.OPENROUTER_KEY)
                
                # Accuracy badhane ke liye Examples (Few-Shot Prompting)
                decision_prompt = (
                    f"User Message: '{text}'. "
                    "Task: Classify if the user wants to OPEN a specific website or just CHAT.\n\n"
                    "RULES:\n"
                    "1. If user asks to open/visit/go to a brand (Swiggy, Amazon, YT, etc.), reply ONLY with the URL.\n"
                    "2. If user asks a question ABOUT a brand (e.g., 'Swiggy kab bana?'), reply ONLY 'CHAT'.\n"
                    "3. If user just greets or asks general info, reply ONLY 'CHAT'.\n\n"
                    "EXAMPLES:\n"
                    "- 'Swiggy kholo' -> https://www.swiggy.com\n"
                    "- 'Amazon pe iPhone dikha' -> https://www.amazon.in/s?k=iPhone\n"
                    "- 'YouTube pe Carryminati' -> https://www.youtube.com/results?search_query=Carryminati\n"
                    "- 'Swiggy ka owner kaun hai?' -> CHAT\n"
                    "- 'Google pe weather check kar' -> https://www.google.com/search?q=weather\n"
                    "- 'Hi, kaise ho?' -> CHAT\n\n"
                    "Response Format: Direct URL or the word CHAT."
                )

                res = client.chat.completions.create(
                    model=Config.CHAT_MODEL,
                    messages=[{"role": "user", "content": decision_prompt}]
                )
                
                ai_decision = res.choices[0].message.content.strip()

                # Robust Link Detection
                if "http" in ai_decision.lower():
                    url_match = re.search(r'(https?://[^\s]+)', ai_decision)
                    final_url = url_match.group(0) if url_match else ai_decision
                    self.web_agent_executor(final_url)
                else:
                    self.continue_normal_chat(text)

            except Exception as e:
                print(f"Decision Error: {e}")
                self.continue_normal_chat(text)

        threading.Thread(target=smart_decision, daemon=True).start()
    def mcp_web_tool(self, query):
        """MCP Style Tool: Zero-cost live data fetcher"""
        try:
            # Google search snippets nikalne ke liye
            encoded_query = requests.utils.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}&hl=en"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0"}
            
            resp = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Google ke different result containers ko scan karna
            results = []
            for g in soup.find_all('div', class_=['VwiC3b', 'BNeawe']):
                text = g.get_text().strip()
                if len(text) > 20: results.append(text)
            
            return "\n".join(results[:3]) if results else "No live data found."
        except:
            return "Connection error with MCP Tool."   
    def deep_search_tool(self, query):
        """Top 10 website se data nikalne wala upgraded tool"""
        try:
            encoded_query = requests.utils.quote(query)
            url = f"https://www.bing.com/search?q={encoded_query}&count=10"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Saare snippets aur titles nikalna
            raw_data = []
            results = soup.find_all('li', class_='b_algo')
            
            for index, item in enumerate(results[:10]): # Top 10 results
                title = item.find('h2').get_text() if item.find('h2') else "No Title"
                snippet = item.find('p').get_text() if item.find('p') else ""
                if snippet:
                    raw_data.append(f"[{index+1}] Source: {title}\nInfo: {snippet}")
            
            # Agar primary snippets kam hain toh descriptions bhi uthao
            if len(raw_data) < 3:
                for caption in soup.find_all('div', class_='b_caption')[:5]:
                    raw_data.append(caption.get_text())

            final_report = "\n\n".join(raw_data)
            return final_report if final_report else "No deep data found."
            
        except Exception as e:
            return f"Deep Search Error: {str(e)}"
    def continue_normal_chat(self, text):
        # 1. Identity & Memory Setup (Sirf pehli baar ke liye)
        if not self.conversation:
            mem_prompt = f"\nUser Memory: {self.memory.get('user_info', 'Not set')}"
            self.conversation.append({"role": "system", "content": Config.SYSTEM_IDENTITY + mem_prompt})

        # 2. 🔥 Deep Research Brain: Intent + Top 10 Search
        def process_deep_intent():
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=Config.OPENROUTER_KEY)
            
            try:
                # A. AI sochega ki search query kya honi chahiye
                intent_check_prompt = [
                    {"role": "system", "content": "You are SPARKI's Research Engine. If the user needs real-time info, respond ONLY with a detailed search query. Otherwise, respond with 'OFFLINE'."},
                    {"role": "user", "content": text}
                ]
                
                decision = client.chat.completions.create(
                    model=Config.CHAT_MODEL,
                    messages=intent_check_prompt
                ).choices[0].message.content.strip()

                web_context = ""
                if "OFFLINE" not in decision:
                    print(f"🔍 Deep Research Mode: Analyzing Top 10 sites for '{decision}'")
                    # Yahan wahi deep_search_tool call ho raha hai jo 10 websites scan karta hai
                    web_context = self.deep_search_tool(decision)

                # B. Final Synthesis Prompt (Tony Stark Mode)
                if web_context:
                    full_prompt = f"""
                    [DEEP RESEARCH DATA FROM TOP 10 SOURCES]:
                    {web_context}

                    [USER QUESTION]: {text}

                    [INSTRUCTIONS]:
                    1. Upar diye gaye saare sources ko analyze karo.
                    2. Ek best, accurate aur detailed final answer tyar karo.
                    3. Tone 'Tony Stark' jaisa classy aur confident rakho.
                    4. Language Hinglish honi chahiye.
                    """
                else:
                    # Agar normal chat hai
                    full_prompt = text

                # C. Final prompt history mein dalo aur AI response start karo
                self.conversation.append({"role": "user", "content": full_prompt})
                self.get_ai_response()

            except Exception as e:
                print(f"Deep Intent Error: {e}")
                # Fallback: Agar logic fail ho toh normal response de do
                if text not in [c['content'] for c in self.conversation]:
                    self.conversation.append({"role": "user", "content": text})
                self.get_ai_response()

        # UI ko freeze hone se bachane ke liye background thread
        threading.Thread(target=process_deep_intent, daemon=True).start()
    def get_ai_response(self):
        # Purana sara code yahan comment out kar dena (OpenRouter wala)
        
        def run_nvidia_chat():
            try:
                # 1. Bubble create karo (Assistant ka placeholder)
                # self.add_bubble("assistant", "") logic yahan thoda badlega stream ke liye
                full_response = ""
                
                # 2. NVIDIA AI Call
                completion = nvidia_client.chat.completions.create(
                    model="google/gemma-2-9b-it",
                    messages=self.conversation, # Purani history maintain rahegi
                    temperature=0.2,
                    top_p=0.7,
                    max_tokens=1024,
                    stream=True
                )

                # 3. Streaming Logic for GUI
                # Pehle ek khali assistant bubble add karo
                self.after(0, lambda: self.add_bubble("assistant", "..."))
                
                for chunk in completion:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        
                        # Har chunk pe last bubble update karo (agar tune update_bubble banaya hai)
                        # Agar nahi banaya toh last mein ek saath dikhao ya chunk by chunk label append karo
                
                # Final response save karo
                self.conversation.append({"role": "assistant", "content": full_response})
                
                # UI Update (Final Text)
                self.after(0, lambda: self.refresh_last_bubble(full_response))
                
                # Voice output (Optional)
                if self.voice_mode_active:
                    self.tts_speak(full_response)

            except Exception as e:
                print(f"NVIDIA Error: {e}")
                self.after(0, lambda: self.add_bubble("assistant", "Bhai network check kar, error aa raha hai!"))

        threading.Thread(target=run_nvidia_chat, daemon=True).start()
    def update_last_bubble(self, new_text):
        # Sabse aakhiri row (bubble) nikalna
        rows = self.chat_area.winfo_children()
        if rows:
            last_row = rows[-1]
            # Bubble frame ke andar ka label dhoondhna
            for child in last_row.winfo_children():
                if isinstance(child, ctk.CTkFrame): # Ye hamara bubble hai
                    for sub_child in child.winfo_children():
                        if isinstance(sub_child, ctk.CTkLabel):
                            sub_child.configure(text=new_text)
                            break
        self.scroll_to_bottom()
    def add_bubble(self, role, text):
        align = "e" if role == "user" else "w"
        bubble_color = "#007AFF" if role == "user" else "#2b2b2b" 
        
        # Row jo poori width lega
        row = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        row.pack(fill="x", pady=10, padx=20)
        
        # Bubble Frame - Iski width hum fix rakhenge taaki text wrap ho sake
        bubble = ctk.CTkFrame(row, fg_color=bubble_color, corner_radius=20)
        bubble.pack(anchor=align)

        # LBL - wraplength ko humne fix 400 kar diya hai
        # Isse bada text ho hi nahi sakta, niche hi jayega
        lbl = ctk.CTkLabel(
            bubble, 
            text=text, 
            wraplength=400, # Ye magic number hai, text yahi ruk jayega
            justify="left", 
            font=("Segoe UI", 15), 
            text_color="white"
        )
        lbl.pack(padx=15, pady=10)
        
        if role == "assistant": 
            self.last_bubble_label = lbl 
            
        self.scroll_to_bottom()
    def build_voice_overlay(self):
        self.overlay = ctk.CTkFrame(self, fg_color="#0a0a0a") 
        self.exit_v_btn = ctk.CTkButton(self.overlay, text="✖ Close Voice Mode", fg_color="#ff4b4b", command=self.toggle_voice_mode)
        self.exit_v_btn.place(relx=0.95, rely=0.05, anchor="ne")
        self.voice_label = ctk.CTkLabel(self.overlay, text="Listening...", font=("Segoe UI", 24, "bold"), text_color="#00E5FF")
        self.voice_label.place(relx=0.5, rely=0.3, anchor="center")
        self.orb = ctk.CTkFrame(self.overlay, width=150, height=150, corner_radius=75, fg_color="#007AFF")
        self.orb.place(relx=0.5, rely=0.6, anchor="center")

    def tts_speak(self, text):
        if not self.voice_mode_active: return
        self.is_speaking = True
        def play():
            filename = f"speech_{int(time.time())}.mp3"
            try:
                # 1. Clean Markdown and extra symbols
                clean_text = re.sub(r'[*#_>~-]', '', text)
                
                # 2. Emojis aur ajeeb symbols ko hatao (Keep Hindi + English + Numbers)
                # Ye regex sirf alphanumeric aur basic punctuation rakhega
                clean_text = re.sub(r'[^\w\s,.।!a-zA-Z0-9]', '', clean_text)
                
                # 3. Clean extra spaces
                clean_text = " ".join(clean_text.split())

                if not clean_text.strip():
                    return

                # Hindi ('hi') lang use kar rahe hain jo Hinglish ko handle kar leti hai
                # Isko slow=False rakha hai taaki robotic na lage
                tts = gTTS(text=clean_text[:400], lang='hi', slow=False)
                tts.save(filename)
                
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy() and self.is_speaking: 
                    time.sleep(0.1)
                
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                
                if os.path.exists(filename): 
                    os.remove(filename)
            except Exception as e:
                print(f"TTS Error: {e}")
            finally: 
                self.is_speaking = False
                if self.voice_mode_active: 
                    self.after(200, self.start_voice_listening)
        
        threading.Thread(target=play, daemon=True).start()

    def voice_engine(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio, language="hi-IN")
                self.after(0, lambda: self.process_chat(manual_text=text))
            except:
                if self.voice_mode_active and not self.is_speaking: self.start_voice_listening()

    def toggle_voice_mode(self):
        if not self.voice_mode_active:
            self.voice_mode_active = True
            self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.start_voice_listening()
        else:
            self.voice_mode_active = False
            pygame.mixer.music.stop()
            self.overlay.place_forget()

    def start_voice_listening(self):
        if self.voice_mode_active: threading.Thread(target=self.voice_engine, daemon=True).start()

    def stop_and_listen(self):
        self.is_speaking = False
        pygame.mixer.music.stop()
        if self.voice_mode_active: self.start_voice_listening()
    # --- APP ECOSYSTEM LOGIC (BINA KUCH HATAAYE) ---
    def open_app_selector(self):
        path = filedialog.askopenfilename(title="Select App Executable", filetypes=[("Executable Files", "*.exe")])
        if path:
            app_name = os.path.basename(path).split('.')[0].capitalize()
            self.added_apps[app_name] = path
            self.app_notifications[app_name] = 0
            self.memory["added_apps"] = self.added_apps
            self.save_memory()
            self.refresh_sidebar()
            self.add_bubble("assistant", f"Bhai, {app_name} ko Sparki Ecosystem mein jod diya hai! 🔗")

    def refresh_sidebar(self):
        for widget in self.apps_container.winfo_children():
            widget.destroy()
        
        for app_name, path in self.added_apps.items():
            count = self.app_notifications.get(app_name, 0)
            # 10+, 20+, 30+ logic
            if count > 30: badge = "30+"
            elif count > 20: badge = "20+"
            elif count > 10: badge = "10+"
            else: badge = str(count)

            # Button text with Notification count
            btn_text = f"{app_name}\n({badge})"
            
            # App Button
            app_btn = ctk.CTkButton(self.apps_container, text=btn_text, fg_color="#262626", 
                                    height=60, corner_radius=10, font=("Segoe UI", 11),
                                    command=lambda p=path: os.startfile(p))
            app_btn.pack(pady=5, fill="x", padx=5)
            
            # Right Click to Remove
            app_btn.bind("<Button-3>", lambda e, name=app_name: self.show_app_context_menu(e, name))

    def show_app_context_menu(self, event, app_name):
        m = Menu(self, tearoff=0, bg="#1a1a1a", fg="white", borderwidth=0)
        m.add_command(label=f"Remove {app_name}", command=lambda: self.remove_sparki_app(app_name))
        m.post(event.x_root, event.y_root)

    def remove_sparki_app(self, app_name):
        if app_name in self.added_apps:
            del self.added_apps[app_name]
            if app_name in self.app_notifications: del self.app_notifications[app_name]
            self.memory["added_apps"] = self.added_apps
            self.save_memory()
            self.refresh_sidebar()
            self.add_bubble("assistant", f"Bhai, {app_name} ko list se hta diya hai. 👍")
    def upload_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.pdf_name = os.path.basename(path)
            def read():
                reader = PyPDF2.PdfReader(path)
                self.pdf_context = "".join([p.extract_text() for p in reader.pages])[:10000]
                self.after(0, self.show_pdf_status)
            threading.Thread(target=read, daemon=True).start()

    def show_pdf_status(self):
        self.pdf_bar.configure(height=40); self.pdf_lbl.configure(text=f"📄 {self.pdf_name} (Attached)")
        self.pdf_del_btn = ctk.CTkButton(self.pdf_bar, text="✖", width=30, command=self.remove_pdf); self.pdf_del_btn.pack(side="right", padx=10)

    def remove_pdf(self):
        self.pdf_context = ""; self.pdf_name = ""; self.pdf_bar.configure(height=0)
        if hasattr(self, 'pdf_del_btn'): self.pdf_del_btn.destroy()

    def process_image(self):
        prompt = self.entry.get().strip(); self.entry.delete(0, "end")
        if prompt:
            self.add_bubble("user", f"🎨 Visualizing: {prompt}")
            threading.Thread(target=self.run_flux, args=(prompt,), daemon=True).start()
    def remove_loading_animation(self):
        """Image load hone ke baad loading bubble hatane ke liye"""
        if hasattr(self, 'loading_row') and self.loading_row.winfo_exists():
            self.loading_row.destroy()        
    def show_loading_animation(self):
        """Image generate hote waqt loading bubble dikhane ke liye"""
        # 1. Loading Row setup
        self.loading_row = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        self.loading_row.pack(fill="x", pady=10, padx=25)
        
        # 2. Loading Bubble
        self.loading_bubble = ctk.CTkFrame(self.loading_row, fg_color="#2b2b2b", corner_radius=20)
        self.loading_bubble.pack(anchor="w")
        
        # 3. Loading Text (Hum yahan text use kar rahe hain, 
        # kyuki image animation lagane ke liye extra library chahiye hogi)
        self.loading_label = ctk.CTkLabel(self.loading_bubble, text="✨ Sparki is dreaming...", font=("Arial", 14, "italic"), text_color="#aaaaaa")
        self.loading_label.pack(padx=20, pady=15)
        
        # Ek chota sa dot animation chalane ke liye
        self.dot_count = 0
        self.animate_dots()
        
        self.scroll_to_bottom()
    
    def animate_dots(self):
        """Dots ko animate karne ke liye helper function"""
        if hasattr(self, 'loading_label') and self.loading_label.winfo_exists():
            base_text = "✨ Sparki is dreaming"
            self.dot_count = (self.dot_count + 1) % 4
            dots = "." * self.dot_count
            self.loading_label.configure(text=base_text + dots)
            # Har 500ms (0.5 sec) mein update karo
            self.after(500, self.animate_dots)
    def run_flux(self, prompt):
        self.after(0, self.show_loading_animation)
        
        try:
            headers = {
                "Authorization": f"Bearer {Config.IMAGE_API_KEY}",
                "Accept": "application/json",
            }
            payload = {
                "prompt": prompt,
               "mode": "base",
    "cfg_scale": 3.5,
    "width": 1024,
    "height": 1024,
    "seed": 0,
    "steps": 50
            }

            response = requests.post(Config.IMAGE_INVOKE_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            response_body = response.json()

            # NVIDIA API Base64 extraction
            if "artifacts" in response_body:
                image_b64 = response_body['artifacts'][0]['base64']
            elif "image" in response_body:
                image_b64 = response_body['image']
            else:
                raise Exception("Response mein image data nahi mila!")

            image_data = base64.b64decode(image_b64)
            
            # 🔥 Check: Kya ye waqai image hai?
            try:
                img = Image.open(BytesIO(image_data))
                img.verify() # Verify karega ki file corrupt toh nahi
                img = Image.open(BytesIO(image_data)) # Re-open for use
            except:
                raise Exception("API ne image ki jagah kachra bheja hai.")

            self.after(0, self.remove_loading_animation)
            self.after(0, lambda i=img, d=image_data: self.display_image(i, d))

            def upload_and_save(img_bytes, img_prompt):
                try:
                    img_name = f"sparki_{int(time.time())}.png"
                    file_id = self.upload_to_cloud_direct(img_bytes, img_name, f"Prompt: {img_prompt}")
                    if file_id:
                        self.conversation.append({"role": "assistant", "content": f"TG_IMAGE:{file_id}"})
                        self.save_chat()
                except Exception as thread_e:
                    print(f"❌ Cloud Backup Error: {thread_e}")

            threading.Thread(target=upload_and_save, args=(image_data, prompt), daemon=True).start()

        except Exception as err: # 👈 Humne 'e' ko 'err' kar diya
            self.after(0, self.remove_loading_animation)
            error_msg = str(err)[:50] # 👈 Error ko pehle string mein save kiya
            print(f"❌ NVIDIA Image Error: {err}")
            # 🔥 Fix: 'err_val=error_msg' pass karke lambda ko variable pakdaya
            self.after(0, lambda err_val=error_msg: self.add_bubble("assistant", f"Bhai image nahi ban payi: {err_val}"))
    def display_image(self, img, data):
        # UI Setup
        row = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        row.pack(fill="x", pady=10, padx=25)
        bubble = ctk.CTkFrame(row, fg_color="#2b2b2b", corner_radius=20)
        bubble.pack(anchor="w")
        
        # Display image from RAM
        ctk_img = ctk.CTkImage(img, size=(480, 480))
        ctk.CTkLabel(bubble, image=ctk_img, text="").pack(padx=10, pady=10)
        
        # Download button (Sirf tab jab tu manual click kare)
        ctk.CTkButton(bubble, text="Download to Laptop", command=lambda: self.save_img(data)).pack(pady=(0, 15))
        
        self.scroll_to_bottom()

    def save_img(self, data):
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path:
            with open(path, "wb") as f: f.write(data)

    def save_chat(self):
        if self.conversation:
            # Title setup
            user_msgs = [m["content"] for m in self.conversation if m["role"] == "user"]
            title = user_msgs[0][:25] + "..." if user_msgs else "New Chat"
            
            self.all_sessions[self.current_session_id] = {
                "title": title, 
                "messages": self.conversation,
                "pdf_context": self.pdf_context
            }
            
            # 1. JSON String banayi
            db_data = json.dumps(self.all_sessions, indent=4)
            
            # 2. 🔥 Cloud Pe Backup (RAM se seedha)
            threading.Thread(target=self.upload_to_cloud_direct, args=(db_data.encode(), f"history_{self.current_session_id}.json", "Chat History"), daemon=True).start()
            
            # Local update (UI ke liye zaroori hai)
            with open(Config.HISTORY_FILE, "w") as f:
                f.write(db_data)
                
            self.after(0, self.refresh_history_ui)
    def sparki_web_builder(self, user_prompt, file_paths=None):
        """Advanced Full-Stack Builder with Real File Integration"""
        def task():
            self.after(0, self.show_loading_ui)
            extracted_context = ""
            if file_paths:
                print(f"📂 Processing {len(file_paths)} files...")
                for path in file_paths:
                    try:
                        if path.endswith('.pdf'):
                            with open(path, 'rb') as f:
                                reader = PyPDF2.PdfReader(f)
                                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                                extracted_context += f"\n--- DATA FROM {os.path.basename(path)} ---\n{text}\n"
                        elif path.endswith(('.txt', '.py', '.js', '.html', '.json')):
                            with open(path, 'r', encoding='utf-8') as f:
                                extracted_context += f"\n--- CODE/DATA FROM {os.path.basename(path)} ---\n{f.read()}\n"
                    except Exception as fe:
                        print(f"❌ File Read Error: {fe}")

            # 🛑 Context Check: Agar context bahut bada hai toh trim karo par headers rakho
            if len(extracted_context) > 60000:
                extracted_context = extracted_context[:60000] + "\n...[Data Trimmed for Performance]..."

            # 🔥 Professional Full-Stack Architect Prompt
            sys_instr = """You are a World-Class Full-Stack Developer & Lead UI/UX Engineer.
            TASK: Build a high-end, production-ready, interactive web application.
            
            STRICT DESIGN RULES:
            1. UI: Use 'Apple-Style' Minimalism or 'Futuristic Dark' with Glassmorphism effects.
            2. ASSETS: Use Lucide-Icons or FontAwesome via CDN. Use professional fonts (Outfit, Inter).
            3. INTERACTIVITY: Every button MUST have a ripple effect or hover animation. Every tab/form MUST work via JavaScript.
            4. DATA INTEGRATION: Read the provided 'FILE DATA' carefully. Transform it into professional components: 
               - If it's statistics: Use Chart.js.
               - If it's a list: Use a searchable, paginated Table.
               - If it's a bio/profile: Create premium Hero Sections.
            5. CODE: Output ONLY one single code block containing HTML, CSS, and JS combined. No explanations."""

            # Structured User Prompt
            final_user_content = f"""
            [USER REQUEST]: {user_prompt}
            
            [CRITICAL FILE DATA]:
            {extracted_context if extracted_context else "No files attached."}
            
            [EXISTING CODEBASE TO UPDATE]:
            {self.web_memory if self.web_memory else "Starting new project."}
            
            INSTRUCTION: Use the [CRITICAL FILE DATA] to populate the website content. Make it look like a real, data-driven web app.
            """

            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=Config.OPENROUTER_KEY)
            
            # Coding King Model
            try:
                res = client.chat.completions.create(
                    model="nvidia/nemotron-3-super-120b-a12b:free", # Sabse stable aur powerful coding model
                    messages=[
                        {"role": "system", "content": sys_instr},
                        {"role": "user", "content": final_user_content}
                    ],
                    temperature=0.2
                )
                
                raw_code = res.choices[0].message.content
                clean_code = re.sub(r'```html|```', '', raw_code).strip()
                self.web_memory = clean_code
                
                self.after(0, self.show_web_result_ui)
                print("✅ SPARKI: Web App Built Successfully!")

            except Exception as e:
                error_msg = str(e)
                print(f"❌ AI Error: {error_msg}")
                self.after(0, lambda: self.add_bubble("assistant", f"⚠️ AI Error: {error_msg[:60]}"))

        threading.Thread(target=task, daemon=True).start()
    def show_loading_ui(self, task_name="Architecting"):
        """Web build hote waqt screen pe message dikhane ke liye"""
        self.loading_frame = ctk.CTkFrame(self.chat_area, fg_color="#0d0d0d", corner_radius=15, border_width=1, border_color="#1f538d")
        self.loading_frame.pack(fill="x", pady=10, padx=20)
        
        # Ye rahi teri line jo English mein dikhegi
        self.wait_label = ctk.CTkLabel(self.loading_frame, 
                                       text="SPARKI is architecting your website, please wait...", 
                                       font=("Segoe UI", 13, "bold"), 
                                       text_color="#ffffff")
        self.wait_label.pack(padx=20, pady=(15, 5))
        
        # Progress Bar
        self.prog = ctk.CTkProgressBar(self.loading_frame, orientation="horizontal", mode="indeterminate", width=280, progress_color="#1f538d")
        self.prog.pack(padx=20, pady=5)
        self.prog.start()
        
        # Niche chote logs (Optional, isse user ko pata chalta hai system chal raha hai)
        self.log_label = ctk.CTkLabel(self.loading_frame, text="⚙️ Initializing Engine...", font=("Consolas", 10), text_color="#00FF00")
        self.log_label.pack(padx=20, pady=(0, 15))
        
        logs = ["Processing Files...", "Generating Logic...", "Injecting CSS...", "Finalizing Code..."]
        def shuffle_logs(i=0):
            if hasattr(self, 'loading_frame') and self.loading_frame.winfo_exists():
                self.log_label.configure(text=f"⚙️ {logs[i % len(logs)]}")
                self.after(1000, lambda: shuffle_logs(i + 1))
        shuffle_logs()
    def show_web_result_ui(self):
        """Web build hone ke baad premium options dikhana"""
        # Purana loading hatao
        if hasattr(self, 'loading_frame'): self.loading_frame.destroy()
            
        row = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        row.pack(fill="x", pady=10, padx=20)
        
        # Dashboard UI Bubble
        bubble = ctk.CTkFrame(row, fg_color="#0a0a0a", corner_radius=20, border_width=1, border_color="#1f538d")
        bubble.pack(anchor="w", padx=2, pady=2)
        
        # Header Section
        header = ctk.CTkLabel(bubble, text="🚀 WEB APP READY", font=("Segoe UI", 13, "bold"), text_color="#1f538d")
        header.pack(padx=20, pady=(15, 5))

        details = "Stack: Full-Stack HTML/JS\nOptimization: Responsive UI\nAssets: CDN Enabled"
        ctk.CTkLabel(bubble, text=details, font=("Consolas", 10), text_color="#777777", justify="left").pack(padx=20, pady=5)
        
        # Control Buttons Row
        btn_row = ctk.CTkFrame(bubble, fg_color="transparent")
        btn_row.pack(padx=10, pady=(10, 20))

        # Button 1: Preview (Stark Blue)
        ctk.CTkButton(btn_row, text="🌐 LIVE PREVIEW", fg_color="#1f538d", text_color="white", 
                      hover_color="#2a6cb5", width=130, height=35, corner_radius=10, 
                      font=("Segoe UI", 11, "bold"), command=self.preview_web).pack(side="left", padx=5)
        
        # Button 2: Download (Transparent Border)
        ctk.CTkButton(btn_row, text="📥 DOWNLOAD", fg_color="transparent", border_width=1, 
                      border_color="#1f538d", text_color="white", hover_color="#1a1a1a",
                      width=130, height=35, corner_radius=10, 
                      font=("Segoe UI", 11, "bold"), command=self.download_web).pack(side="left", padx=5)

    def preview_web(self):
        """Temporary file banake browser mein open karna"""
        import tempfile
        if not hasattr(self, 'web_memory') or not self.web_memory:
            messagebox.showwarning("Warning", "No web code found! ⚠️")
            return
            
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as tf:
            tf.write(self.web_memory)
            webbrowser.open(f'file://{tf.name}')

    def download_web(self):
        """Professional File Dialog for saving code"""
        if not hasattr(self, 'web_memory') or not self.web_memory: return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".html", 
            initialfile="SPARKI_Web_Project.html",
            title="Export Source Code",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.web_memory)
            messagebox.showinfo("Export Success", "Full-Stack Source code saved! ✅")           

    def new_chat(self):
        for child in self.chat_area.winfo_children(): child.destroy()
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.conversation = []; self.remove_pdf()

    def scroll_to_bottom(self):
        self.update_idletasks()
        try: self.chat_area._parent_canvas.yview_moveto(1.0)
        except: pass
    def stop_sparki(self):
        # Confirmation check
        if messagebox.askyesno("Exit", "Kya aap SPARKI ko band karna chahte hain?"):
            # Sare background threads ko alert karne ke liye (Optional)
            print("Stopping SPARKI...")
            
            # Application close
            self.quit()
            self.destroy()
            os._exit(0) # Force exit taaki background threads bhi ruk jayein    

def launch_sparki():
    Config.load_config() # Keys load karo memory se
    app = SPARKI_AI()
    app.mainloop()

if __name__ == "__main__":
    # Check if setup is already done
    setup_done = False
    if os.path.exists(Config.MEMORY_FILE):
        try:
            with open(Config.MEMORY_FILE, "r") as f:
                data = json.load(f)
                setup_done = data.get("setup_done", False)
        except:
            setup_done = False

    if not setup_done:
        ctk.set_appearance_mode("dark")
        
        # Ek hidden root window banayenge
        temp_root = ctk.CTk()
        temp_root.withdraw() # Isse khali dabba nahi dikhega
        
        # Icon set karein taaki taskbar pe pankh na aaye
        try:
            temp_root.iconbitmap("sparki.ico")
        except:
            pass

        def start_main():
            # Setup khatam hone pe thoda ruk kar main app chalayenge
            # Taaki "application destroyed" wala error na aaye
            temp_root.after(100, temp_root.destroy) 
            launch_sparki()

        setup_app = SetupWizard(on_success=start_main)
        
        # Setup window ko bhi icon dedo
        try:
            setup_app.iconbitmap("sparki.ico")
        except:
            pass
            
        setup_app.mainloop()
    else:
        # Agar setup pehle se hai toh seedha SPARKI
        launch_sparki()
