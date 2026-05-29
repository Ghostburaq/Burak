'================================================================
'  MiT Strom Schweiz — VBA Makro Auto-Installer
'  Doppelklick zum Installieren — fertig.
'  Benötigt: Excel ≥ 2010 + erlaubter VBA-Projektzugriff
'================================================================
Option Explicit

Dim fso, shell, scriptPath, xlsmPath, fileExists
Set fso   = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName)
xlsmPath   = scriptPath & "\CH_MiT_Strom_Customer.xlsm"

If Not fso.FileExists(xlsmPath) Then
    MsgBox "❌ Datei nicht gefunden:" & vbCrLf & xlsmPath & vbCrLf & vbCrLf & _
           "Bitte 'Install_VBA_Macros.vbs' im selben Ordner wie die .xlsm starten.", _
           vbCritical, "MiT Strom Installer"
    WScript.Quit 1
End If

Dim answer
answer = MsgBox("⚡ MiT Strom Schweiz — VBA Auto-Installer" & vbCrLf & vbCrLf & _
       "Installiert in CH_MiT_Strom_Customer.xlsm:" & vbCrLf & _
       "  • 7 VBA-Makros (Report, PDF, E-Mail, …)" & vbCrLf & _
       "  • 5 Buttons im 📄 Report Sheet" & vbCrLf & _
       "  • Auto-Refresh beim Öffnen" & vbCrLf & vbCrLf & _
       "Excel wird kurz geöffnet und automatisch wieder geschlossen." & vbCrLf & vbCrLf & _
       "Fortfahren?", _
       vbQuestion + vbYesNo + vbDefaultButton1, "MiT Strom Installer")
If answer <> vbYes Then WScript.Quit 0

Dim xl, wb, vbproj, codeMod, codeBody, ws, btn, line, lines, i

On Error Resume Next
Set xl = CreateObject("Excel.Application")
If Err.Number <> 0 Then
    MsgBox "❌ Excel konnte nicht gestartet werden." & vbCrLf & _
           "Stelle sicher dass Microsoft Excel installiert ist.", vbCritical
    WScript.Quit 1
End If
On Error Goto 0

xl.Visible = False
xl.DisplayAlerts = False
xl.AutomationSecurity = 1   ' msoAutomationSecurityLow

Set wb = xl.Workbooks.Open(xlsmPath)

' Check VBA project trust
On Error Resume Next
Set vbproj = wb.VBProject
If Err.Number <> 0 Then
    wb.Close False
    xl.Quit
    MsgBox "❌ Zugriff auf VBA-Projekt verweigert." & vbCrLf & vbCrLf & _
           "Bitte in Excel aktivieren:" & vbCrLf & _
           "Datei → Optionen → Trust Center → Trust Center-Einstellungen" & vbCrLf & _
           "→ Makro-Einstellungen → 'Zugriff auf Visual Basic-Projekt vertrauen' ✔" & vbCrLf & vbCrLf & _
           "Danach Installer erneut starten.", vbCritical
    WScript.Quit 1
End If
On Error Goto 0

' Remove existing module if present
On Error Resume Next
vbproj.VBComponents.Remove vbproj.VBComponents("MiT_Strom_Reports")
On Error Goto 0

' Add new standard module (vbext_ct_StdModule = 1)
Dim newMod
Set newMod = vbproj.VBComponents.Add(1)
newMod.Name = "MiT_Strom_Reports"
Set codeMod = newMod.CodeModule

' Build VBA source
codeBody = GetVBACode()
codeMod.AddFromString codeBody

' Wire up Workbook_Open auto-refresh
Dim thisWbCode
Set thisWbCode = vbproj.VBComponents("DieseArbeitsmappe").CodeModule
If thisWbCode Is Nothing Then Set thisWbCode = vbproj.VBComponents("ThisWorkbook").CodeModule

Dim openCode
openCode = "Private Sub Workbook_Open()" & vbCrLf & _
           "    On Error Resume Next" & vbCrLf & _
           "    Call UpdateReportTimestamp" & vbCrLf & _
           "    Worksheets(""📄 Report"").Activate" & vbCrLf & _
           "End Sub"
thisWbCode.AddFromString openCode

' Place buttons on 📄 Report sheet
On Error Resume Next
Set ws = wb.Worksheets("📄 Report")
If Err.Number <> 0 Then
    Set ws = wb.Worksheets(4)
    Err.Clear
End If
On Error Goto 0

' Clean up any old buttons
Dim shp
For Each shp In ws.Shapes
    If InStr(shp.Name, "BtnMiT_") = 1 Then shp.Delete
Next

Call AddBtn(ws, "BtnMiT_Generate", "🔄 Report aktualisieren",  10, 660, 200, 32, "GenerateFullReport")
Call AddBtn(ws, "BtnMiT_PDF",      "📄 Report → PDF",          220, 660, 180, 32, "ExportReportToPDF")
Call AddBtn(ws, "BtnMiT_FullPDF",  "📦 Komplett-PDF",          410, 660, 160, 32, "ExportFullPackageToPDF")
Call AddBtn(ws, "BtnMiT_Mail",     "📧 Per E-Mail senden",     580, 660, 180, 32, "EmailReport")
Call AddBtn(ws, "BtnMiT_Stats",    "⚡ Quick Stats",            10, 700, 160, 32, "QuickStats")
Call AddBtn(ws, "BtnMiT_Add",      "➕ Neuer Deal",            180, 700, 160, 32, "AddNewDeal")

' Save & close
wb.Save
wb.Close True
xl.Quit
Set xl = Nothing

MsgBox "✅ VBA-Makros + Buttons erfolgreich installiert!" & vbCrLf & vbCrLf & _
       "Öffne jetzt 'CH_MiT_Strom_Customer.xlsm' und klicke auf die" & vbCrLf & _
       "Buttons im Sheet «📄 Report».", vbInformation, "MiT Strom Installer"

'================================================================
Sub AddBtn(targetWs, btnName, caption, leftPx, topPx, w, h, macroName)
    Dim btn
    Set btn = targetWs.Buttons.Add(leftPx, topPx, w, h)
    btn.Name = btnName
    btn.Caption = caption
    btn.OnAction = macroName
    With btn.Font
        .Name = "Calibri"
        .Size = 11
        .Bold = True
    End With
End Sub

Function GetVBACode()
    Dim s
    s = ""
    s = s & "Option Explicit" & vbCrLf
    s = s & vbCrLf
    s = s & "Public Const REPORT_SHEET As String = ""📄 Report""" & vbCrLf
    s = s & "Public Const PIPELINE_SHEET As String = ""MiT Strom Pipeline""" & vbCrLf
    s = s & "Public Const DASH_SHEET As String = ""Dashboard""" & vbCrLf
    s = s & "Public Const DIAGRAM_SHEET As String = ""📊 Diagramme""" & vbCrLf
    s = s & vbCrLf
    s = s & "Public Sub GenerateFullReport()" & vbCrLf
    s = s & "    Dim t As Double: t = Timer" & vbCrLf
    s = s & "    Application.ScreenUpdating = False" & vbCrLf
    s = s & "    Application.Calculation = xlCalculationManual" & vbCrLf
    s = s & "    On Error GoTo CleanFail" & vbCrLf
    s = s & "    Call RefreshAllData" & vbCrLf
    s = s & "    Call UpdateReportTimestamp" & vbCrLf
    s = s & "    ThisWorkbook.Worksheets(REPORT_SHEET).Activate" & vbCrLf
    s = s & "    Application.Calculation = xlCalculationAutomatic" & vbCrLf
    s = s & "    Application.Calculate" & vbCrLf
    s = s & "    Application.ScreenUpdating = True" & vbCrLf
    s = s & "    MsgBox ""✅ Report aktualisiert in "" & Format(Timer - t, ""0.00"") & "" s"", vbInformation, ""MiT Strom""" & vbCrLf
    s = s & "    Exit Sub" & vbCrLf
    s = s & "CleanFail:" & vbCrLf
    s = s & "    Application.Calculation = xlCalculationAutomatic" & vbCrLf
    s = s & "    Application.ScreenUpdating = True" & vbCrLf
    s = s & "    MsgBox ""❌ Fehler: "" & Err.Description, vbCritical" & vbCrLf
    s = s & "End Sub" & vbCrLf
    s = s & vbCrLf
    s = s & "Public Sub ExportReportToPDF()" & vbCrLf
    s = s & "    Dim ws As Worksheet, fn As String, defPath As String" & vbCrLf
    s = s & "    On Error GoTo PDFFail" & vbCrLf
    s = s & "    Set ws = ThisWorkbook.Worksheets(REPORT_SHEET)" & vbCrLf
    s = s & "    defPath = ThisWorkbook.Path" & vbCrLf
    s = s & "    If Len(defPath) = 0 Then defPath = Environ(""USERPROFILE"") & ""\Desktop""" & vbCrLf
    s = s & "    fn = defPath & ""\MiT_Strom_Report_"" & Format(Now, ""YYYY-MM-DD_HHMM"") & "".pdf""" & vbCrLf
    s = s & "    ws.ExportAsFixedFormat Type:=xlTypePDF, Filename:=fn, _" & vbCrLf
    s = s & "        Quality:=xlQualityStandard, IgnorePrintAreas:=False, OpenAfterPublish:=True" & vbCrLf
    s = s & "    MsgBox ""📄 PDF erstellt:"" & vbCrLf & fn, vbInformation" & vbCrLf
    s = s & "    Exit Sub" & vbCrLf
    s = s & "PDFFail:" & vbCrLf
    s = s & "    MsgBox ""❌ "" & Err.Description, vbCritical" & vbCrLf
    s = s & "End Sub" & vbCrLf
    s = s & vbCrLf
    s = s & "Public Sub ExportFullPackageToPDF()" & vbCrLf
    s = s & "    Dim sheetsArr As Variant, fn As String, defPath As String" & vbCrLf
    s = s & "    On Error GoTo Fail" & vbCrLf
    s = s & "    sheetsArr = Array(""CEO Report"", DASH_SHEET, DIAGRAM_SHEET, REPORT_SHEET)" & vbCrLf
    s = s & "    defPath = ThisWorkbook.Path" & vbCrLf
    s = s & "    If Len(defPath) = 0 Then defPath = Environ(""USERPROFILE"") & ""\Desktop""" & vbCrLf
    s = s & "    fn = defPath & ""\MiT_Strom_FullPackage_"" & Format(Now, ""YYYY-MM-DD_HHMM"") & "".pdf""" & vbCrLf
    s = s & "    ThisWorkbook.Sheets(sheetsArr).Select" & vbCrLf
    s = s & "    ActiveSheet.ExportAsFixedFormat Type:=xlTypePDF, Filename:=fn, _" & vbCrLf
    s = s & "        Quality:=xlQualityStandard, IgnorePrintAreas:=False, OpenAfterPublish:=True" & vbCrLf
    s = s & "    ThisWorkbook.Sheets(REPORT_SHEET).Activate" & vbCrLf
    s = s & "    MsgBox ""📦 Komplett-PDF erstellt:"" & vbCrLf & fn, vbInformation" & vbCrLf
    s = s & "    Exit Sub" & vbCrLf
    s = s & "Fail:" & vbCrLf
    s = s & "    MsgBox ""❌ "" & Err.Description, vbCritical" & vbCrLf
    s = s & "End Sub" & vbCrLf
    s = s & vbCrLf
    s = s & "Public Sub RefreshAllData()" & vbCrLf
    s = s & "    Dim ws As Worksheet" & vbCrLf
    s = s & "    On Error Resume Next" & vbCrLf
    s = s & "    For Each ws In ThisWorkbook.Worksheets: ws.Calculate: Next ws" & vbCrLf
    s = s & "    Application.CalculateFullRebuild" & vbCrLf
    s = s & "End Sub" & vbCrLf
    s = s & vbCrLf
    s = s & "Public Sub UpdateReportTimestamp()" & vbCrLf
    s = s & "    On Error Resume Next" & vbCrLf
    s = s & "    ThisWorkbook.Worksheets(REPORT_SHEET).Range(""A3"").Value = _" & vbCrLf
    s = s & "        ""Stand: "" & Format(Now, ""DD.MM.YYYY HH:MM"") & ""  ·  via Makro""" & vbCrLf
    s = s & "End Sub" & vbCrLf
    s = s & vbCrLf
    s = s & "Public Sub EmailReport()" & vbCrLf
    s = s & "    Dim ol As Object, mail As Object, fn As String, defPath As String" & vbCrLf
    s = s & "    On Error GoTo MailFail" & vbCrLf
    s = s & "    defPath = ThisWorkbook.Path: If Len(defPath) = 0 Then defPath = Environ(""TEMP"")" & vbCrLf
    s = s & "    fn = defPath & ""\MiT_Strom_Report_"" & Format(Now, ""YYYY-MM-DD_HHMM"") & "".pdf""" & vbCrLf
    s = s & "    ThisWorkbook.Worksheets(REPORT_SHEET).ExportAsFixedFormat Type:=xlTypePDF, _" & vbCrLf
    s = s & "        Filename:=fn, Quality:=xlQualityStandard, OpenAfterPublish:=False" & vbCrLf
    s = s & "    Set ol = CreateObject(""Outlook.Application"")" & vbCrLf
    s = s & "    Set mail = ol.CreateItem(0)" & vbCrLf
    s = s & "    With mail" & vbCrLf
    s = s & "        .Subject = ""MiT Strom Schweiz — Sales-Report "" & Format(Now, ""DD.MM.YYYY"")" & vbCrLf
    s = s & "        .Body = ""Liebe Kollegen,"" & vbCrLf & vbCrLf & _" & vbCrLf
    s = s & "                ""anbei der aktuelle MiT-Strom-Sales-Report."" & vbCrLf & vbCrLf & _" & vbCrLf
    s = s & "                ""Beste Grüsse"" & vbCrLf & ""Burak Ücöz"" & vbCrLf & _" & vbCrLf
    s = s & "                ""Mobil in Time AG · An Aggreko Company""" & vbCrLf
    s = s & "        .Attachments.Add fn" & vbCrLf
    s = s & "        .Display" & vbCrLf
    s = s & "    End With" & vbCrLf
    s = s & "    Exit Sub" & vbCrLf
    s = s & "MailFail:" & vbCrLf
    s = s & "    MsgBox ""❌ "" & Err.Description & vbCrLf & ""(Outlook muss installiert sein)"", vbExclamation" & vbCrLf
    s = s & "End Sub" & vbCrLf
    s = s & vbCrLf
    s = s & "Public Sub AddNewDeal()" & vbCrLf
    s = s & "    Dim ws As Worksheet, lastRow As Long, newRow As Long" & vbCrLf
    s = s & "    Dim kunde As String, kt As String, seg As String, vol As String" & vbCrLf
    s = s & "    On Error GoTo AddFail" & vbCrLf
    s = s & "    Set ws = ThisWorkbook.Worksheets(PIPELINE_SHEET)" & vbCrLf
    s = s & "    kunde = InputBox(""Kunde / Unternehmen:"", ""Neuer Deal — 1/4"")" & vbCrLf
    s = s & "    If Len(kunde) = 0 Then Exit Sub" & vbCrLf
    s = s & "    kt = InputBox(""Kanton (z.B. ZH, BE, GE):"", ""Neuer Deal — 2/4"")" & vbCrLf
    s = s & "    seg = InputBox(""Segment (z.B. Events, Industrie):"", ""Neuer Deal — 3/4"")" & vbCrLf
    s = s & "    vol = InputBox(""Geschätztes Volumen CHF:"", ""Neuer Deal — 4/4"")" & vbCrLf
    s = s & "    If Not IsNumeric(vol) Then MsgBox ""Volumen muss eine Zahl sein."", vbExclamation: Exit Sub" & vbCrLf
    s = s & "    lastRow = ws.Cells(ws.Rows.Count, 2).End(xlUp).Row" & vbCrLf
    s = s & "    newRow = lastRow + 1" & vbCrLf
    s = s & "    ws.Cells(newRow, 1).Value = newRow - 5" & vbCrLf
    s = s & "    ws.Cells(newRow, 2).Value = kunde" & vbCrLf
    s = s & "    ws.Cells(newRow, 3).Value = kt" & vbCrLf
    s = s & "    ws.Cells(newRow, 4).Value = seg" & vbCrLf
    s = s & "    ws.Cells(newRow, 9).Value = CDbl(vol)" & vbCrLf
    s = s & "    ws.Cells(newRow, 18).Value = ""tbd""" & vbCrLf
    s = s & "    ws.Range(""O6:Q6"").Copy ws.Range(""O"" & newRow & "":Q"" & newRow)" & vbCrLf
    s = s & "    ws.Range(""Z6:AA6"").Copy ws.Range(""Z"" & newRow & "":AA"" & newRow)" & vbCrLf
    s = s & "    Application.CutCopyMode = False" & vbCrLf
    s = s & "    MsgBox ""✅ Deal hinzugefügt in Zeile "" & newRow, vbInformation" & vbCrLf
    s = s & "    ws.Activate: ws.Range(""E"" & newRow).Select" & vbCrLf
    s = s & "    Exit Sub" & vbCrLf
    s = s & "AddFail:" & vbCrLf
    s = s & "    MsgBox ""Fehler: "" & Err.Description, vbCritical" & vbCrLf
    s = s & "End Sub" & vbCrLf
    s = s & vbCrLf
    s = s & "Public Sub QuickStats()" & vbCrLf
    s = s & "    Dim won As Double, off As Double, opp As Double, tot As Double, cnt As Long" & vbCrLf
    s = s & "    On Error Resume Next" & vbCrLf
    s = s & "    won = ThisWorkbook.Worksheets(DASH_SHEET).Range(""A6"").Value" & vbCrLf
    s = s & "    off = ThisWorkbook.Worksheets(DASH_SHEET).Range(""D6"").Value" & vbCrLf
    s = s & "    opp = ThisWorkbook.Worksheets(DASH_SHEET).Range(""G6"").Value" & vbCrLf
    s = s & "    tot = ThisWorkbook.Worksheets(DASH_SHEET).Range(""I6"").Value" & vbCrLf
    s = s & "    cnt = ThisWorkbook.Worksheets(DASH_SHEET).Range(""I7"").Value" & vbCrLf
    s = s & "    MsgBox ""⚡ MiT Strom — Quick Stats"" & vbCrLf & String(40,""-"") & vbCrLf & _" & vbCrLf
    s = s & "        ""✅ WON:          "" & Format(won, ""#,##0"") & "" CHF"" & vbCrLf & _" & vbCrLf
    s = s & "        ""📄 Offerte:     "" & Format(off, ""#,##0"") & "" CHF"" & vbCrLf & _" & vbCrLf
    s = s & "        ""🎯 Opp.:        "" & Format(opp, ""#,##0"") & "" CHF"" & vbCrLf & _" & vbCrLf
    s = s & "        String(40,""-"") & vbCrLf & _" & vbCrLf
    s = s & "        ""📊 TOTAL:       "" & Format(tot, ""#,##0"") & "" CHF"" & vbCrLf & _" & vbCrLf
    s = s & "        ""🔢 Deals aktiv: "" & cnt, vbInformation, ""Quick Stats""" & vbCrLf
    s = s & "End Sub" & vbCrLf
    GetVBACode = s
End Function
