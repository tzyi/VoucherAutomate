#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import ctypes
import json
import logging
import time
from ctypes import wintypes

from pywinauto import Application, timings
from pywinauto.keyboard import send_keys

import settings

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# 對整個 process 關閉 IME，避免中文組字干擾 send_keys
try:
    ctypes.windll.imm32.ImmDisableIME(-1)
except Exception:
    pass

# 調低 pywinauto 內建等待（預設偏保守）
timings.Timings.after_setfocus_wait = 0.02
timings.Timings.after_clickinput_wait = 0.05
timings.Timings.after_sendkeys_key_wait = 0.005
timings.Timings.window_find_timeout = 10

je_param = {
    "body_sleep": settings.BODY_SLEEP,
    "debit_credit": 1,
    "debit_credit_sleep": settings.DEBIT_CREDIT_SLEEP,
    "account_code": "",
    "account_code_sleep": settings.ACCOUNT_CODE_SLEEP,
    "description": "",
    "description_sleep": settings.DESCRIPTION_SLEEP,
    "dept_code": '',
    "dept_sleep": settings.DEPT_SLEEP,
    "amount": 0,
    "amount_sleep": settings.AMOUNT_SLEEP,
    "project_code": "",
    "project_code_sleep": settings.PROJECT_CODE_SLEEP,
    "line_note": "",
    "line_note_sleep": settings.LINE_NOTE_SLEEP
}

_window_cache = {"app": None, "window": None}


def get_window(force_refresh=False):
    """連接應用並取得主視窗（快取重用）"""
    if not force_refresh and _window_cache["window"] is not None:
        try:
            # 驗證視窗仍有效
            _window_cache["window"].window_text()
            return _window_cache["window"]
        except Exception:
            logger.warning("快取視窗已失效，重新連接...")

    app = Application(backend="uia").connect(title_re=settings.APP_TITLE_RE)
    window = app.window(title_re=settings.APP_TITLE_RE)
    _window_cache["app"] = app
    _window_cache["window"] = window
    return window


# ---------- 剪貼簿貼上（避開 IME 影響，中文瞬間送達）----------
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

_user32 = ctypes.windll.user32
_kernel32 = ctypes.windll.kernel32

_user32.OpenClipboard.argtypes = [wintypes.HWND]
_user32.OpenClipboard.restype = wintypes.BOOL
_user32.EmptyClipboard.restype = wintypes.BOOL
_user32.CloseClipboard.restype = wintypes.BOOL
_user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
_user32.SetClipboardData.restype = wintypes.HANDLE
_kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
_kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
_kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
_kernel32.GlobalLock.restype = wintypes.LPVOID
_kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]


def _set_clipboard_text(text: str):
    data = text.encode('utf-16-le') + b'\x00\x00'
    if not _user32.OpenClipboard(0):
        raise RuntimeError("OpenClipboard 失敗")
    try:
        _user32.EmptyClipboard()
        h_mem = _kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not h_mem:
            raise RuntimeError("GlobalAlloc 失敗")
        ptr = _kernel32.GlobalLock(h_mem)
        ctypes.memmove(ptr, data, len(data))
        _kernel32.GlobalUnlock(h_mem)
        if not _user32.SetClipboardData(CF_UNICODETEXT, h_mem):
            raise RuntimeError("SetClipboardData 失敗")
    finally:
        _user32.CloseClipboard()


def paste_text(text: str):
    """把文字放到剪貼簿並以 Ctrl+V 貼上（比 send_keys 穩定且瞬間完成）"""
    _set_clipboard_text(text)
    send_keys("^v")


def click_body(body_sleep=0.3, voucher_idx=1, line_idx=1):
    """第1步：點擊 Body 區域 (TFDBGrid) 後按 ENTER 進入編輯模式"""
    prefix = f"[第{voucher_idx}筆傳票/第{line_idx}筆明細]"
    logger.info(f"{prefix} 【第1步】點擊 Body 區域")

    try:
        window = get_window()
        logger.debug(f"{prefix} ✓ 已連接: {window.window_text()}")

        # AutomationId 會變動，直接用 ClassName TFDBGrid 查找
        matches = window.descendants(class_name="TFDBGrid")
        logger.debug(f"{prefix} 找到 {len(matches)} 個 TFDBGrid 元件")
        if not matches:
            raise RuntimeError("找不到 Body 元件，請確認頁面已開啟正確的傳票明細列")

        body_ctrl = matches[0]
        logger.debug(f"{prefix} 點擊 Body 元件...")
        body_ctrl.click_input()
        logger.debug(f"{prefix} ✓ 點擊成功")

        send_keys("{ENTER}")
        logger.debug(f"{prefix} ✓ 已按 ENTER")

        time.sleep(body_sleep)
        logger.debug(f"{prefix} ✓ 【第1步】完成")

    except Exception as e:
        logger.error(f"{prefix} ✗ 【第1步】失敗: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


def debit_credit_input(debit_credit=2, debit_credit_sleep=0, voucher_idx=1, line_idx=1):
    """第2步：借貸 (TwwDBComboBox)"""
    prefix = f"[第{voucher_idx}筆傳票/第{line_idx}筆明細]"
    logger.info(f"{prefix} 【第2步】借貸 - 輸入值: {debit_credit}")

    try:
        window = get_window()
        matches = window.descendants(class_name="TwwDBComboBox")
        logger.debug(f"{prefix} 找到 {len(matches)} 個 TwwDBComboBox 元件")
        if not matches:
            raise RuntimeError("找不到借貸元件")

        dc_ctrl = matches[0]
        dc_ctrl.set_focus()

        # 用 send_keys 模擬鍵盤輸入，觸發 ComboBox 的資料綁定查找
        # （set_edit_text 只會寫 edit 部分文字、不會觸發 lookup，造成顯示值與底層值不一致）
        send_keys("^a")
        send_keys(str(debit_credit))
        send_keys("{ENTER}")
        logger.debug(f"{prefix} ✓ 輸入: {debit_credit}")

        if debit_credit_sleep:
            time.sleep(debit_credit_sleep)
        logger.debug(f"{prefix} ✓ 【第2步】完成")

    except Exception as e:
        logger.error(f"{prefix} ✗ 【第2步】失敗: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


def account_code_input(account_code=6211, account_code_sleep=0.8, voucher_idx=1, line_idx=1):
    """第3步：科目編號（焦點已在欄位上，靠鍵盤輸入）"""
    prefix = f"[第{voucher_idx}筆傳票/第{line_idx}筆明細]"
    logger.info(f"{prefix} 【第3步】科目編號 - 輸入值: {account_code}")

    try:
        send_keys("^a")
        send_keys(str(account_code))
        send_keys("{ENTER}")
        # 科目編號 ENTER 後鼎新會去 DB 查科目名稱，需要等待
        time.sleep(account_code_sleep)
        logger.debug(f"{prefix} ✓ 【第3步】完成")

    except Exception as e:
        logger.error(f"{prefix} ✗ 【第3步】失敗: {type(e).__name__}: {e}")
        raise


def description_input(description='這是一個摘要內容', description_sleep=0.3, voucher_idx=1, line_idx=1):
    """第4步：摘要（中文用剪貼簿貼上）"""
    prefix = f"[第{voucher_idx}筆傳票/第{line_idx}筆明細]"
    logger.info(f"{prefix} 【第4步】摘要 - 輸入值: {description!r}")

    try:
        if description == '':
            send_keys("{ENTER}")
        else:
            send_keys(description, with_spaces=True)
            send_keys("{ENTER}")

        # 鼎新 Grid cell 需要第二個 ENTER 才會離開編輯模式到下一欄
        send_keys("{ENTER}")

        if description_sleep:
            time.sleep(description_sleep)
        logger.debug(f"{prefix} ✓ 【第4步】完成")

    except Exception as e:
        logger.error(f"{prefix} ✗ 【第4步】失敗: {type(e).__name__}: {e}")
        raise


def dept_code_input(dept_code, dept_sleep, voucher_idx=1, line_idx=1):
    """第5步：部門"""
    prefix = f"[第{voucher_idx}筆傳票/第{line_idx}筆明細]"
    logger.info(f"{prefix} 【第5步】部門 - 輸入值: {dept_code}")

    try:
        if dept_code == '':
            logger.debug(f"{prefix} 部門為空值，不執行")
        else:
            send_keys(str(dept_code))
            send_keys("{ENTER}")

        time.sleep(dept_sleep)
        logger.debug(f"{prefix} ✓ 【第5步】完成")
    except Exception as e:
        logger.error(f"{prefix} ✗ 【第5步】失敗: {type(e).__name__}: {e}")
        raise


def amount_input(amount=999, amount_sleep=0.3, voucher_idx=1, line_idx=1):
    """第6步：金額"""
    prefix = f"[第{voucher_idx}筆傳票/第{line_idx}筆明細]"
    logger.info(f"{prefix} 【第6步】金額 - 輸入值: {amount}")

    try:
        send_keys(str(amount))
        send_keys("{ENTER}")
        if amount_sleep:
            time.sleep(amount_sleep)
        logger.debug(f"{prefix} ✓ 【第6步】完成")
    except Exception as e:
        logger.error(f"{prefix} ✗ 【第6步】失敗: {type(e).__name__}: {e}")
        raise


def project_code_input(project_code='2018-002', project_code_sleep=0.3, voucher_idx=1, line_idx=1):
    """第7步：專案代號"""
    prefix = f"[第{voucher_idx}筆傳票/第{line_idx}筆明細]"
    logger.info(f"{prefix} 【第7步】專案代號 - 輸入值: {project_code!r}")

    try:
        if project_code == '':
            send_keys("{ENTER}")
        else:
            send_keys(str(project_code), with_spaces=True)
            send_keys("{ENTER}")

        if project_code_sleep:
            time.sleep(project_code_sleep)
        logger.debug(f"{prefix} ✓ 【第7步】完成")
    except Exception as e:
        logger.error(f"{prefix} ✗ 【第7步】失敗: {type(e).__name__}: {e}")
        raise


def line_note_input(line_note='我是備註', line_note_sleep=0.3, voucher_idx=1, line_idx=1):
    """第8步：備註"""
    prefix = f"[第{voucher_idx}筆傳票/第{line_idx}筆明細]"
    logger.info(f"{prefix} 【第8步】備註 - 輸入值: {line_note!r}")

    try:
        if line_note != '':
            send_keys(line_note, with_spaces=True)

        if line_note_sleep:
            time.sleep(line_note_sleep)
        logger.debug(f"{prefix} ✓ 【第8步】完成")
    except Exception as e:
        logger.error(f"{prefix} ✗ 【第8步】失敗: {type(e).__name__}: {e}")
        raise


def run_je(content, voucher_idx=1, line_idx=1):
    param = {**je_param, **{k: v for k, v in content.items() if k in je_param}}

    prefix = f"[第{voucher_idx}筆傳票/第{line_idx}筆明細]"
    logger.info("╔" + "=" * 58 + "╗")
    logger.info(f"║ {prefix} 會計傳票建立作業 自動化".center(58) + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.debug(f"{prefix} 參數: {param}")

    click_body(body_sleep=param["body_sleep"], voucher_idx=voucher_idx, line_idx=line_idx)
    debit_credit_input(debit_credit=param["debit_credit"], debit_credit_sleep=param["debit_credit_sleep"], voucher_idx=voucher_idx, line_idx=line_idx)
    account_code_input(account_code=param["account_code"], account_code_sleep=param["account_code_sleep"], voucher_idx=voucher_idx, line_idx=line_idx)
    description_input(description=param["description"], description_sleep=param["description_sleep"], voucher_idx=voucher_idx, line_idx=line_idx)
    dept_code_input(dept_code=param["dept_code"], dept_sleep=param["dept_sleep"], voucher_idx=voucher_idx, line_idx=line_idx)
    amount_input(amount=param["amount"], amount_sleep=param["amount_sleep"], voucher_idx=voucher_idx, line_idx=line_idx)
    project_code_input(project_code=param["project_code"], project_code_sleep=param["project_code_sleep"], voucher_idx=voucher_idx, line_idx=line_idx)
    line_note_input(line_note=param["line_note"], line_note_sleep=param["line_note_sleep"], voucher_idx=voucher_idx, line_idx=line_idx)

    logger.info(f"{prefix} ✓ 全部步驟執行完畢!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="會計傳票明細輸入工具")
    parser.add_argument("--content", type=str, default="",
                        help="明細內容 JSON 字串")
    args = parser.parse_args()

    if args.content:
        override = json.loads(args.content)
        je_param.update({k: v for k, v in override.items() if k in je_param})

    run_je(je_param)
