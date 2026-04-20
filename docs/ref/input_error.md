# 效能問題改善

我寫一個python程序
功能主要是讀取Excel資料
用pywinauto去抓取鼎新SmartERP會計系統 Window桌面版應用程式的元件
將資料填到表格上
填寫每個欄位我都視為一個步驟
步驟跟步驟間
如果sleep不夠久
會有資料填錯的問題
但sleep太久，總執行時間過長
究竟是什麼情況會導致這情況?
可以幫我讓執行時間變快且不會出錯嗎?

-這是 pywinauto 自動化中非常經典的問題。讓我先分析原因，再提供解決方案。
為什麼會需要 sleep?
根本原因
pywinauto 在傳送輸入（SendKeys、type_keys、set_text）後，立即返回控制權給 Python，但 Windows 應用程式端的處理是非同步的。特別是鼎新這類基於 Delphi/PowerBuilder/VB 的傳統 ERP，會有以下狀況：

欄位 OnChange / OnExit 事件觸發資料庫查詢
例如輸入「料號」後，程式會去 DB 抓品名、單位、庫存，這期間 UI 被鎖住。如果你馬上填下一欄，前一欄的事件還沒跑完，輸入就會跑到錯的地方，或前一欄被回寫的值覆蓋掉你剛打的內容。
焦點（Focus）還沒真正轉移
Tab 或點擊後，Windows 訊息佇列需要時間處理 WM_KILLFOCUS → WM_SETFOCUS。太快送鍵盤訊息，會打到舊的控制項。
訊息佇列堆積
type_keys 是模擬鍵盤訊息一個個送，鼎新若在中間彈出驗證對話框（例如金額超限、日期格式），後續按鍵會被灌到對話框裡。
Grid / 表格控制項的 cell commit
表格欄位通常要等 cell editor 關閉（commit 到資料列）才算完成，這個過程沒有明確的視覺回饋。
輸入法（IME）干擾
中文 Windows 預設開啟注音/新注音，type_keys 送英數時如果 IME 在組字狀態，會吃字。

加速且穩定的策略
與其 time.sleep(固定秒數)，應該改成「等到條件成立才往下走」。核心是 wait_until + 讀值驗證。
pythonfrom pywinauto import Application, timings
from pywinauto.keyboard import send_keys
import time

# 1) 全域調低 pywinauto 內建等待（預設偏保守）
timings.Timings.after_setfocus_wait = 0.05
timings.Timings.after_clickinput_wait = 0.05
timings.Timings.after_sendkeys_key_wait = 0.01
timings.Timings.window_find_timeout = 10

def set_field(edit_ctrl, value, verify=True, timeout=3):
    """填欄位 + 驗證 + 觸發 OnChange"""
    edit_ctrl.set_focus()
    # 直接用 Win32 訊息寫入，比 type_keys 快且避開 IME
    edit_ctrl.set_edit_text(value)
    # 送 Tab 觸發 OnExit（鼎新多數欄位靠這個查 DB）
    send_keys('{TAB}')
    
    if verify:
        # 輪詢直到「下一個預期的欄位」被自動填上，或目前欄位值穩定
        end = time.time() + timeout
        while time.time() < end:
            if edit_ctrl.window_text() == value or edit_ctrl.window_text() != '':
                return
            time.sleep(0.03)  # 30ms 輪詢
幾個關鍵優化點
① 用 set_edit_text 取代 type_keys
set_edit_text 是直接 WM_SETTEXT，瞬間完成、不受 IME 影響；type_keys 是逐鍵模擬。差距可能是 50ms vs 500ms。但注意：有些鼎新欄位會檢查 WM_CHAR 才觸發驗證，這類欄位仍需 type_keys，填完後補 {TAB}。
② 等「狀態」而不是等「時間」

填完料號後，等「品名欄位」變成非空
送出後，等「儲存中」對話框消失：dlg.wait_not('visible', timeout=10)
用 child_window(...).wait('ready', timeout=5)

③ 關閉 IME
程式開頭加：
pythonimport ctypes
ctypes.windll.imm32.ImmDisableIME(-1)  # 對整個 process 關閉 IME
④ 用 uia 或 win32 backend 要選對
鼎新 SmartERP 多半是 Win32 backend 比較穩且快。uia 對舊版 Delphi 元件常常抓不到或很慢。用 Application(backend="win32")。
⑤ 批次處理時關閉畫面重繪
如果是 Grid 大量輸入，可以考慮 SendMessage(WM_SETREDRAW, False) 填完再開回來——但鼎新 Grid 不一定支援，要測試。
⑥ 避免 click_input，改用 click 或直接 set_focus
click_input 會真的移動滑鼠（吃 50-200ms），click 是送訊息（瞬間）。




看完你的程式碼，我找到幾個關鍵的效能殺手和不穩定的根源。我會先診斷，然後給你重構後的完整版本。
診斷：為什麼會慢又不穩
🔴 問題 1：每個 step 都重新 get_window() —— 這是最大殺手
pythondef click_body(...):
    window = get_window()  # ← 每次都重新搜尋整個 UI 樹
Application(backend="uia").connect(...) + window() 在 UIA backend 下每次都會掃描整個桌面的 UI 樹，鼎新這種大型 ERP 視窗通常要 0.5~2 秒。你有 8 個 step，光是連接就浪費 4~16 秒，而且每次都是這樣。
但 click_body 之後其實根本不需要再拿 window——後續 step 都是靠鍵盤 send_keys 操作當前焦點，window 物件完全沒用到。
🔴 問題 2：backend 用 uia 而不是 win32
你的元件都是 Delphi 的 TFDBGrid、TwwDBComboBox（從 class name 看得出來是 InfoPower + FireDAC），這是原生 Win32 控制項。用 uia backend 會慢 3~10 倍，而且 UIA 事件觸發不穩定。Delphi 程式用 win32 backend 才對。
🔴 問題 3：type_keys 的 pause=0.05 逐字延遲
pythondc_ctrl.type_keys(str(debit_credit), with_spaces=True, pause=0.05)
pause=0.05 表示每個字元間等 50ms。「這是一個摘要內容」6 個字 = 300ms，「2018-002」= 400ms。而且 type_keys 還要解析特殊字元。
🔴 問題 4：description_input 有重複 ENTER
pythonsend_keys("{ENTER}")   # 第 1 次
# ...
send_keys("{ENTER}")   # 第 2 次（在 time.sleep 前面，重複了！）
這個 bug 可能導致焦點多跳一格，後面的欄位全部對錯位置，然後你以為是 sleep 不夠所以加長等待——其實是邏輯錯了。
🔴 問題 5：中文用 send_keys 會不穩
send_keys('這是一個摘要') 在有 IME 的環境會出錯。中文應該直接用 set_edit_text 或 Windows 剪貼簿貼上。
🟡 問題 6：sleep 是固定時間而非等條件
科目編號按 ENTER 後，鼎新要去 DB 查科目名稱、判斷是否需要專案/部門，這個時間變動很大（DB 忙的時候 3 秒，閒的時候 0.3 秒）。固定 sleep(3) 是取最壞情況。

重構方案
核心改動：

連線一次、重用 window 物件
改用 win32 backend
摘要、備註等中文欄位改用剪貼簿貼上
純數字欄位（科目、金額）用 send_keys 但拿掉 pause
用「輪詢檢查狀態」取代固定 sleep
修掉重複 ENTER 的 bug
重構後的自動化腳本重構後的自動化腳本重點改動對照表
原版問題改動預期節省每個 step 都 get_window()全程連線 1 次、快取重用4~16 秒/筆backend="uia"改為 backend="win32"UI 查找快 3~10 倍type_keys(..., pause=0.05)改用 send_keys 無 pause，或剪貼簿貼上每字 50ms → 0ms中文用 send_keys 送字元改用 pyperclip + Ctrl+V穩定且瞬間完成固定 sleep(1~3)wait_idle 輪詢，條件達成就跳出平均省一半description_input 重複 ENTER移除多餘 ENTER修正資料錯位 bugIME 干擾ImmDisableIME 關閉避免吃字
一個重要提醒
原版的 description_input 有這段 bug（也可能是你總覺得「sleep 不夠就錯」的真正元兇）：
pythonsend_keys("{ENTER}")  # if/else 裡面按了一次
...
send_keys("{ENTER}")  # ⚠️ if/else 外面又按了一次！
這會讓焦點多跳一格，後面每一欄都對錯欄位——看起來就像「資料填錯」，但根本不是 sleep 的問題。加長 sleep 只是讓錯誤發生得更慢而已。
還能再優化的方向
如果這版跑起來還是不夠快，可以考慮：

直接綁定每個欄位的控制項，跳過 send_keys 用 set_edit_text——但這要先用 Inspect.exe 或 pywinauto 的 print_control_identifiers() 把每個欄位的 class + index 確認好（鼎新 Grid cell 可能不是獨立控制項，這招未必有效）。
用 Ctrl+V 貼所有欄位——連數字欄位也用剪貼簿，比 send_keys 更快。
監聽 Windows 訊息等待 DB 查詢完成——進階用法，透過 WaitForInputIdle 或監控 status bar 文字變化。
