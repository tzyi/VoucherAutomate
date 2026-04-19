# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 專案概述

**VoucherAutomate** 是一個 Windows UI 自動化工具，用於自動化會計傳票輸入。它從 Excel 檔案讀取傳票資料，並自動填寫鼎新會計系統的傳票單據。

## 架構設計

### 目錄結構

```
WinAuto/
├── gui.py                 # PySide6 GUI 應用（主入口點）
├── settings.py            # 集中配置檔案
├── requirements.txt       # 依賴套件
└── src/                   # 業務邏輯（由 main.py 動態載入）
    ├── main.py           # 傳票處理流程編排
    ├── read_excel.py     # 讀取並解析 Excel 檔案
    ├── head.py           # 輸入傳票頭部欄位（單別、日期、備註）
    ├── body.py           # 輸入傳票明細行項目（科目、金額等）
    └── toolbar_btn.py    # 處理工具列按鈕操作
```

### 核心設計模式

#### 1. 動態模組載入
`main.py` 使用 `importlib.util.spec_from_file_location()` 在執行時動態載入其他模組。這使得模組可以獨立測試、熱更新，且無需繁複的相對導入。

#### 2. 集中式配置管理
所有可配置的值都在 `settings.py` 中：
- **日誌設定**：`LOG_LEVEL`、`LOG_FORMAT`
- **欄位輸入延遲**：`BODY_SLEEP`、`ACCOUNT_CODE_SLEEP` 等（單位：秒）
- **應用程式標題**：`APP_TITLE_RE`（正則表達式，方便應用程式標題變更時修改）

#### 3. 導入路徑解析
- `gui.py` 將 `src/` 加入 `sys.path`，以便導入 src 中的模組
- `src/main.py` 在動態載入前將父目錄加入 `sys.path`，使所有動態載入的模組都能找到 `settings.py`
- 所有 src 模組都用 `import settings`（非相對導入），因為可能被動態載入

#### 4. 視窗快取與連接
`body.py` 實現了應用程式視窗的快取機制，避免頻繁重新連接，提高效能。首次連接時使用 pywinauto 的 UIAutomation 後端定位視窗，之後複用快取的連接。

#### 5. Qt 信號槽用於即時日誌
`gui.py` 定義 `QtLogHandler` 將日誌記錄轉換為 Qt 信號，ProcessorPage 的終端窗格即時渲染日誌並根據級別著色。

### 資料流程

```
1. 用戶在 GUI 選擇 Excel 檔案 → main() 函數
   ↓
2. read_excel.py 解析 Excel → 傳票資料結構
   ↓
3. main.py 迴圈遍歷傳票，對每張傳票：
   - toolbar_btn.py：點擊「新增」按鈕建立新傳票
   - head.py：輸入傳票單別、日期、備註
   - body.py：迴圈輸入每筆明細（科目、金額等）
   ↓
4. 日誌通過 Qt 信號發出，GUI 終端即時顯示進度
```

## 常用命令

### 環境設置
```bash
# 安裝依賴
pip install -r requirements.txt

# 驗證 pywinauto 可用
python -c "from pywinauto import Application; print('OK')"
```

### 執行應用程式

**GUI 模式**（推薦用於測試和監控）：
```bash
python gui.py
```
- 在「Browse」按鈕選擇 Excel 檔案
- 點擊「Execute」開始自動化
- 在終端窗格監控進度和日誌

**CLI 模式**（無頭批量處理）：
```bash
python src/main.py
# 或指定 Excel 路徑
python src/main.py --excel-path path/to/file.xlsx
```

### 單模組測試
```bash
# 測試 Excel 解析
python src/read_excel.py

# 測試工具列按鈕檢測（無需應用程式執行）
python src/toolbar_btn.py --btn 0

# 測試日誌輸出
python src/head.py

# 測試傳票明細輸入（需應用程式執行）
python src/body.py --content '{"account_code": "6211", "amount": 1000}'
```

## 重要實現細節

### 導入路徑解析機制

由於 src 模組存在於子目錄中，但可能被 `gui.py` 直接導入或被 `main.py` 動態載入，導入路徑的解析有特殊考量：

1. **gui.py 的做法**：
   ```python
   BASE_DIR = Path(__file__).parent
   sys.path.insert(0, str(BASE_DIR / "src"))
   import settings  # ← 現在可以找到 settings.py（在根目錄）
   import main      # ← 可以找到 src/main.py
   ```

2. **src/main.py 的做法**：
   ```python
   BASE_DIR = Path(__file__).parent  # ← src 目錄
   sys.path.insert(0, str(BASE_DIR.parent))  # ← 加入根目錄
   import settings  # ← 從根目錄讀取
   ```
   這樣動態載入的 `body.py` 等模組也能找到 `settings.py`。

### 應用程式視窗標題配置

應用程式視窗標題的正則表達式儲存在 `settings.APP_TITLE_RE`。若目標應用程式的標題變更，只需修改此設定即可。`body.py` 和 `toolbar_btn.py` 都透過此設定查找目標應用程式視窗：

```python
# body.py
app = Application(backend="uia").connect(title_re=settings.APP_TITLE_RE)
```

### PyAutomate 配置調優

- **後端**：使用 "uia"（UI Automation）以支援 Delphi 舊版應用程式
- **時序調整**（body.py）：
  ```python
  timings.Timings.after_setfocus_wait = 0.02
  timings.Timings.after_clickinput_wait = 0.05
  timings.Timings.after_sendkeys_key_wait = 0.005
  timings.Timings.window_find_timeout = 10
  ```

這些調整是針對鼎新系統表單狀態快速變化的特性而設的。若自動化變得不穩定，需增加延遲時間。

### 中文輸入處理（IME 禁用）

`body.py` 在程序啟動時禁用進程級的 IME（輸入法編輯器），防止中文組字干擾鍵盤輸入。對於中文文本，改用剪貼簿貼上（Ctrl+V）方式，確保瞬間送達：

```python
# 禁用 IME
ctypes.windll.imm32.ImmDisableIME(-1)

# 中文文本用剪貼簿貼上
def paste_text(text: str):
    _set_clipboard_text(text)
    send_keys("^v")
```

### 日誌系統架構

1. **初始化**（gui.py）：
   ```python
   root_logger = logging.getLogger()
   root_logger.setLevel(settings.LOG_LEVEL)  # 預設 INFO
   root_logger.addHandler(self.log_handler)
   ```

2. **QtLogHandler** 攔截所有日誌記錄並轉換為 Qt 信號，ProcessorPage 的 `_append_log()` 根據級別著色：
   - INFO：橙色
   - WARNING/ERROR：紅色
   - DEBUG：灰色

3. **日誌重新載入**：SettingsPage 中修改設定後，會通過 `importlib.reload(settings)` 重新載入設定並更新 root logger 的級別。

## 配置自定義

### 修改欄位輸入延遲

若目標應用程式回應較慢，可在 `settings.py` 調整各欄位的延遲時間（單位：秒）：

```python
ACCOUNT_CODE_SLEEP = 2.0   # 科目編號輸入後的等待時間
AMOUNT_SLEEP = 1.0         # 金額輸入後的等待時間
```

也可透過 GUI Settings 頁面動態修改，變更會自動寫入 `settings.py`。

### 應用程式標題變更

若應用程式視窗標題變更，只需更新 `settings.py`：

```python
APP_TITLE_RE = "新的應用程式標題正則表達式"
```

### 日誌級別切換

```python
LOG_LEVEL = logging.DEBUG   # 詳細日誌（測試時用）
LOG_LEVEL = logging.INFO    # 標準日誌（生產環境用）
```

## 常見開發工作流

### 添加新的傳票欄位

1. 在 `body.py` 定義新的輸入函數（如 `custom_field_input()`）
2. 將欄位名稱加入 `je_param` 字典，設定預設值
3. 在 `run_je()` 函數中調用新函數，按順序插入
4. 若該欄位需要可配置的延遲時間，在 `settings.py` 添加新設定，並在 `gui.py` 的 `SettingsPage.SLEEP_FIELDS` 列表中註冊

### 調試自動化流程

**問題：傳票輸入中途卡住或出錯**

1. 檢查目標應用程式是否正常執行且視窗焦點正確
2. 若是時序問題，在 `settings.py` 增加相關欄位的延遲時間
3. 若需詳細日誌，將 `LOG_LEVEL` 改為 `logging.DEBUG` 並重新運行

**問題：視窗連接失敗**

1. 驗證 `settings.APP_TITLE_RE` 與實際應用程式視窗標題相符
2. 執行 `python src/toolbar_btn.py --btn 0` 測試視窗檢測是否正常
3. 檢查 `body.py` 中的 `_window_cache` 是否成功快取視窗

### 修改 Excel 檔案結構

若 Excel 檔案的欄位結構變更，需修改 `read_excel.py` 的解析邏輯。該函數期望的標題列包括：

```python
# read_excel.py 中期望的欄位
"傳票日期", "傳票單別", "備註",  # 傳票級別
"借/貸", "科目編號", "摘要", "部門", "金額", "專案代號", "備註_2"  # 明細級別
```

若 Excel 檔案新增或移除欄位，需相應調整解析邏輯。

## 測試環境要求

- **Windows 系統**（pywinauto 依賴 Windows UIAutomation 框架）
- **鼎新會計傳票系統**：應用程式必須執行且視窗需能聚焦
- **Excel 檔案結構**：必須符合 `read_excel.py` 期望的欄位結構
- **PyAutomate 時序**：虛擬機器或舊機器可能需要增加延遲時間

## 關鍵檔案說明

| 檔案 | 職責 | 關鍵類/函數 |
|------|------|-----------|
| `gui.py` | PySide6 GUI 應用 | `MainWindow`, `ProcessorPage`, `SettingsPage`, `QtLogHandler`, `Worker` |
| `src/main.py` | 傳票流程編排 | `main()`, `load_module()`, `click_toolbar_btn()` |
| `src/read_excel.py` | Excel 解析 | `read_excel()`, `dedupe_headers()` |
| `src/head.py` | 傳票頭部輸入 | `type_and_enter()`, `type_date_and_enter()`, `type_remark()` |
| `src/body.py` | 傳票明細輸入 | `run_je()`, `get_window()`, `click_body()`, `account_code_input()` 等 8 個欄位函數 |
| `src/toolbar_btn.py` | 工具列操作 | `cancel_operation()`, `find_button_alternative()` |
| `settings.py` | 集中配置 | 日誌、欄位延遲、應用程式標題 |
