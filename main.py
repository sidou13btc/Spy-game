import os
import random
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import arabic_reshaper

# ---------------- إعدادات المسارات (نسبية) ----------------
# هذه المجلدات يجب أن تكون بجانب ملف main.py داخل حزمة التطبيق
UI_DIR = "ui_images"
PLAYER_DIR = "player_images"
EXTS = (".png", ".jpg", ".jpeg", ".webp")

# ---------------- دالة معالجة النص العربي ----------------
def ar(text):
    """إعادة تشكيل النص العربي وعكسه للعرض الصحيح في tkinter"""
    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(text)
    return reshaped[::-1]

# ---------------- ألوان التصميم ----------------
CLR_BG = "#020617"
CLR_CARD = "#0F172A"
CLR_ACCENT = "#FF4D4D"
CLR_TEXT = "#F8FAFC"
CLR_SUB = "#94A3B8"

# ---------------- تهيئة النافذة الرئيسية ----------------
root = tk.Tk()
root.title("Spy Game")
root.geometry("720x1280")
root.configure(bg=CLR_BG)

main_frame = tk.Frame(root, bg=CLR_BG)
main_frame.pack(fill="both", expand=True)

# ---------------- متغيرات اللعبة ----------------
players_var = tk.IntVar(value=5)
spies_var = tk.IntVar(value=1)
minutes_var = tk.IntVar(value=2)
saved_names = []
session_players = []
current_idx = 0
timer_active = False

# حجم ثابت للصور (يناسب الشاشة مع ترك مساحة للنصوص)
IMG_WIDTH = 680
IMG_HEIGHT = 1000

# قائمة الصور السرية المتاحة (بدون صورة الجاسوس)
available_secrets = []

def refresh_available_secrets():
    global available_secrets
    try:
        all_imgs = [f for f in os.listdir(PLAYER_DIR) if f.lower().endswith(EXTS)]
        # افتراض أن صورة الجاسوس تبدأ بـ "26051997"
        spy_img = next((f for f in all_imgs if f.startswith("26051997")), all_imgs[0] if all_imgs else None)
        if spy_img:
            available_secrets = [f for f in all_imgs if f != spy_img]
        else:
            available_secrets = all_imgs[:]
        random.shuffle(available_secrets)
    except FileNotFoundError:
        available_secrets = []

# كاش للصور لتجنب إعادة التحميل
image_cache = {}

def get_img(folder, name_with_ext, size=None):
    """تحميل الصورة من المجلد مع الاحتفاظ بنسخة في الكاش"""
    if size is None:
        size = (IMG_WIDTH, IMG_HEIGHT)
    cache_key = (folder, name_with_ext, size)
    if cache_key in image_cache:
        return image_cache[cache_key]

    path = os.path.join(folder, name_with_ext)
    # إذا كان الملف بدون امتداد، نحاول إضافة الامتدادات المدعومة
    if not any(name_with_ext.endswith(ex) for ex in EXTS):
        for ex in EXTS:
            test_path = os.path.join(folder, name_with_ext + ex)
            if os.path.exists(test_path):
                path = test_path
                break

    if os.path.exists(path):
        img = Image.open(path)
        # تحجيم الصورة مع الحفاظ على نسبة الطول إلى العرض
        img.thumbnail(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        image_cache[cache_key] = photo
        return photo
    return None

def enforce_rules(*args):
    p = players_var.get()
    if p < 3:
        players_var.set(3)
    if p > 12:
        players_var.set(12)
    max_s = (players_var.get() - 1) // 2
    if spies_var.get() > max_s:
        spies_var.set(max_s)
    if spies_var.get() < 1:
        spies_var.set(1)

players_var.trace_add("write", enforce_rules)
spies_var.trace_add("write", enforce_rules)

# ---------------- الشاشة الرئيسية ----------------
def show_home():
    global timer_active
    timer_active = False
    for w in main_frame.winfo_children():
        w.destroy()

    content = tk.Frame(main_frame, bg=CLR_BG)
    content.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(content, text=ar("الـجـاسـوس"), font=("Times New Roman", 32, "bold"),
             fg=CLR_ACCENT, bg=CLR_BG).pack(pady=(0, 15))

    tk.Label(content, text="DZ VERSION", font=("Georgia", 18, "italic"),
             fg=CLR_SUB, bg=CLR_BG).pack(pady=10)

    card = tk.Frame(content, bg=CLR_CARD, padx=20, pady=20,
                    highlightthickness=1, highlightbackground="#1E293B")
    card.pack(pady=15, fill="x")

    def create_row(label, var):
        f = tk.Frame(card, bg=CLR_CARD)
        f.pack(pady=6, fill="x")
        tk.Label(f, text=ar(label), font=("Times New Roman", 12),
                 fg=CLR_TEXT, bg=CLR_CARD, width=12, anchor="e").pack(side="right")
        tk.Button(f, text="+", bg="#1E293B", fg=CLR_ACCENT,
                  font=("Verdana", 11, "bold"), bd=0, width=3,
                  command=lambda: var.set(var.get() + 1)).pack(side="right", padx=5)
        tk.Label(f, textvariable=var, font=("Verdana", 13, "bold"),
                 fg=CLR_ACCENT, bg=CLR_CARD, width=3).pack(side="right")
        tk.Button(f, text="-", bg="#1E293B", fg=CLR_ACCENT,
                  font=("Verdana", 11, "bold"), bd=0, width=3,
                  command=lambda: var.set(var.get() - 1)).pack(side="right", padx=5)

    create_row("عدد اللاعبين", players_var)
    create_row("عدد الجواسيس", spies_var)
    create_row("وقت النقاش", minutes_var)

    tk.Button(content, text=ar("إبدأ المهمة"), font=("Times New Roman", 15, "bold"),
              bg=CLR_ACCENT, fg="white", bd=0, padx=40, pady=10,
              command=show_names).pack(pady=20)

    tk.Label(content, text="By Bensahla Sidahmed", font=("Georgia", 10, "italic"),
             fg=CLR_SUB, bg=CLR_BG).pack(pady=5)

# ---------------- شاشة إدخال الأسماء ----------------
def show_names():
    for w in main_frame.winfo_children():
        w.destroy()

    content = tk.Frame(main_frame, bg=CLR_BG)
    content.pack(fill="both", expand=True)

    tk.Label(content, text=ar("أسماء الفريق"), font=("Times New Roman", 28, "bold"),
             fg=CLR_TEXT, bg=CLR_BG).pack(pady=20)

    container = tk.Frame(content, bg=CLR_BG)
    container.pack(fill="both", expand=True, padx=20)

    canvas = tk.Canvas(container, bg=CLR_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=CLR_BG)

    scrollable_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def _configure_canvas(event):
        canvas.itemconfig("all", width=event.width)

    canvas.bind("<Configure>", _configure_canvas)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    num = players_var.get()
    global saved_names
    current_entries = []

    if not saved_names or len(saved_names) != num:
        saved_names = [f"Player {i+1}" for i in range(num)]

    def on_entry_click(entry, default_text):
        def handler(event):
            if entry.get() == default_text:
                entry.delete(0, tk.END)
        return handler

    for i in range(num):
        row = tk.Frame(scrollable_frame, bg=CLR_CARD, pady=10, padx=15,
                       highlightthickness=1, highlightbackground="#1E293B")
        row.pack(pady=5, fill="x")

        ent = tk.Entry(row, font=("Times New Roman", 14), bg=CLR_CARD, fg=CLR_ACCENT,
                       bd=0, justify="right", insertbackground="white")
        default_text = saved_names[i]
        ent.insert(0, default_text)
        ent.bind("<FocusIn>", on_entry_click(ent, default_text))
        ent.pack(side="right", fill="x", expand=True)
        current_entries.append(ent)

    btn_frame = tk.Frame(content, bg=CLR_BG, pady=20)
    btn_frame.pack(fill="x")

    tk.Button(btn_frame, text=ar("توزيع"), bg=CLR_ACCENT, fg="white",
              font=("Times New Roman", 15, "bold"), padx=40, pady=10, bd=0,
              command=lambda: prep_game([e.get() for e in current_entries])
              ).pack(side="right", padx=10)

    tk.Button(btn_frame, text=ar("رجوع"), bg="#1E293B", fg=CLR_SUB,
              font=("Times New Roman", 15, "bold"), padx=40, pady=10, bd=0,
              command=show_home).pack(side="left", padx=10)

# ---------------- إعداد جولة جديدة ----------------
def prep_game(names_list):
    global saved_names, session_players, current_idx, available_secrets
    saved_names = names_list
    random.seed(time.time_ns())
    random.shuffle(saved_names)

    try:
        all_imgs = [f for f in os.listdir(PLAYER_DIR) if f.lower().endswith(EXTS)]
        # تحديد صورة الجاسوس (التي تبدأ بـ 26051997)
        spy_img = next((f for f in all_imgs if f.startswith("26051997")), all_imgs[0] if all_imgs else "spy")
        # تحديث قائمة الصور السرية
        if not available_secrets:
            refresh_available_secrets()
        # اختيار صورة سرية عشوائية
        if available_secrets:
            round_secret_img = random.choice(available_secrets)
            available_secrets.remove(round_secret_img)
        else:
            round_secret_img = "secret"
    except Exception:
        spy_img = "spy"
        round_secret_img = "secret"

    num = players_var.get()
    s_num = spies_var.get()
    roles = [spy_img] * s_num + [round_secret_img] * (num - s_num)
    random.shuffle(roles)
    session_players = list(zip(saved_names, roles))
    random.shuffle(session_players)
    current_idx = 0
    show_identity()

# ---------------- شاشة كشف الهوية ----------------
def show_identity():
    for w in main_frame.winfo_children():
        w.destroy()
    if current_idx >= len(session_players):
        show_timer()
        return

    content = tk.Frame(main_frame, bg=CLR_BG)
    content.pack(fill="both", expand=True)

    name, img_file = session_players[current_idx]

    tk.Label(content, text=ar(name), font=("Times New Roman", 28, "bold"),
             fg=CLR_ACCENT, bg=CLR_BG, wraplength=700).pack(pady=30)

    card_container = tk.Frame(content, bg=CLR_BG)
    card_container.pack(fill="both", expand=True, padx=20, pady=10)

    img_back = get_img(UI_DIR, "wajiha1")
    card_lbl = tk.Label(card_container, image=img_back, bg=CLR_BG, bd=0)
    if img_back:
        card_lbl.image = img_back
    card_lbl.place(relx=0.5, rely=0.5, anchor="center")

    shown = [False]

    def flip(e):
        if not shown[0]:
            img_secret = get_img(PLAYER_DIR, img_file)
            if img_secret:
                card_lbl.config(image=img_secret)
                card_lbl.image = img_secret
            else:
                card_lbl.config(text=img_file, fg="white", font=("Times New Roman", 20))
            shown[0] = True
        else:
            global current_idx
            current_idx += 1
            show_identity()

    card_lbl.bind("<Button-1>", flip)

    tk.Label(content, text=ar("إلمس الكرت لكشف السر"), font=("Times New Roman", 16),
             fg=CLR_SUB, bg=CLR_BG).pack(pady=20)

# ---------------- شاشة العداد (المؤقت) ----------------
def show_timer():
    global timer_active
    timer_active = True
    for w in main_frame.winfo_children():
        w.destroy()

    content = tk.Frame(main_frame, bg=CLR_BG)
    content.pack(fill="both", expand=True)

    tk.Label(content, text=ar("جاري النقاش"), font=("Times New Roman", 28, "bold"),
             fg=CLR_TEXT, bg=CLR_BG).pack(pady=30)

    center_frame = tk.Frame(content, bg=CLR_BG)
    center_frame.pack(expand=True)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("yellow.Horizontal.TProgressbar", background='#FFD700',
                    troughcolor=CLR_CARD, bordercolor=CLR_BG,
                    lightcolor='#FFD700', darkcolor='#FFD700')

    progress = ttk.Progressbar(center_frame, style="yellow.Horizontal.TProgressbar",
                               orient="horizontal", length=500, mode='determinate',
                               maximum=100, value=100)
    progress.pack(pady=20)

    lbl_counter = tk.Label(center_frame, text="", font=("Courier New", 36, "bold"),
                            fg=CLR_TEXT, bg=CLR_BG)
    lbl_counter.pack(pady=10)

    total_s = minutes_var.get() * 60
    current_s = [total_s]

    def update_timer():
        if not timer_active:
            return
        try:
            if current_s[0] <= 0:
                progress['value'] = 0
                lbl_counter.config(text="00:00", fg="#EF4444")
                return
            progress['value'] = (current_s[0] / total_s) * 100
            mins = int(current_s[0] // 60)
            secs = int(current_s[0] % 60)
            lbl_counter.config(text=f"{mins:02d}:{secs:02d}", fg=CLR_TEXT)
            current_s[0] -= 0.1
            root.after(100, update_timer)
        except:
            pass

    update_timer()

    def on_enter_green(e):
        new_round_btn.config(bg="#32CD32", fg="white", relief="ridge", bd=2)

    def on_leave_green(e):
        new_round_btn.config(bg="#2E7D32", fg="white", relief="flat", bd=0)

    new_round_btn = tk.Button(content, text=ar("جولة أخرى"), bg="#2E7D32", fg="white",
                              font=("Times New Roman", 20, "bold"), padx=60, pady=15, bd=0,
                              cursor="hand2", activebackground="#32CD32", activeforeground="white",
                              command=show_home)
    new_round_btn.pack(pady=40)
    new_round_btn.bind("<Enter>", on_enter_green)
    new_round_btn.bind("<Leave>", on_leave_green)

# ---------------- بدء التطبيق ----------------
if __name__ == "__main__":
    refresh_available_secrets()   # تحميل قائمة الصور عند البداية
    show_home()
    root.mainloop()