# 功能
幫我撰寫一個je.py
並且需要寫logging
程式執行的步驟都要log顯示在terminal上
log格式 : 2026-04-18 00:25:41,445 - INFO - 這是log的內容

一開始宣告一個dict
```python
je_param = {
	"dc_num": 2,
	"dc_sleep": 1,
	"acc_code": 6211,
	"acc_code_sleep": 1,
	"summary": "這是一個摘要內容",
	"sum_sleep":1,
	"dept_code": 230,
	"dept_sleep": 1,
	"amount_num": 999,
	"amount_sleep": 1,
	"project_code": "2018-002",
	"project_sleep": 1,
	"note_text": "我是備註",
	"note_sleep": 1
}
```

## 第1步 click body
以下為借貸按鈕資訊
```
How found:	Mouse move (1296,627)
	hwnd=0x000502E2 32bit class="TFDBGrid" style=0x54310000 ex=0x200
Name:	""
ControlType:	UIA_PaneControlTypeId (0xC371)
LocalizedControlType:	"窗格"
BoundingRectangle:	{l:930 t:526 r:1901 b:765}
IsEnabled:	true
IsOffscreen:	false
IsKeyboardFocusable:	true
HasKeyboardFocus:	false
AccessKey:	""
ProcessId:	5616
RuntimeId:	[2A.502E2]
AutomationId:	"328418"
FrameworkId:	"Win32"
ClassName:	"TFDBGrid"
NativeWindowHandle:	0x502E2
ProviderDescription:	"[pid:5460,providerId:0x502E2 Main:Nested [pid:5616,providerId:0x502E2 Annotation(parent link):Microsoft: Annotation Proxy (unmanaged:uiautomationcore.dll); Main:Microsoft: MSAA Proxy (unmanaged:uiautomationcore.dll)]; Nonclient:Microsoft: Non-Client Proxy (unmanaged:uiautomationcore.dll); Hwnd(parent link):Microsoft: HWND Proxy (unmanaged:uiautomationcore.dll)]"
IsPassword:	false
HelpText:	""
IsDialog:	false
LegacyIAccessible.ChildId:	0
LegacyIAccessible.DefaultAction:	""
LegacyIAccessible.Description:	""
LegacyIAccessible.Help:	""
LegacyIAccessible.KeyboardShortcut:	""
LegacyIAccessible.Name:	""
LegacyIAccessible.Role:	用戶端 (0xA)
LegacyIAccessible.State:	可設定焦點 (0x100000)
LegacyIAccessible.Value:	""
Scroll.HorizontallyScrollable:	true
Scroll.HorizontalScrollPercent:	0.000000
Scroll.HorizontalViewSize:	0.781250
Scroll.VerticallyScrollable:	true
Scroll.VerticalScrollPercent:	0.000000
Scroll.VerticalViewSize:	99.900100
IsAnnotationPatternAvailable:	false
IsDragPatternAvailable:	false
IsDockPatternAvailable:	false
IsDropTargetPatternAvailable:	false
IsExpandCollapsePatternAvailable:	false
IsGridItemPatternAvailable:	false
IsGridPatternAvailable:	false
IsInvokePatternAvailable:	false
IsItemContainerPatternAvailable:	false
IsLegacyIAccessiblePatternAvailable:	true
IsMultipleViewPatternAvailable:	false
IsObjectModelPatternAvailable:	false
IsRangeValuePatternAvailable:	false
IsScrollItemPatternAvailable:	false
IsScrollPatternAvailable:	true
IsSelectionItemPatternAvailable:	false
IsSelectionPatternAvailable:	false
IsSpreadsheetItemPatternAvailable:	false
IsSpreadsheetPatternAvailable:	false
IsStylesPatternAvailable:	false
IsSynchronizedInputPatternAvailable:	false
IsTableItemPatternAvailable:	false
IsTablePatternAvailable:	false
IsTextChildPatternAvailable:	false
IsTextEditPatternAvailable:	false
IsTextPatternAvailable:	false
IsTextPattern2Available:	false
IsTogglePatternAvailable:	false
IsTransformPatternAvailable:	false
IsTransform2PatternAvailable:	false
IsValuePatternAvailable:	false
IsVirtualizedItemPatternAvailable:	false
IsWindowPatternAvailable:	false
IsCustomNavigationPatternAvailable:	false
IsSelectionPattern2Available:	false
FirstChild:	"" 編輯
LastChild:	(null) 捲動方塊
Next:	[null]
Previous:	[null]
Other Props:	Object has no additional properties
Children:	"" 編輯
	"垂直" 捲軸
	"水平" 捲軸
	(null) 捲動方塊
Ancestors:	"自訂資料" 窗格
	"" 索引標籤
	"" 窗格
	"會計傳票建立作業(ACTI10)[奧義測10]" 視窗
	"桌面 1" 窗格
	[ No Parent ]


```
撰寫一個def click_body(body_sleep=1)的函數

抓取body區域2

並click

在按下ENTER

並且sleep 1秒鐘



# 第2步 借貸

撰寫一個def dc(dc_num=2,dc_sleep=1)的函數

然後輸入2

按下ENTER

並且sleep 1秒鐘


# 第3步 科目編號

撰寫一個def account_code(acc_code=6211,acc_code_sleep=1)的函數

輸入6211

並按下ENTER

並且sleep 1秒鐘


---

# 第4步 摘要

撰寫一個def account_summary(summary='這是一個摘要內容',sum_sleep=1)的函數

若summary=''是空值

直接按下ENTER

並且sleep 1秒鐘

若summary='這是一個摘要內容'是有值

然後輸入這是一個摘要內容

並按下ENTER

並且sleep 1秒鐘


# 第5步 部門

撰寫一個def dept(dept_code=230,dept_sleep=1)的函數

然後輸入230

並按下ENTER

並且sleep 1秒鐘


# 第6步 金額

撰寫一個def amount(amount_num=999,amount_sleep=1)的函數

然後輸入999

並按下ENTER

並且sleep 1秒鐘





# 第7步 專案代號

撰寫一個def project(project_code='2018-002',project_sleep=1)的函數

若project_code=''是空值

直接按下ENTER

並且sleep 1秒鐘

若project_code='2018-002'是有值

然後輸入2018-002

並按下ENTER

並且sleep 1秒鐘


# 第8步 備註

撰寫一個def note(note_text='我是備註',note_sleep=1)的函數

若note_text=''是空值

直接顯示備註為空值，不執行輸入

若note_text='我是備註'是有值

然後輸入我是備註

並且sleep 1秒鐘

