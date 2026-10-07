import customtkinter as ctk
import subprocess
from PIL import Image, ImageTk
import calendar_app
from tkinter import messagebox
# import csv
from pathlib import Path
import sqlite3
import datetime
from plyer import notification


# 変数宣言
WINDOW_WIDTH = 1150
WINDOW_HEIGHT = 600
WHITE_COLOR = "#fbfbef"
CLEAR = "transparent"
TEXT_COLOR = "black"
TITLE_FONT = ("Meiryo", 30, "bold")
SUB_FONT = ("Meiryo", 25)
# SEARCH_FILE = Path("data.csv")
select_data_push = 0
HEADER = [
    ['食品名', 'カテゴリ', '区分', '期限', '数量']
]
CALENDAR_IMG = ctk.CTkImage(
    Image.open(r"img\calendar_image.png"), 
    size=(50, 50)
)
CATEGORY_LIST = [
    "野菜", 
    "肉", 
    "魚", 
    "菓子", 
    "飲み物"
]
WEIGHTS = [2, 2, 3, 3, 3, 2]

# customt kitnerの初期化
bg_window_frame = ctk.CTk()
bg_window_frame.resizable(False, False)
bg_window_frame.title("食品管理アプリ")
bg_window_frame.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+150+50")


limit_time = ctk.StringVar(value="[ 未設定 ]")

# sqliteの初期化

# データベースに接続
con = sqlite3.connect("data.db")

# カーソルを作成
cur = con.cursor()

# data = []
# res = cur.execute("SELECT add_food_name FROM food_data")
# for text in res.fetchall():
#     data.append(text[0])

# print(data)

# テーブルを作成
cur.execute("""
    CREATE TABLE IF NOT EXISTS food_data(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        add_food_name, 
        category, 
        select_type, 
        limit_time, 
        add_food_num, 
        left_data_time
    )
""")

# ファイルが無い場合はファイルを作成
# if not SEARCH_FILE.is_file():
#     with open("./data.csv", mode="w", newline='', encoding="UTF-8") as data_csv:
#         writer = csv.writer(data_csv)
#         writer.writerows(HEADER)

# 関数
def show_toast_message(message_title, message):
    # トーチ通知を表示
    notification.notify(
        title=message_title, 
        message=message, 
        app_name="食品期限管理アプリ", 
        timeout=5
    )

def run_calendar_app():
    # カレンダーアプリの実行
    calendar_app.open_calendar(bg_window_frame, limit_time, time_limit_label)

def limilt_time_up_date():
    # 残り日数の再計算
    cur.execute("SELECT CAST(limit_time AS TEXT) FROM food_data")
    row = cursor.fetchall()
    now = datetime.datetime.now()
    if row is not None:
        for id in range(len(row)):
            result_limit_time = 0
            temp_limit_time = row[id][0]
            temp_limit_time = datetime.strptime(temp_limit_time, "%Y/%m/%d")
            result_limit_time = temp_limit_time - now
            cur.execute("""
                UPDATE food_data SET left_data_time = ? WHERE id = ?
            """,(result_limit_time, id,))
    con.commit()

def push_add_food_info():
    # 入力欄などの値を取得して代入
    add_info_data = []
    
    add_info_data.append(
        [add_food_entry.get(), 
        category_combox.get(), 
        select_type.get(), 
        limit_time.get(), 
        add_food_num_entry.get()]
    )
    # print(add_info_data)
    input_is_error(add_info_data[0])

def show_error_message():
    # エラー時のメッセージ
    messagebox.showerror("警告", "入力されていないフィールドが存在します。 \n フィールドに値を入力してください")

def show_successed_message():
    # 成功時のメッセージ
    messagebox.showinfo("成功", "情報を追加しました。")

def input_db_data(data):
    # DBにデータを保存
    # print(data)
    temp_text = ""
    
    if data[2] == 1:
        temp_text="消費期限"
    elif data[2] == 2:
        temp_text="賞味期限"
    
    now = datetime.datetime.now()
    temp = datetime.datetime.strptime(data[3], "%Y/%m/%d")
    left_time = temp - now
    
    cur.execute("""
        INSERT INTO food_data VALUES(
            ?, ?, ?, ?, ?, ?, ?
        )
    """, (None, data[0], data[1], temp_text, data[3], data[4], str(left_time.days)))
    
    con.commit()
    
    update_data_list()

def input_is_error(data):
    # エラーかどうかの判定
    flag = False
    for row in data:
        if row == '' or row == "[ 未設定 ]":
            show_error_message()
            flag = False
            break
        else:
            flag = True
    
    if flag:
        input_db_data(data)
        show_successed_message()

def show_header_label():
    # ヘッダーの作成
    SHOW_HEADER = ["食品名", "カテゴリ", "区分", "期限", "数量", "残り日数"]
    
    header_frame = ctk.CTkFrame(
        master=main_right_frame, 
        bg_color=CLEAR, 
        border_width=1, 
        width=650, 
        height=50
    )
    header_frame.place(x=8, y=50)
    header_frame.grid_propagate(False)
    
    header_frame.grid_rowconfigure(0, weight=1)
    
    for col, w in enumerate(WEIGHTS):
        header_frame.grid_columnconfigure(col, weight=w)
    
    for i in range(len(WEIGHTS)):
        bg_frame = ctk.CTkFrame(
            master=header_frame, 
            fg_color=CLEAR, 
            corner_radius=0
        )
        bg_frame.grid(row=0, column=i, sticky="nsew", padx=3, pady=3)
        header_text_label = ctk.CTkLabel(
            master=bg_frame, 
            text=f"{SHOW_HEADER[i]}", 
            text_color=TEXT_COLOR, 
            font=("Meiryo", 17, "bold")
        )
        header_text_label.place(relx=0.5, rely=0.5, anchor="center")

def update_data_list():
    # フレーム内の更新
    for widget in scroll_list_frame.winfo_children():
        widget.destroy()
    for widget in message_scroll_frame.winfo_children():
        widget.destroy()
    show_data_list()
    show_message_frame()

def select_row(selected_data):
    # 選んでいるフレームを選択
    global select_data_push
    select_data_push = int(selected_data[0])
    update_data_list()

def push_delete():
    # 食品を削除
    global select_data_push
    
    if select_data_push == 0:
        messagebox.showwarning("警告", "削除する行を選択してください。")
        return
    delete_id = select_data_push
    cur.execute("DELETE FROM food_data WHERE id = ?", (delete_id,))
    con.commit()
    messagebox.showinfo("成功", "データを削除しました")
    update_data_list()

def push_increment():
    # 数量を1増やす
    global select_data_push
    
    if select_data_push == 0:
        messagebox.showwarning("警告", "編集する行を選択してください。")
        return
    
    increment_id = select_data_push
    cur.execute("""
        UPDATE food_data SET add_food_num = add_food_num + 1 WHERE id = ?
    """, (increment_id,))
    con.commit()
    messagebox.showinfo("成功", "数量を１増やしました")
    update_data_list()

def push_decrement():
    # 数量を1減らす
    global select_data_push
    
    if select_data_push == 0:
        messagebox.showwarning("警告", "編集する行を選択してください。")
        return
    
    decrement_id = select_data_push
    cur.execute("""
        UPDATE food_data SET add_food_num = add_food_num - 1 WHERE id = ?
    """, (decrement_id,))
    con.commit()
    messagebox.showinfo("成功", "数量を１減らました")
    update_data_list()

def show_data_list():
    # リストを表示
    global select_data_push
    cur.execute(
        "SELECT * FROM food_data ORDER BY CAST(left_data_time AS INTEGER) ASC"
    )
    data = cur.fetchall()
    
    # 食品情報を表示
    for row in range(len(data)):
        time_data = int(data[row][6])
        if time_data >= 7:
            bg_is_color = "#E2F0D9"
        elif time_data >= 3:
            bg_is_color = "#FFF2CC"
        elif time_data >= 1:
            bg_is_color = "#FFE699"
        elif time_data == 0:
            bg_is_color = "#FCE4D6"
        else:
            bg_is_color = "#F8CBAD"
        
        if select_data_push == int(data[row][0]):
            is_border_color = "black"
        else:
            is_border_color = bg_is_color
        
        bg_list_frame = ctk.CTkFrame(
            master=scroll_list_frame, 
            fg_color=bg_is_color, 
            border_width=2, 
            border_color=is_border_color
        )
        bg_list_frame.pack(pady=5, fill="x", expand=False)
        # bg_list_frame.grid(row=0, column=row, sticky="nsew", padx=3, pady=3)
        WEIGHTS_LISTE_VER = [4, 6, 3, 3, 4, 2]
        for col, w in enumerate(WEIGHTS_LISTE_VER):
            bg_list_frame.grid_columnconfigure(col, weight=w)
        
        row_item = data[row]
        click_row = lambda event, item=row_item: select_row(item)
        bg_list_frame.bind("<Button-1>", click_row)
        for i in range(len(WEIGHTS_LISTE_VER)):
            if i+1 == 6:
                if int(data[row][i+1]) <= -1:
                    temp_text = "期限切れ"
                elif int(data[row][i+1]) == 0:
                    temp_text = "本日期限切れ"
                else:
                    temp_text = f"あと{data[row][i+1]}日"
            else:
                temp_text = f"{data[row][i+1]}"
            
            text_label = ctk.CTkLabel(
                master=bg_list_frame, 
                text=temp_text, 
                text_color=TEXT_COLOR, 
                font=("Meiryo", 17, "bold"), 
                fg_color=CLEAR
            )
            text_label.grid(row=0, column=i, sticky="nsew", padx=5, pady=10)
            text_label.bind("<Button-1>", click_row)

def show_message_frame():
    # リスト内から賞味期限、消費期限が近いのを取得
    cur.execute("SELECT select_type, add_food_name, CAST(left_data_time AS INTEGER) FROM food_data ORDER BY CAST(left_data_time AS INTEGER) ASC")
    row = cur.fetchall()
    soon_limit_food_list = []
    if row is not None:
        for select_type, food_name, left_time in row:
            left_time = int(left_time)
            soon_limit_food_list.append([select_type, food_name, left_time])
    #print(soon_limit_food_list)
    for row in range(len(soon_limit_food_list)):
        food_limit = soon_limit_food_list[row][2]
        food_name = soon_limit_food_list[row][1]
        food_select_type = soon_limit_food_list[row][0]
        if food_limit >= 4:
            continue # 4日以上は表示しないため
        if food_limit <= -1:
            frame_fg_color = "#FF4D4D" # 期限切れ
        elif food_limit <= 0:
            frame_fg_color = "#FF9800" # 本日締め切り
        elif food_limit >= 1 and food_limit <= 3:
            frame_fg_color = "#FFC107" # 1日以上3日以下前
        
        sub_message_frame = ctk.CTkFrame(
            master=message_scroll_frame, 
            fg_color=frame_fg_color, 
            height=50
        )
        sub_message_frame.pack(pady=5, fill="x", expand=False)
        
        message_text = ""
        temp = soon_limit_food_list[row][1]
        if food_limit <= -1:
            message_text = f"{food_name}の{food_select_type}は期限切れです。"
        elif food_limit == 0:
            message_text = f"{food_name}の{food_select_type}は本日までです。"
        elif food_limit >= 1 and food_limit <= 3:
            message_text = f"{food_name}の{food_select_type}はあと3日以内です。"
        show_toast_message(f"{food_select_type}の通知", message_text)
        sub_message_label = ctk.CTkLabel(
            master=sub_message_frame, 
            text=message_text, 
            text_color=TEXT_COLOR, 
            font=("Meiryo", 18, "bold")
        )
        sub_message_label.pack(padx=5, pady=10)


# フレームの作成

main_window_frame = ctk.CTkFrame(
    master=bg_window_frame, 
    fg_color="#d5edc9"
)
main_window_frame.pack(fill="both")


# 左フレーム
main_left_frame = ctk.CTkFrame(
    master=main_window_frame, 
    fg_color=CLEAR, 
    width=WINDOW_WIDTH*0.4, 
    height=WINDOW_HEIGHT
)
main_left_frame.pack(side="left", fill="y")
main_left_frame.pack_propagate(False)

add_food_info = ctk.CTkFrame(
    master=main_left_frame, 
    fg_color=WHITE_COLOR, 
    width=WINDOW_WIDTH*0.4, 
    height=WINDOW_HEIGHT * 0.6, 
    border_color="#d1d0be", 
    border_width=2
)
add_food_info.pack(side="top", padx=10, pady=10)
add_food_info.pack_propagate(False)

message_info = ctk.CTkFrame(
    master=main_left_frame, 
    fg_color=WHITE_COLOR, 
    width=WINDOW_WIDTH*0.4, 
    height=WINDOW_HEIGHT*0.4, 
    border_color="#d1d0be", 
    border_width=2
)
message_info.pack(side="bottom", padx=10, pady=(5, 10))
message_info.pack_propagate(False)

# 右フレーム
main_right_frame = ctk.CTkFrame(
    master=main_window_frame, 
    fg_color=WHITE_COLOR, 
    width=WINDOW_WIDTH*0.7, 
    height=WINDOW_HEIGHT, 
    border_color="#d1d0be", 
    border_width=2
)
main_right_frame.pack(fill="both", padx=(5, 10), pady=10)
message_info.pack_propagate(False)


# 左フレームの処理

# 食品情報追加のラベル
add_title_label = ctk.CTkLabel(
    master=add_food_info, 
    fg_color=CLEAR, 
    text_color=TEXT_COLOR, 
    text="食品情報の追加", 
    font=TITLE_FONT
)
add_title_label.place(x=5, y=3)

# 追加する食品のエントリー
add_food_label = ctk.CTkLabel(
    master=add_food_info, 
    fg_color=CLEAR, 
    text_color=TEXT_COLOR, 
    text="食品名", 
    font=SUB_FONT
)
add_food_label.place(x=5, y=50)
add_food_entry = ctk.CTkEntry(
    master=add_food_info, 
    text_color=TEXT_COLOR, 
    width=215, 
    font=("Meiryo", 15)
)
add_food_entry.place(x=110, y=55)

# カテゴリのラベル
category_label = ctk.CTkLabel(
    master=add_food_info, 
    fg_color=CLEAR, 
    text_color=TEXT_COLOR, 
    text="カテゴリ", 
    font=SUB_FONT
)
category_label.place(x=5, y=100)

# カテゴリ選択のコムボックス
category_combox = ctk.CTkComboBox(
    master=add_food_info, 
    width=215, 
    values=CATEGORY_LIST
)
category_combox.place(x=110, y=104)

# 区分を選択するラベル
type_label = ctk.CTkLabel(
    master=add_food_info, 
    fg_color=CLEAR, 
    text_color=TEXT_COLOR, 
    text="区分", 
    font=SUB_FONT
)
type_label.place(x=5, y=150)

# 区分を選択するボタン

select_type = ctk.IntVar(value=1)

type_radio_button_no_eat = ctk.CTkRadioButton(
    master=add_food_info, 
    text_color=TEXT_COLOR, 
    text="消費期限", 
    font=("Meiryo", 20), 
    variable=select_type, value=1
)
type_radio_button_no_eat.place(x=75, y=153)

type_radio_button_no_taste = ctk.CTkRadioButton(
    master=add_food_info, 
    text_color=TEXT_COLOR, 
    text="賞味期限", 
    font=("Meiryo", 20), 
    variable=select_type, value=2)
type_radio_button_no_taste.place(x=210, y=153)

# 期限のラベル
time_limit_label_title = ctk.CTkLabel(
    master=add_food_info, 
    fg_color=CLEAR, 
    text_color=TEXT_COLOR, 
    text="期限", 
    font=SUB_FONT
)
time_limit_label_title.place(x=5, y=200)

# 期間を表示されるラベルを作成
time_limit_label = ctk.CTkLabel(
    master=add_food_info, 
    fg_color=CLEAR, 
    text_color=TEXT_COLOR, 
    textvariable=limit_time, 
    font=SUB_FONT
)
time_limit_label.place(x=70, y=200)

# カレンダーを表示させるボタンを作成
select_time_limit_button = ctk.CTkButton(
    master=add_food_info, 
    image=CALENDAR_IMG, 
    fg_color=CLEAR, 
    text="", 
    hover_color=("gray80", "gray30"), 
    width=50, 
    height=50, 
    command=run_calendar_app
)
select_time_limit_button.place(x=230, y=190)

# 数量のラベル
add_food_num_label = ctk.CTkLabel(
    master=add_food_info, 
    fg_color=CLEAR, 
    text_color=TEXT_COLOR, 
    text="数量", 
    font=SUB_FONT
)
add_food_num_label.place(x=5, y=250)

# 数量のエントリー
add_food_num_entry = ctk.CTkEntry(
    master=add_food_info, 
    text_color=TEXT_COLOR, 
    width=215, 
    font=("Meiryo", 15)
)
add_food_num_entry.place(x=105, y=253)

# 食品情報を追加するボタン
add_food_info_button = ctk.CTkButton(
    master=add_food_info, 
    fg_color="#1f8610", 
    hover_color="#399411", 
    text="追加する", 
    font=("Meiryo", 25, "bold"), 
    command=push_add_food_info
)
add_food_info_button.place(x=120, y=300)


# メッセージの覧フレーム
message_title_label = ctk.CTkLabel(
    master=message_info, 
    fg_color=CLEAR, 
    text_color=TEXT_COLOR, 
    text="通知情報", 
    font=TITLE_FONT
)
message_title_label.place(x=5, y=3)

# メッセージフレームのスクロールフレームを作成
message_scroll_frame = ctk.CTkScrollableFrame(
    master=message_info, 
    fg_color="white", 
    bg_color="white", 
    width=380, 
    height=1, 
    border_color="gray", 
    border_width=2
)
message_scroll_frame.pack(fill="both", padx=10, pady=(45, 5))

# show_message_frame()


# 右フレームの処理

# 食品情報一覧のフレーム
list_title_label = ctk.CTkLabel(
    master=main_right_frame, 
    fg_color=CLEAR, 
    text_color=TEXT_COLOR, 
    text="食品情報の一覧", 
    font=TITLE_FONT
)
list_title_label.place(x=5, y=3)

# スクロールするフレームの作成

show_header_label()

scroll_list_frame = ctk.CTkScrollableFrame(
    master=main_right_frame, 
    width=WINDOW_WIDTH*0.55, 
    height=WINDOW_HEIGHT*0.67, 
    bg_color="white", 
    fg_color="white", 
    border_color="gray", 
    border_width=1
)
scroll_list_frame.place(x=5, y=110)

delete_food_button = ctk.CTkButton(
    master=main_right_frame, 
    fg_color="#1f8610", 
    hover_color="#399411", 
    text="削除する", 
    font=("Meiryo", 25, "bold"), 
    command=push_delete
)
delete_food_button.place(x=5, y=530)

edit_label = ctk.CTkLabel(
    master=main_right_frame, 
    fg_color=CLEAR, 
    text_color=TEXT_COLOR, 
    text="数量の変更", 
    font=("Meiryo", 20, "bold")
)
edit_label.place(x=160, y=538)

edit_increment_num = ctk.CTkButton(
    master=main_right_frame, 
    text="⇧", 
    fg_color="gray", 
    hover_color="#333333", 
    text_color="black", 
    font=("Meiryo", 10, "bold"), 
    width=30, 
    height=20, 
    command=push_increment
)
edit_increment_num.place(x=265, y=530)

edit_decrement_num = ctk.CTkButton(
    master=main_right_frame, 
    text="⇩", 
    fg_color="gray", 
    hover_color="#333333",
    text_color="black", 
    font=("Meiryo", 10, "bold"), 
    width=30, 
    height=20, 
    command=push_decrement
)
edit_decrement_num.place(x=265, y=555)

show_data_list()
show_message_frame()


bg_window_frame.mainloop()
