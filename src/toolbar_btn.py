#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import argparse
from pywinauto import Application

import settings

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def cancel_operation(button_index=0):
    """
    點擊工具列 ToolBar1 內指定索引的按鈕

    參數：
    - button_index: 要點擊的按鈕索引（0 = 第一個，1 = 第二個，以此類推）
    """

    try:
        # 步驟 1: 連接應用
        logger.debug("=" * 60)
        logger.debug("開始連接應用...")
        app = Application(backend="uia").connect(
            title_re=settings.APP_TITLE_RE
        )
        logger.debug(f"✓ 成功連接應用")

        # 步驟 2: 取得視窗
        logger.debug("-" * 60)
        logger.info("取得主視窗...")
        window = app.window(title_re=settings.APP_TITLE_RE)
        logger.info(f"✓ 視窗標題: {window.window_text()}")
        logger.info(f"✓ 視窗 hwnd: {hex(window.handle)}")

        # 步驟 3: 取得 ToolBar
        logger.debug("-" * 60)
        logger.debug("查找工具列 'ToolBar1'...")
        toolbar = window.child_window(
            title="ToolBar1",
            control_type="ToolBar"
        )
        logger.debug(f"✓ 找到工具列: {toolbar.window_text()}")

        # 步驟 4: 在工具列中查找按鈕
        logger.debug("-" * 60)
        logger.debug("在工具列中查找按鈕...")

        logger.debug("  嘗試取得工具列中的所有按鈕...")
        buttons = toolbar.descendants(control_type="Button")
        logger.debug(f"  找到 {len(buttons)} 個按鈕")

        if buttons:
            # 遍歷顯示所有按鈕信息
            for idx, btn in enumerate(buttons):
                logger.debug(f"  [按鈕 {idx}]")
                logger.debug(f"    Name: '{btn.window_text()}'")
                try:
                    logger.debug(f"    AutomationId: {btn.get_automation_id()}")
                except:
                    pass
                logger.debug(f"    ClassName: {btn.class_name()}")
                logger.debug(f"    Is Enabled: {btn.is_enabled()}")
                try:
                    logger.debug(f"    Is Offscreen: {btn.element_info.element.CurrentIsOffscreen}")
                except Exception:
                    pass
                logger.debug(f"    Bounding Rect: {btn.rectangle()}")

            # 檢查索引是否有效
            if button_index >= len(buttons):
                logger.error(f"✗ 按鈕索引 {button_index} 超出範圍（共 {len(buttons)} 個按鈕）")
                return None

            # 選擇指定索引的按鈕
            logger.debug("-" * 60)
            logger.debug(f"選擇工具列中的第 {button_index} 個按鈕...")
            target_button = buttons[button_index]

            logger.info(f"✓ 成功找到目標按鈕!")
            logger.debug(f"  Name: '{target_button.window_text()}'")
            try:
                logger.debug(f"  AutomationId: {target_button.get_automation_id()}")
            except:
                pass
            logger.debug(f"  ClassName: {target_button.class_name()}")
            logger.debug(f"  Bounding Rect: {target_button.rectangle()}")

            return target_button

        else:
            logger.error("✗ 工具列中未找到任何按鈕")
            return None

    except Exception as e:
        logger.error(f"✗ 發生錯誤: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def find_button_alternative(button_index=0):
    """
    替代方式: 直接從視窗搜尋 Button 控件，根據 parent 篩選
    """

    try:
        logger.debug("=" * 60)
        logger.debug("使用替代方法: 直接搜尋視窗中的 Button...")

        app = Application(backend="uia").connect(
            title_re=settings.APP_TITLE_RE
        )
        window = app.window(title_re=settings.APP_TITLE_RE)

        # 直接搜尋所有 Button
        logger.debug("查找視窗中的所有 Button 控件...")
        all_buttons = window.descendants(control_type="Button")
        logger.debug(f"找到 {len(all_buttons)} 個 Button")

        # 篩選位於 ToolBar1 的按鈕
        logger.debug("篩選位於工具列的按鈕...")
        toolbar_buttons = []
        for btn in all_buttons:
            parent = btn.parent()
            if parent and parent.window_text() == "ToolBar1":
                toolbar_buttons.append(btn)
                logger.debug(f"  ✓ 找到工具列按鈕")

        logger.debug(f"工具列中共有 {len(toolbar_buttons)} 個按鈕")

        if toolbar_buttons and button_index < len(toolbar_buttons):
            target_button = toolbar_buttons[button_index]
            logger.debug(f"✓ 成功找到目標按鈕 (索引 {button_index})")
            return target_button

        return None

    except Exception as e:
        logger.error(f"✗ 發生錯誤: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="按鈕點擊工具 - 點擊工具列中指定索引的按鈕")
    parser.add_argument("--btn", type=int, default=0, help="按鈕索引 (預設: 0)")
    args = parser.parse_args()

    logger.debug("\n")
    logger.debug("╔" + "=" * 58 + "╗")
    logger.debug("║" + " " * 58 + "║")
    logger.debug("║  按鈕點擊工具".center(58) + "║")
    logger.debug("║" + " " * 58 + "║")
    logger.debug("╚" + "=" * 58 + "╝")
    logger.debug("\n")
    logger.debug(f"目標按鈕索引: {args.btn}\n")

    # 方法 1
    button = cancel_operation(button_index=args.btn)

    if button:
        logger.debug("\n" + "=" * 60)
        logger.debug("✓ 成功! 可進行後續操作")

        # 按鈕詳細信息
        logger.debug("\n按鈕詳細信息:")
        logger.debug(f"  Is Keyboard Focusable: {button.is_keyboard_focusable()}")
        logger.debug(f"  Has Keyboard Focus: {button.has_keyboard_focus()}")

        # 執行點擊操作
        logger.debug("\n" + "=" * 60)
        logger.debug("準備執行點擊操作...")

        try:
            logger.debug("使用 click_input() 方式 (物理點擊)...")
            button.click_input()
            logger.debug("✓ 成功執行點擊操作!")

        except Exception as click_error:
            logger.warning(f"click_input() 失敗: {click_error}")
            logger.debug("嘗試使用 click() 方式 (UIA Invoke Pattern)...")
            try:
                button.click()
                logger.debug("✓ 成功執行點擊操作!")
            except Exception as click_error2:
                logger.error(f"✗ click() 也失敗: {click_error2}")

    else:
        logger.warning("\n第一種方法失敗，嘗試替代方法...")
        button = find_button_alternative(button_index=args.btn)

        if button:
            logger.debug("\n✓ 替代方法成功!")

            # 執行點擊操作
            logger.debug("\n" + "=" * 60)
            logger.debug("準備執行點擊操作...")

            try:
                logger.debug("使用 click_input() 方式 (物理點擊)...")
                button.click_input()
                logger.debug("✓ 成功執行點擊操作!")

            except Exception as click_error:
                logger.warning(f"click_input() 失敗: {click_error}")
                logger.debug("嘗試使用 click() 方式 (UIA Invoke Pattern)...")
                try:
                    button.click()
                    logger.debug("✓ 成功執行點擊操作!")
                except Exception as click_error2:
                    logger.error(f"✗ click() 也失敗: {click_error2}")
        else:
            logger.error("\n✗ 無法找到目標按鈕")
