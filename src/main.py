import importlib.util
import logging
import sys
import time
from pathlib import Path
from pywinauto.keyboard import send_keys

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR.parent))

import settings

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)
PYTHON = sys.executable


def load_module(filename, module_name):
    spec = importlib.util.spec_from_file_location(module_name, BASE_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def click_toolbar_btn(toolbar_mod, button_index=0):
    """找到工具列按鈕並點擊（原 02_toolbar_btn.py __main__ 的邏輯）"""
    button = toolbar_mod.cancel_operation(button_index=button_index)
    if button is None:
        button = toolbar_mod.find_button_alternative(button_index=button_index)
    if button is None:
        raise RuntimeError(f"找不到工具列按鈕 index={button_index}")

    try:
        button.click_input()
    except Exception:
        button.click()


def main(excel_path=None, stop_event=None):
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("開始執行會計傳票自動化作業")
    logger.info("=" * 60)

    # 預先載入所有模組
    read_excel_mod = load_module("read_excel.py", "read_excel_mod")
    toolbar_mod = load_module("toolbar_btn.py", "toolbar_mod")
    head_mod = load_module("head.py", "head_mod")
    body_mod = load_module("body.py", "body_mod")

    if excel_path is None:
        excel_path = str(BASE_DIR / "ACTI10_2.xlsx")
    logger.info(f"讀取 Excel: {excel_path}")
    data = read_excel_mod.read_excel(excel_path)
    total_vouchers = len(data)
    total_lines = sum(len(v["lines"]) for v in data)
    logger.info(f"共讀取 {total_vouchers} 張傳票，{total_lines} 筆明細")

    processed_vouchers = 0
    processed_lines = 0

    for i, voucher in enumerate(data):
        if stop_event is not None and stop_event.is_set():
            logger.warning("偵測到中斷訊號，停止執行")
            break
        logger.info(f"處理第 {i+1} 張傳票")
        # Step 2: 新增按鈕
        if i == 0:
            click_toolbar_btn(toolbar_mod, button_index=0)
        send_keys("{F5}")

        # Step 3: 輸入傳票單別
        head_mod.type_and_enter(str(voucher["voucher_type"]))

        # Step 4: 輸入傳票日期
        head_mod.type_date_and_enter(str(voucher["voucher_date"]))

        # Step 5: 輸入傳票備註
        remark = voucher["voucher_remark"]
        if remark != "":
            head_mod.type_remark(str(remark))

        # Step 6: 逐筆輸入明細
        lines = voucher["lines"]
        line_count = 0
        for line_idx, line in enumerate(lines, 1):
            if stop_event is not None and stop_event.is_set():
                logger.warning("偵測到中斷訊號，停止執行")
                break
            if line.get("account_code") == '':
                break
            body_mod.run_je(line, voucher_idx=i+1, line_idx=line_idx)
            send_keys("{ENTER}")
            line_count += 1

        processed_lines += line_count
        processed_vouchers += 1

        send_keys("{F12}")
        time.sleep(5)  # 等待儲存完成

    # 計算執行時間
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    logger.info("=" * 60)
    logger.info(f"執行時間 : {minutes}分{seconds}秒，共處理{processed_vouchers}張傳票，{processed_lines}筆明細")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

