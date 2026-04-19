import logging

# Logging 設定：可選 logging.DEBUG 或 logging.INFO
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# 應用程式視窗標題正則表達式
APP_TITLE_RE = "會計傳票建立作業"

# 各欄位輸入後的等待時間 (秒)
BODY_SLEEP = 0.3
DEBIT_CREDIT_SLEEP = 1.0
ACCOUNT_CODE_SLEEP = 2.0
DESCRIPTION_SLEEP = 1.0
DEPT_SLEEP = 2.0
AMOUNT_SLEEP = 1.0
PROJECT_CODE_SLEEP = 1.0
LINE_NOTE_SLEEP = 1.0
