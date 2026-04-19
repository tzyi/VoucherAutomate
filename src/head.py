#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
from pywinauto.keyboard import send_keys

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def type_and_enter(text):
    logger.debug(f"輸入文字: '{text}'")
    send_keys(text, with_spaces=True, pause=0.05)
    time.sleep(0.3)
    send_keys('{ENTER}')
    logger.debug("✓ 按下 ENTER")
    time.sleep(0.5)


def type_date_and_enter(date_text):
    logger.debug(f"輸入日期: '{date_text}'")
    send_keys(date_text, with_spaces=True, pause=0.05)
    time.sleep(0.3)
    send_keys('{ENTER}')
    time.sleep(0.5)
    send_keys('{ENTER}')
    logger.debug("✓ 按下 ENTER")
    time.sleep(0.5)


def type_remark(text):
    logger.debug(f"輸入備註: '{text}'")
    send_keys(text, with_spaces=True, pause=0.05)
    time.sleep(1)
