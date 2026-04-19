# UI

# Google Stitch
- 設計說明
```
我想使用python的PySide6設計一個Window桌面應用程式
請使用PySide6原生元件最好
我要有以下功能:

1. 畫面可以選擇Excel檔案，並且可以清除選擇檔案的按鈕
2. 有執行按鈕，也有中斷執行的按鈕
3. 下面有一個大文字框，可以即時看log

幫我設計符合現代UI/UX原則的UI
```

- 修改UI
```
1. 左邊分頁，只留下Processor，其他全部去除，並在最下面有一個Settings按鈕
2. 右上角3個按鈕都去除
3. Execition區塊，請把Pause按鈕去除，Terminate改成Stop，並且Execute Job改成Execute。然後Execute跟Stop請並排
4. 將Input Confuguration跟Execution區域高度縮減，讓下面顯示log的區塊高度增加
```


# GUI 

```
請參考 @stitch_pyside6_excel_processor\

將我的專案使用PySide6設計一個Window桌面應用程式
1. 畫面可以選擇Excel檔案，並且可以清除選擇檔案的按鈕，data = read_excel_mod.read_excel(str(BASE_DIR / "ACTI10_2.xlsx"))要可以變成抓取使用者選擇的檔案
2. 有執行按鈕，也有中斷執行的按鈕
3. 下面有一個大文字框，可以即時看log
4. 設定頁面中，讀取settings.py中的內容來設計頁面
```



# 產品圖片

```
幫我利用Canva生成產品介紹圖片
產品名稱叫VoucherAutomate
他是一款傳票入帳自動化的window桌面應用程式
只要讀取Excel就可以輕鬆入帳至ERP
圖片請生成16:9 橫幅
產品的圖片內容不要無中生有，要利用我上傳的圖片
```