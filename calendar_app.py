import tkinter as tk
from tkcalendar import Calendar

WINDOW_WIDTH = 250
WINDOW_HEIGHT = 280

def open_calendar(parent_window, date, label_widget=None):
    # Toplevelの初期化
    top = tk.Toplevel(parent_window)
    top.title("期限を選択")
    top.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    top.grab_set()

    calendar_widget = Calendar(
        top, 
        selectmode="day", 
        year=2026, 
        month=9, 
        day=22
    )
    calendar_widget.pack(fill="both", expand=True, padx=5, pady=5)

    def set_selected_date():
        selected = calendar_widget.get_date()
        date.set(selected)  # 変数に日付にする
        if label_widget:
            label_widget.configure(text=selected)
        top.destroy()
    
    select_button = tk.Button(
        top, 
        bg="#1f8610", 
        activebackground="#399411", 
        fg="white",
        text="決定", 
        font=("Meiryo", 10, "bold"), 
        command=set_selected_date
    )
    select_button.pack(pady=5)
