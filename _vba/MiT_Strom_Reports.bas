Attribute VB_Name = "MiT_Strom_Reports"
'==================================================================
'  MiT Strom Schweiz — Reporting Macros
'  Mobil in Time AG · An Aggreko Company · Burak Ücöz
'==================================================================
Option Explicit

Public Const REPORT_SHEET As String = "📄 Report"
Public Const PIPELINE_SHEET As String = "MiT Strom Pipeline"
Public Const DASH_SHEET As String = "Dashboard"
Public Const DIAGRAM_SHEET As String = "📊 Diagramme"

'------------------------------------------------------------------
'  MASTER: One-click full report generation
'------------------------------------------------------------------
Public Sub GenerateFullReport()
    Dim t As Double: t = Timer
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual

    On Error GoTo CleanFail

    Call RefreshAllData
    Call UpdateReportTimestamp
    Call ThisWorkbook.Worksheets(REPORT_SHEET).Activate

    Application.Calculation = xlCalculationAutomatic
    Application.Calculate
    Application.ScreenUpdating = True

    MsgBox "✅ Report generiert in " & Format(Timer - t, "0.00") & " s" & vbCrLf & _
           "Sheet «" & REPORT_SHEET & "» wurde aktualisiert.", _
           vbInformation, "MiT Strom Report"
    Exit Sub
CleanFail:
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True
    MsgBox "❌ Fehler bei Report-Erstellung:" & vbCrLf & Err.Description, vbCritical
End Sub

'------------------------------------------------------------------
'  PDF Export — Report sheet als PDF speichern
'------------------------------------------------------------------
Public Sub ExportReportToPDF()
    Dim ws As Worksheet, fn As String, defPath As String
    On Error GoTo PDFFail
    Set ws = ThisWorkbook.Worksheets(REPORT_SHEET)
    defPath = ThisWorkbook.Path
    If Len(defPath) = 0 Then defPath = Environ("USERPROFILE") & "\Desktop"

    fn = defPath & "\MiT_Strom_Report_" & Format(Now, "YYYY-MM-DD_HHMM") & ".pdf"
    ws.ExportAsFixedFormat Type:=xlTypePDF, _
                           Filename:=fn, _
                           Quality:=xlQualityStandard, _
                           IncludeDocProperties:=True, _
                           IgnorePrintAreas:=False, _
                           OpenAfterPublish:=True
    MsgBox "📄 PDF erstellt:" & vbCrLf & fn, vbInformation, "PDF-Export"
    Exit Sub
PDFFail:
    MsgBox "❌ PDF-Export Fehler: " & Err.Description, vbCritical
End Sub

'------------------------------------------------------------------
'  PDF — komplette Mappe (Dashboard + Report + Diagramme)
'------------------------------------------------------------------
Public Sub ExportFullPackageToPDF()
    Dim sheetsArr As Variant, fn As String, defPath As String
    On Error GoTo Fail
    sheetsArr = Array("CEO Report", DASH_SHEET, DIAGRAM_SHEET, REPORT_SHEET)
    defPath = ThisWorkbook.Path
    If Len(defPath) = 0 Then defPath = Environ("USERPROFILE") & "\Desktop"
    fn = defPath & "\MiT_Strom_FullPackage_" & Format(Now, "YYYY-MM-DD_HHMM") & ".pdf"

    ThisWorkbook.Sheets(sheetsArr).Select
    ActiveSheet.ExportAsFixedFormat Type:=xlTypePDF, Filename:=fn, _
                                    Quality:=xlQualityStandard, _
                                    IgnorePrintAreas:=False, _
                                    OpenAfterPublish:=True
    ThisWorkbook.Sheets(REPORT_SHEET).Activate
    MsgBox "📦 Komplett-PDF erstellt:" & vbCrLf & fn, vbInformation
    Exit Sub
Fail:
    MsgBox "❌ PDF-Export Fehler: " & Err.Description, vbCritical
End Sub

'------------------------------------------------------------------
'  Refresh: Force recalc + sort pipeline by Status, Volume
'------------------------------------------------------------------
Public Sub RefreshAllData()
    Dim ws As Worksheet
    On Error Resume Next
    For Each ws In ThisWorkbook.Worksheets
        ws.Calculate
    Next ws
    Application.CalculateFullRebuild
End Sub

'------------------------------------------------------------------
'  Timestamp aktualisieren im Report
'------------------------------------------------------------------
Public Sub UpdateReportTimestamp()
    On Error Resume Next
    ThisWorkbook.Worksheets(REPORT_SHEET).Range("A3").Value = _
        "Stand: " & Format(Now, "DD.MM.YYYY HH:MM") & "  ·  Erstellt von Makro"
End Sub

'------------------------------------------------------------------
'  Report als E-Mail (Outlook) versenden mit PDF im Anhang
'------------------------------------------------------------------
Public Sub EmailReport()
    Dim ol As Object, mail As Object, fn As String, defPath As String
    On Error GoTo MailFail

    defPath = ThisWorkbook.Path
    If Len(defPath) = 0 Then defPath = Environ("TEMP")
    fn = defPath & "\MiT_Strom_Report_" & Format(Now, "YYYY-MM-DD_HHMM") & ".pdf"

    ThisWorkbook.Worksheets(REPORT_SHEET).ExportAsFixedFormat _
        Type:=xlTypePDF, Filename:=fn, _
        Quality:=xlQualityStandard, IgnorePrintAreas:=False, OpenAfterPublish:=False

    Set ol = CreateObject("Outlook.Application")
    Set mail = ol.CreateItem(0)
    With mail
        .Subject = "MiT Strom Schweiz — Sales-Report " & Format(Now, "DD.MM.YYYY")
        .Body = "Liebe Kollegen," & vbCrLf & vbCrLf & _
                "anbei der aktuelle MiT-Strom-Sales-Report." & vbCrLf & vbCrLf & _
                "Beste Grüsse" & vbCrLf & "Burak Ücöz" & vbCrLf & _
                "Mobil in Time AG  ·  An Aggreko Company"
        .Attachments.Add fn
        .Display
    End With
    MsgBox "📧 Outlook-Entwurf erstellt mit PDF-Anhang.", vbInformation
    Exit Sub
MailFail:
    MsgBox "❌ E-Mail-Fehler: " & Err.Description & vbCrLf & _
           "(Outlook muss installiert sein)", vbExclamation
End Sub

'------------------------------------------------------------------
'  Add new deal to pipeline (input-form style)
'------------------------------------------------------------------
Public Sub AddNewDeal()
    Dim ws As Worksheet, lastRow As Long, newRow As Long
    Dim kunde As String, kt As String, seg As String, vol As String
    On Error GoTo AddFail

    Set ws = ThisWorkbook.Worksheets(PIPELINE_SHEET)
    kunde = InputBox("Kunde / Unternehmen:", "Neuer Deal — Schritt 1/4")
    If Len(kunde) = 0 Then Exit Sub
    kt = InputBox("Kanton (z.B. ZH, BE, GE):", "Neuer Deal — Schritt 2/4")
    seg = InputBox("Segment (z.B. Events, Industrie):", "Neuer Deal — Schritt 3/4")
    vol = InputBox("Geschätztes Volumen CHF:", "Neuer Deal — Schritt 4/4")
    If Not IsNumeric(vol) Then
        MsgBox "Volumen muss eine Zahl sein.", vbExclamation: Exit Sub
    End If

    lastRow = ws.Cells(ws.Rows.Count, 2).End(xlUp).Row
    newRow = lastRow + 1
    ws.Cells(newRow, 1).Value = newRow - 5
    ws.Cells(newRow, 2).Value = kunde
    ws.Cells(newRow, 3).Value = kt
    ws.Cells(newRow, 4).Value = seg
    ws.Cells(newRow, 9).Value = CDbl(vol)
    ws.Cells(newRow, 18).Value = "tbd"

    Dim srcRow As Long: srcRow = 6
    ws.Range("O" & srcRow & ":Q" & srcRow).Copy ws.Range("O" & newRow & ":Q" & newRow)
    Application.CutCopyMode = False

    MsgBox "✅ Deal hinzugefügt in Zeile " & newRow & vbCrLf & _
           "Bitte Details ergänzen (kW, Dauer, Kosten, USP, Status).", vbInformation
    ws.Activate
    ws.Range("E" & newRow).Select
    Exit Sub
AddFail:
    MsgBox "Fehler: " & Err.Description, vbCritical
End Sub

'------------------------------------------------------------------
'  Show stats popup (quick overview)
'------------------------------------------------------------------
Public Sub QuickStats()
    Dim won As Double, off As Double, opp As Double, tot As Double
    Dim cnt As Long
    On Error Resume Next
    won = ThisWorkbook.Worksheets(DASH_SHEET).Range("A6").Value
    off = ThisWorkbook.Worksheets(DASH_SHEET).Range("D6").Value
    opp = ThisWorkbook.Worksheets(DASH_SHEET).Range("G6").Value
    tot = ThisWorkbook.Worksheets(DASH_SHEET).Range("I6").Value
    cnt = ThisWorkbook.Worksheets(DASH_SHEET).Range("I7").Value

    MsgBox "⚡  MiT Strom — Quick Stats" & vbCrLf & String(45, "-") & vbCrLf & _
           "✅ WON:           " & Format(won, "#,##0") & " CHF" & vbCrLf & _
           "📄 Offerte:       " & Format(off, "#,##0") & " CHF" & vbCrLf & _
           "🎯 Opportunität:  " & Format(opp, "#,##0") & " CHF" & vbCrLf & _
           String(45, "-") & vbCrLf & _
           "📊 TOTAL:         " & Format(tot, "#,##0") & " CHF" & vbCrLf & _
           "🔢 Deals aktiv:   " & cnt, _
           vbInformation, "MiT Strom Quick Stats"
End Sub

'------------------------------------------------------------------
'  Workbook Open Hook (ThisWorkbook code)
'------------------------------------------------------------------
'   Im «DieseArbeitsmappe» / «ThisWorkbook» Code-Modul einfügen:
'   Private Sub Workbook_Open()
'       Call UpdateReportTimestamp
'       Worksheets("📄 Report").Activate
'   End Sub
