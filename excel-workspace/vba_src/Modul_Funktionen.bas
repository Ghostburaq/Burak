Attribute VB_Name = "Modul_Funktionen"
Option Explicit

' =====================================================================
'  MiT GESAMTMAPPE - ZUSATZFUNKTIONEN
'  - MIT_NeuerDeal   : Schnell-Erfassung Pipeline (Eingabemaske)
'  - MIT_NeuerKunde  : Schnell-Erfassung CRM (Eingabemaske)
'  - MIT_FollowUp14  : markierte Kalenderzeilen auf +14 Tage
'  - MIT_OffertePDF  : Angebot als PDF speichern
'  - MIT_NeueOfferte : Offerten-Zaehler +1 und Eingabefelder leeren
' =====================================================================

Private Function LetzteDatenzeile(ws As Worksheet, ByVal spalte As Long, _
                                  ByVal abZeile As Long) As Long
    Dim r As Long, leer As Long
    LetzteDatenzeile = abZeile - 1
    leer = 0: r = abZeile
    Do While leer < 80 And r < 100000
        If Len(Trim$(CStr(ws.Cells(r, spalte).Value))) > 0 Then
            LetzteDatenzeile = r: leer = 0
        Else
            leer = leer + 1
        End If
        r = r + 1
    Loop
End Function

Public Sub MIT_NeuerDeal()
    Dim ws As Worksheet, z As Long
    Dim kunde As String
    Set ws = ThisWorkbook.Worksheets("02_PIPELINE")
    kunde = Trim$(InputBox("NEUER DEAL — Kunde / Unternehmen:", "Schnell-Erfassung Pipeline"))
    If Len(kunde) = 0 Then Exit Sub
    z = LetzteDatenzeile(ws, 2, 5) + 1

    ws.Cells(z, 2).Value = kunde
    ws.Cells(z, 3).Value = UCase$(Trim$(InputBox("Kanton (z.B. ZH):", "Neuer Deal", "ZH")))
    ws.Cells(z, 4).Value = Trim$(InputBox("Segment:", "Neuer Deal", "Industrie"))
    ws.Cells(z, 5).Value = Trim$(InputBox("Leistung / Fleet (z.B. 250 kVA Generator):", "Neuer Deal"))
    Dim kw As String
    kw = Trim$(InputBox("kW (Zahl, optional):", "Neuer Deal"))
    If IsNumeric(kw) Then ws.Cells(z, 6).Value = CDbl(kw)
    Dim vol As String
    vol = Trim$(InputBox("Volumen CHF (Zahl):", "Neuer Deal"))
    If IsNumeric(vol) Then ws.Cells(z, 9).Value = CDbl(vol)
    Dim st As String
    st = Trim$(InputBox("Status (WON / offered / follow-up / tbd / LOST):", "Neuer Deal", "tbd"))
    If Len(st) > 0 Then ws.Cells(z, 18).Value = st
    Dim wr As String
    wr = Trim$(InputBox("Wahrscheinlichkeit % (z.B. 50):", "Neuer Deal", "10"))
    If IsNumeric(wr) Then ws.Cells(z, 19).Value = CDbl(wr) / 100

    Application.Goto ws.Cells(z, 2), False
    MsgBox "Deal '" & kunde & "' in Zeile " & z & " erfasst." & vbCrLf & _
           "Marge/Gew.Wert/Nr. rechnen automatisch.", vbInformation, "Neuer Deal"
End Sub

Public Sub MIT_NeuerKunde()
    Dim ws As Worksheet, z As Long
    Dim firma As String
    Set ws = ThisWorkbook.Worksheets("03_KUNDEN_CRM")
    firma = Trim$(InputBox("NEUER KUNDE — Firmenname:", "Schnell-Erfassung CRM"))
    If Len(firma) = 0 Then Exit Sub
    z = LetzteDatenzeile(ws, 4, 5) + 1

    ws.Cells(z, 4).Value = firma
    ws.Cells(z, 2).Value = UCase$(Trim$(InputBox("Priorität (A / B / C):", "Neuer Kunde", "B")))
    ws.Cells(z, 3).Value = Trim$(InputBox("Segment:", "Neuer Kunde"))
    ws.Cells(z, 5).Value = Trim$(InputBox("Ort:", "Neuer Kunde"))
    ws.Cells(z, 7).Value = UCase$(Trim$(InputBox("Kanton:", "Neuer Kunde", "ZH")))
    ws.Cells(z, 8).Value = Trim$(InputBox("Ansprechpartner:", "Neuer Kunde"))
    ws.Cells(z, 10).Value = Trim$(InputBox("E-Mail:", "Neuer Kunde"))
    ws.Cells(z, 13).Value = "offen"
    Dim wt As String
    wt = Trim$(InputBox("Potenzial / Wert CHF (Zahl, optional):", "Neuer Kunde"))
    If IsNumeric(wt) Then ws.Cells(z, 21).Value = CDbl(wt)

    Application.Goto ws.Cells(z, 4), False
    MsgBox "Kunde '" & firma & "' in Zeile " & z & " erfasst.", vbInformation, "Neuer Kunde"
End Sub

Public Sub MIT_FollowUp14()
    Dim ws As Worksheet, sel As Range, zelle As Range
    Dim n As Long
    Set ws = ThisWorkbook.Worksheets("29_KALENDER")
    If ActiveSheet.Name <> "29_KALENDER" Then
        ws.Activate
        MsgBox "Bitte im Reiter 29_KALENDER die gewünschten Zeilen markieren und erneut ausführen.", _
               vbInformation, "Wiedervorlage +14"
        Exit Sub
    End If
    On Error Resume Next
    Set sel = Selection
    On Error GoTo 0
    If sel Is Nothing Then Exit Sub
    n = 0
    For Each zelle In sel.Cells
        If zelle.Row >= 7 Then
            ws.Cells(zelle.Row, 1).Value = Date + 14
            ws.Cells(zelle.Row, 1).NumberFormat = "DD.MM.YYYY"
            n = n + 1
        End If
    Next zelle
    MsgBox n & " Zeile(n) auf Wiedervorlage " & Format(Date + 14, "DD.MM.YYYY") & " gesetzt.", _
           vbInformation, "Wiedervorlage +14"
End Sub

Public Sub MIT_OffertePDF()
    Dim ws As Worksheet, pfad As String, datei As String
    Dim kunde As String, ofnr As String

    On Error GoTo Fehler
    Set ws = ThisWorkbook.Worksheets("22_ANGEBOT_KALK")
    ws.Calculate
    kunde = Trim$(CStr(ws.Range("I8").Value))
    ofnr = Trim$(CStr(ws.Range("I5").Value))
    If Len(kunde) = 0 Then kunde = "Kunde"
    datei = "Offerte_" & SicherName(ofnr) & "_" & SicherName(kunde) & ".pdf"
    If Len(ThisWorkbook.Path) > 0 Then
        pfad = ThisWorkbook.Path & Application.PathSeparator & datei
    Else
        pfad = datei
    End If
    ws.ExportAsFixedFormat Type:=0, Filename:=pfad, Quality:=0, _
        IncludeDocProperties:=True, IgnorePrintAreas:=False, OpenAfterPublish:=False
    MsgBox "Offerte als PDF gespeichert:" & vbCrLf & pfad, vbInformation, "Offerte-PDF"
    Exit Sub
Fehler:
    MsgBox "Offerte-PDF fehlgeschlagen: " & Err.Description & vbCrLf & _
           "Notfalls: Datei > Exportieren > PDF.", vbExclamation, "Offerte-PDF"
End Sub

Public Sub MIT_NeueOfferte()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Worksheets("22_ANGEBOT_KALK")
    ' Zähler +1
    If IsNumeric(ws.Range("J14").Value) Then
        ws.Range("J14").Value = ws.Range("J14").Value + 1
    Else
        ws.Range("J14").Value = 1
    End If
    ' Positionen leeren
    ws.Range("B6:B11").ClearContents
    ws.Range("C6:D11").ClearContents
    ws.Range("F6:F11").ClearContents
    ' Nebenkosten-Eingaben leeren
    ws.Range("B14").ClearContents
    ws.Range("B15").ClearContents
    ws.Range("B17").ClearContents
    ws.Range("B19").ClearContents
    ' Kundenfelder leeren
    ws.Range("I8").ClearContents
    ws.Range("I9").ClearContents
    ws.Range("I10").ClearContents
    ws.Activate
    Application.Goto ws.Range("I8"), False
    MsgBox "Neue Offerte vorbereitet (Nr. " & ws.Range("I5").Value & ")." & vbCrLf & _
           "Kunde und Positionen jetzt eingeben.", vbInformation, "Neue Offerte"
End Sub

Private Function SicherName(ByVal s As String) As String
    Dim bad As Variant, b As Variant
    bad = Array("[", "]", ":", "*", "?", "/", "\", "'", " ", "&")
    For Each b In bad
        s = Replace(s, CStr(b), "_")
    Next b
    If Len(s) > 40 Then s = Left$(s, 40)
    SicherName = s
End Function
