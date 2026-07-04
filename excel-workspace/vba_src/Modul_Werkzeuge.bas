Attribute VB_Name = "Modul_Werkzeuge"
Option Explicit

' =====================================================================
'  MiT GESAMTMAPPE - WERKZEUGE
'  - MIT_NeuerMonatsreport: erstellt automatisch eine NEUE Arbeitsmappe
'    mit Monatsreport + Dashboard (Werte eingefroren) und speichert sie.
'  - MIT_NeuesBlatt: legt ein neues, formatiertes Listen-Blatt an.
'  - MIT_ExportBlatt: exportiert das aktive Blatt als eigene Datei.
' =====================================================================

Public Sub MIT_NeuerMonatsreport()
    Dim nb As Workbook, ws As Worksheet
    Dim pfad As String, datei As String

    On Error GoTo Fehler
    Application.ScreenUpdating = False
    Application.Calculate

    Set nb = Workbooks.Add
    ThisWorkbook.Worksheets("06_MONATSREPORT").Copy Before:=nb.Sheets(1)
    ThisWorkbook.Worksheets("01_DASHBOARD").Copy After:=nb.Sheets(1)
    ' Standard-Leerblätter entfernen
    Application.DisplayAlerts = False
    Dim k As Long
    For k = nb.Sheets.Count To 1 Step -1
        If nb.Sheets(k).Name <> "06_MONATSREPORT" And nb.Sheets(k).Name <> "01_DASHBOARD" Then
            nb.Sheets(k).Delete
        End If
    Next k
    Application.DisplayAlerts = True
    ' Werte einfrieren (Schutz: nur wenn lesbar)
    Dim a As Variant
    On Error Resume Next
    For Each ws In nb.Worksheets
        a = ws.UsedRange.Value
        If Not IsEmpty(a) Then ws.UsedRange.Value = a
    Next ws
    On Error GoTo Fehler

    datei = "MiT_Monatsreport_" & Year(Date) & "_" & Format(Month(Date), "00") & ".xlsx"
    If Len(ThisWorkbook.Path) > 0 Then
        pfad = ThisWorkbook.Path & Application.PathSeparator & datei
    Else
        pfad = datei
    End If
    Application.DisplayAlerts = False
    nb.SaveAs Filename:=pfad, FileFormat:=51   ' xlOpenXMLWorkbook (.xlsx)
    Application.DisplayAlerts = True
    Application.ScreenUpdating = True
    MsgBox "Neue Arbeitsmappe erstellt und gespeichert:" & vbCrLf & pfad, _
           vbInformation, "Monatsreport"
    Exit Sub

Fehler:
    Application.DisplayAlerts = True
    Application.ScreenUpdating = True
    MsgBox "Monatsreport konnte nicht erstellt werden: " & Err.Description, _
           vbExclamation, "Monatsreport"
End Sub

Public Sub MIT_NeuesBlatt()
    Dim nm As String, ws As Worksheet, i As Long
    nm = Trim$(InputBox("Name des neuen Blattes:", "Neues Listen-Blatt", _
                        "NEU " & Format(Date, "DD.MM")))
    If Len(nm) = 0 Then Exit Sub
    If Len(nm) > 31 Then nm = Left$(nm, 31)
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets(nm)
    On Error GoTo 0
    If Not ws Is Nothing Then
        MsgBox "Ein Blatt mit diesem Namen existiert bereits.", vbExclamation
        Exit Sub
    End If
    Set ws = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Sheets(ThisWorkbook.Sheets.Count))
    ws.Name = nm
    ws.Tab.Color = RGB(128, 128, 128)
    With ws.Range("A1")
        .Value = UCase$(nm)
        .Font.Bold = True
        .Font.Size = 15
        .Font.Color = vbWhite
        .Interior.Color = RGB(38, 38, 38)
    End With
    ws.Range("A1:H1").Interior.Color = RGB(38, 38, 38)
    ws.Range("A2").Formula = "=HYPERLINK(""#'00_START'!A1"",""zurück zum START"")"
    Dim c As Long
    For c = 1 To 8
        With ws.Cells(4, c)
            .Value = "Spalte " & c
            .Font.Bold = True
            .Font.Color = vbWhite
            .Interior.Color = RGB(128, 128, 128)
        End With
        ws.Columns(c).ColumnWidth = 18
    Next c
    On Error Resume Next
    ws.Activate
    ws.Rows(5).Select
    ActiveWindow.FreezePanes = True
    On Error GoTo 0
    MsgBox "Neues Blatt '" & nm & "' angelegt (Kopfzeile in Zeile 4, Daten ab Zeile 5).", _
           vbInformation, "Neues Blatt"
End Sub

Public Sub MIT_ExportBlatt()
    Dim nb As Workbook, pfad As String, datei As String

    On Error GoTo Fehler
    Dim quelle As Worksheet
    Set quelle = ActiveSheet
    Application.ScreenUpdating = False
    Application.Calculate
    Set nb = Workbooks.Add
    quelle.Copy Before:=nb.Sheets(1)
    Application.DisplayAlerts = False
    Dim k2 As Long
    For k2 = nb.Sheets.Count To 1 Step -1
        If nb.Sheets(k2).Name <> quelle.Name Then nb.Sheets(k2).Delete
    Next k2
    Application.DisplayAlerts = True
    Dim a2 As Variant
    On Error Resume Next
    a2 = nb.Worksheets(1).UsedRange.Value
    If Not IsEmpty(a2) Then nb.Worksheets(1).UsedRange.Value = a2
    On Error GoTo Fehler

    datei = "MiT_" & SicherDateiname(nb.Worksheets(1).Name) & "_" & _
            Year(Date) & "_" & Format(Month(Date), "00") & "_" & Format(Day(Date), "00") & ".xlsx"
    If Len(ThisWorkbook.Path) > 0 Then
        pfad = ThisWorkbook.Path & Application.PathSeparator & datei
    Else
        pfad = datei
    End If
    Application.DisplayAlerts = False
    nb.SaveAs Filename:=pfad, FileFormat:=51
    Application.DisplayAlerts = True
    Application.ScreenUpdating = True
    MsgBox "Blatt als neue Arbeitsmappe gespeichert:" & vbCrLf & pfad, _
           vbInformation, "Export"
    Exit Sub

Fehler:
    Application.DisplayAlerts = True
    Application.ScreenUpdating = True
    MsgBox "Export fehlgeschlagen: " & Err.Description, vbExclamation, "Export"
End Sub

Private Function SicherDateiname(ByVal s As String) As String
    Dim bad As Variant, b As Variant
    bad = Array("[", "]", ":", "*", "?", "/", "\", "'", " ")
    For Each b In bad
        s = Replace(s, CStr(b), "_")
    Next b
    SicherDateiname = s
End Function
