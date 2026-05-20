Attribute VB_Name = "MiT_CRM"
' =============================================================
'  MiT CRM Vorlage — VBA-Makros
'  Import:  Excel → Entwicklertools → Visual Basic → Datei →
'           Datei importieren → mit_crm.bas
'  Mappe muss .xlsm sein, damit Makros gespeichert werden.
' =============================================================

Option Explicit

Private Const SHEET_NAME As String = "📋 Kunden-Datenbank"
Private Const COL_STATUS As Long = 13           ' M
Private Const COL_FOLLOWUP As Long = 17         ' Q
Private Const COL_PROB As Long = 20             ' T
Private Const COL_LAST_ACT As Long = 22         ' V

' ---- Helfer ------------------------------------------------------------
Private Function DataSheet() As Worksheet
    Set DataSheet = ThisWorkbook.Worksheets(SHEET_NAME)
End Function

Private Function SelectedDataRows() As Range
    Dim sel As Range, r As Range, out As Range
    Set sel = Selection
    For Each r In sel.Rows
        If r.Row >= 4 And DataSheet().Cells(r.Row, 4).Value <> "" Then
            If out Is Nothing Then Set out = r Else Set out = Union(out, r)
        End If
    Next r
    Set SelectedDataRows = out
End Function

' ---- 1) Follow-up +14 Tage --------------------------------------------
Public Sub FollowUpPlus14()
    Dim rng As Range, r As Range, n As Long
    Set rng = SelectedDataRows()
    If rng Is Nothing Then
        MsgBox "Bitte mindestens eine Datensatz-Zeile markieren.", vbInformation
        Exit Sub
    End If
    For Each r In rng.Rows
        DataSheet().Cells(r.Row, COL_FOLLOWUP).Value = Date + 14
        DataSheet().Cells(r.Row, COL_FOLLOWUP).NumberFormat = "dd.mm.yyyy"
        n = n + 1
    Next r
    MsgBox n & " Zeile(n): Follow-up auf " & Format(Date + 14, "dd.mm.yyyy") & " gesetzt.", vbInformation
End Sub

' ---- 2) Status → 'kontaktiert' ----------------------------------------
Public Sub StatusKontaktiert()
    SetStatus "kontaktiert", 25
End Sub

' ---- 3) Status → 'in Gespräch' ----------------------------------------
Public Sub StatusInGespraech()
    SetStatus "in Gespräch", 50
End Sub

' ---- 4) Status → 'Angebot gesendet' -----------------------------------
Public Sub StatusAngebot()
    SetStatus "Angebot gesendet", 70
End Sub

Private Sub SetStatus(newStatus As String, prob As Long)
    Dim rng As Range, r As Range, n As Long
    Set rng = SelectedDataRows()
    If rng Is Nothing Then
        MsgBox "Bitte mindestens eine Datensatz-Zeile markieren.", vbInformation
        Exit Sub
    End If
    For Each r In rng.Rows
        DataSheet().Cells(r.Row, COL_STATUS).Value = newStatus
        DataSheet().Cells(r.Row, COL_PROB).Value = prob
        DataSheet().Cells(r.Row, COL_LAST_ACT).Value = Date
        DataSheet().Cells(r.Row, COL_LAST_ACT).NumberFormat = "dd.mm.yyyy"
        n = n + 1
    Next r
    MsgBox n & " Zeile(n) auf '" & newStatus & "' (" & prob & "%) gesetzt.", vbInformation
End Sub

' ---- 5) Wahrscheinlichkeit aus Status neu berechnen (Bulk) ------------
Public Sub UpdateProb()
    Dim ws As Worksheet, r As Long, n As Long, st As String, p As Long
    Set ws = DataSheet()
    For r = 4 To ws.Cells(ws.Rows.Count, 4).End(xlUp).Row
        st = CStr(ws.Cells(r, COL_STATUS).Value)
        Select Case st
            Case "offen": p = 10
            Case "kontaktiert": p = 25
            Case "in Gespräch": p = 50
            Case "Angebot gesendet": p = 70
            Case "aktiv": p = 100
            Case "inaktiv": p = 0
            Case Else: p = -1
        End Select
        If p >= 0 Then
            ws.Cells(r, COL_PROB).Value = p
            n = n + 1
        End If
    Next r
    MsgBox "Wahrscheinlichkeit für " & n & " Zeilen aktualisiert.", vbInformation
End Sub

' ---- 6) Massenexport pro Segment --------------------------------------
Public Sub ExportSegment()
    Dim seg As String, ws As Worksheet, src As Worksheet, r As Long, dr As Long, c As Long
    seg = InputBox("Segment für Export (z.B. 'Pharma/Chemie'):", "ExportSegment")
    If Len(seg) = 0 Then Exit Sub

    Set src = DataSheet()
    Dim wb As Workbook
    Set wb = Workbooks.Add
    Set ws = wb.Sheets(1)
    ws.Name = Replace(seg, "/", "_")

    ' Header
    For c = 1 To 22
        ws.Cells(1, c).Value = src.Cells(3, c).Value
        ws.Cells(1, c).Font.Bold = True
    Next c

    dr = 2
    For r = 4 To src.Cells(src.Rows.Count, 4).End(xlUp).Row
        If src.Cells(r, 3).Value = seg Then
            For c = 1 To 22
                ws.Cells(dr, c).Value = src.Cells(r, c).Value
            Next c
            dr = dr + 1
        End If
    Next r
    ws.Columns.AutoFit
    MsgBox (dr - 2) & " Datensätze aus '" & seg & "' in neue Mappe exportiert.", vbInformation
End Sub

' ---- 7) Aktive Aufgaben markieren -------------------------------------
Public Sub HighlightOverdue()
    Dim ws As Worksheet, r As Long, n As Long
    Set ws = DataSheet()
    For r = 4 To ws.Cells(ws.Rows.Count, 4).End(xlUp).Row
        If IsDate(ws.Cells(r, COL_FOLLOWUP).Value) Then
            If ws.Cells(r, COL_FOLLOWUP).Value < Date Then
                ws.Cells(r, COL_FOLLOWUP).Interior.Color = RGB(248, 203, 173)
                ws.Cells(r, COL_FOLLOWUP).Font.Bold = True
                n = n + 1
            End If
        End If
    Next r
    MsgBox n & " überfällige Follow-ups hervorgehoben.", vbInformation
End Sub
