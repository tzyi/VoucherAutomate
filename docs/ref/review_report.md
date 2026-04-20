# Code Review — VoucherAutomate

## ▎重點聚焦

**效能、例外處理、Clean Architecture 合規性**

---

## 概覽

這是一個 Windows UI 自動化工具，透過 `pywinauto` 控制鼎新會計系統輸入傳票。
整體功能完整、GUI 設計美觀，但在**錯誤韌性、模組邊界與可維護性**上有幾個需要優先處理的問題。

---

## 🔴 嚴重問題 (Critical)

### 1. 主流程無 per-voucher 錯誤隔離 — `src/main.py:65-102`

```python
for i, voucher in enumerate(data):
    ...
    head_mod.type_and_enter(...)   # 若拋錯 → 整批中斷
    body_mod.run_je(...)           # 若拋錯 → 整批中斷
```

**問題：**
任何一張傳票失敗（UI 元素找不到、視窗跳開等）都會終止剩餘所有傳票，且沒有記錄成功/失敗。

**建議：**

* 使用 `try/except` 包覆每張傳票
* 記錄 error log
* 最後回傳成功/失敗清單

---

### 2. HTML 注入風險 — `gui.py:385-387`

```python
self.terminal.appendHtml(
    f'<span style="color:{color};">{msg}</span>'  # msg 未 escape！
)
```

**問題：**
若 log 訊息包含 `<`, `>`, `&`（例如 `path/to/<file>`），會破壞 HTML 結構甚至顯示錯誤。

**修正：**

```python
from html import escape
self.terminal.appendHtml(f'<span style="color:{color};">{escape(msg)}</span>')
```

---

### 3. 可變全域字典作為預設值 — `src/body.py:34-50`

```python
je_param = { "account_code": "", ... }  # module-level mutable

if __name__ == "__main__":
    je_param.update(...)  # 直接修改全域！
    run_je(je_param)
```

**問題：**

* 修改全域 mutable state
* 搭配 `importlib.reload()` 可能導致狀態殘留

---

## 🟠 高優先級問題 (High)

### 4. `head.py` 完全忽略 `settings.py`

```python
logging.basicConfig(level=logging.DEBUG)  # 硬編碼

def type_and_enter(text):
    time.sleep(0.3)
    time.sleep(0.5)
```

**問題：**

* sleep 全部硬編碼
* log level 強制 DEBUG（覆蓋 GUI 設定）
* 無 `try/except`，UI 操作失敗直接 crash

---

### 5. `toolbar_btn.py` 重複連接應用程式 — `src/toolbar_btn.py:107-148`

```python
app = Application(backend="uia").connect(...)  # 再次連接！
```

**問題：**

* 重複 connect
* 效能浪費
* 可能產生 race condition

**建議：**

* 共用 `body.py` 的 `get_window()` 快取

---

### 6. 多處呼叫 `logging.basicConfig()`

| 檔案                  | 行為                                      |
| ------------------- | --------------------------------------- |
| `main.py:13`        | `basicConfig(level=settings.LOG_LEVEL)` |
| `body.py:16`        | `basicConfig(level=settings.LOG_LEVEL)` |
| `head.py:8`         | `basicConfig(level=logging.DEBUG)` ❌    |
| `toolbar_btn.py:10` | `basicConfig(level=logging.DEBUG)` ❌    |

**問題：**

* 多處設定互相覆蓋
* GUI (`QtLogHandler`) 可能失效

**正確做法：**
👉 僅在入口 (`gui.py` 或 `main.py`) 初始化一次

---

### 7. Excel 解析無防護 — `src/read_excel.py:21-58`

```python
ws = wb["單身資料"]  # 可能 KeyError

row["傳票日期"].strftime(...)  # 可能 AttributeError

"amount": row["金額"] if row["金額"] is not None else ""
```

**問題：**

* 無工作表防護
* 型別未檢查
* 金額用 `""`（應為數值）

---

## 🟡 中優先級問題 (Medium)

### 8. 硬編碼 `time.sleep(5)` — `src/main.py:103`

```python
send_keys("{F12}")
time.sleep(5)
```

**問題：**

* 所有機器都等 5 秒 → 浪費時間

**建議：**

* 使用 `settings.SAVE_SLEEP`
* 或改為「UI 狀態偵測」

---

### 9. `_append_log` 每次強制捲動 — `gui.py:388`

```python
self.terminal.moveCursor(QTextCursor.End)
```

**問題：**

* 高頻 log 造成 UI 卡頓

**建議：**

* 判斷是否已在底部再 scroll

---

### 10. `cancel_operation` 命名誤導 — `src/toolbar_btn.py:17`

**問題：**

* 名稱 ≠ 行為（實際是找按鈕）

**建議：**

```python
find_toolbar_button()
```

---

### 11. `SettingsPage._save()` 無錯誤處理 — `gui.py:536-562`

```python
text = path.read_text(...)
path.write_text(...)
```

**問題：**

* 檔案被鎖定時會 crash

---

## 🏗 Clean Architecture 評估

### 目前架構問題

```
gui.py ──imports──> src/ (透過 sys.path)
main.py ──動態載入──> body / head / toolbar_btn
```

| 問題     | 說明                                 |
| ------ | ---------------------------------- |
| 動態模組載入 | `load_module()` 繞過 import，IDE 無法分析 |
| 模組副作用  | import 時執行 IME、timing、logging      |
| 無明確介面  | 依賴「函式名稱約定」，無 Protocol/ABC          |

---

## 📌 改善優先順序

| 優先    | 項目                            | 位置                  |
| ----- | ----------------------------- | ------------------- |
| 🔴 立即 | per-voucher try/except        | `main.py:65`        |
| 🟠 近期 | `head.py` 改用 settings + 加例外處理 | `src/head.py`       |
| 🟠 近期 | 移除多餘 `logging.basicConfig()`  | `src/*.py`          |
| 🟡 規劃 | Excel 解析防護 + 型別驗證             | `src/read_excel.py` |
| 🟡 規劃 | 移除動態模組載入                      | `src/main.py`       |

---

如果你要，我可以幫你做「下一步版本」👉
直接幫你改成 **幾乎不會壞（高韌性版）架構 + 範例 code**。
