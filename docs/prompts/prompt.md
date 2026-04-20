# prompts


# 01 傳票單別
```
幫我寫一個01.py抓取這個元件
使用者可以執行python 01.py --num 9101
就會在這元件上鍵盤輸入9101後在按下ENTER
```

---

# 02 日期

```
幫我寫一個02.py抓取這個元件
使用者可以執行python 02.py --date 20260408
就會在這元件上鍵盤輸入20260418
```

命令行参数

  - --date：要输入的日期（格式：YYYYMMDD，默认：20260418）
  - --auto-id：编辑框的 AutomationId（默认：786718）
  - --enter：是否在输入后按下 ENTER 键（可选）



---


# 03 備註
```
幫我寫一個03.py抓取這個元件
使用者可以執行python 03.py --text '這是一個備註'
就會在這元件上鍵盤輸入這是一個備註
python 03.py --text ''
也支持空字串

```

命令行参数

  - --text：要输入的备註文字（支持空字符串，默认为空）
  - --auto-id：编辑框的 AutomationId（默认：264684）


```
如果使用者執行python 03.py --text ''
--text參數是''
則就不要執行
直接log顯示 '沒有備註，不需要執行輸入'
```



# read excel

```
寫一個read_excel.py
幫我讀取
的內容
把它組成dict
然後print出來
```
```
幫我將key是借\貸，如果值是-1請幫我改成2
```

```
幫我做以下修改

1. 傳票日期的格式改成 '20260408'
2. 只要值是None都改成''空字串
3. 去除key是單號、序號、沖帳單別、科目名稱、立沖帳目、立沖帳目名稱、部門名稱
```


```
我想要key值是英文
幫我轉換為適當的英文
```

Key 對應如下：
| 原中文 | 英文 |
|--------|------|
| 傳票單別 | voucher_type |
| 傳票日期 | voucher_date |
| 備註 | voucher_remark |
| 明細 | lines |
| 借/貸 | debit_credit |
| 科目編號 | account_code |
| 摘要 | description |
| 部門 | dept_code |
| 金額 | amount |
| 專案代號 | project_code |
| 備註_明細 | line_note |


<!-- # 修改 06_je.py
```
幫我將執行01_read_excel.py 取得的data
``` -->



# 串接

```
幫我寫一個main.py


# step 1 取得data
執行 python 01_read_excel.py 取得data

for line in data:

  # step 2 新增按鈕
  執行 python 02_toolbar_btn.py --num 0

  # step 3 輸入傳票單別
  執行 python 03_voucher_type.py --num line[voucher_type]

  # step 4 輸入傳票日期
  執行 python 04_voucher_date.py --date line[voucher_date]

  # step 5 輸入傳票備註
  執行 python 05_voucher_remark.py --text line[voucher_remark]


  for j in line[lines]:
    # step 6 輸入明細
    幫我將06_je.py
    改成可執行python 06_je.py --content j

```

main.py 流程：
  1. 用 importlib 載入 01_read_excel.py 取得 data（因為 Python 模組名不能以數字開頭）                              
  2. 外層 loop 每張傳票執行 step 2–5（新增、單別、日期、備註）
  3. 內層 loop 每筆明細執行 06_je.py --content <json>                                                            
  
  06_je.py 改動：新增 --content 參數接受 JSON 字串，解析後 update 進 je_param（只會覆蓋已存在的
  key，避免注入非預期欄位）。

  注意事項：
  - 你的 prompt 寫 02_toolbar_btn.py --num 0，但該腳本實際參數名是 --btn，我用了正確的 --btn。
  - voucher_remark key 我跟 01_read_excel.py 目前使用的名字一致。



# 修改03 04 05

```
將pywinauto查找元件的功能去除
使用者執行python 01.py --num 9101
保留直接鍵盤輸入鍵盤輸入9101後在按下ENTER的動作即可

```

```
將pywinauto查找元件的功能去除
使用者可以執行python 04_voucher_date.py --date 20260408
保留鍵盤輸入20260418後在按下ENTER的動作即可

```

```
將pywinauto查找元件的功能去除
使用者可以執行python 05_voucher_remark.py --text '這是一個備註'
保留鍵盤輸入這是一個備註
若是python 05_voucher_remark.py --text ''，參數是空字串
不要執行
直接log顯示 '沒有備註，不需要執行輸入'結束

```



# 效能問題

```
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
```


# settings.py

```
幫我創建一個settings.py
裡面設定要包含:
1. logging可以自己選擇要DEBUG模式還是INFO
2. body_sleep、debit_credit_sleep、account_code_sleep、description_sleep、dept_sleep、amount_sleep、project_code_sleep、line_note_sleep可以在設定檔設定
``