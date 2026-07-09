Attribute VB_Name = "Modul_Import"
Option Explicit

' =====================================================================
'  MiT GESAMTMAPPE - IMPORT-ZENTRALE
'  Importiert beliebige Excel-/CSV-Dateien und verteilt die Blätter
'  automatisch auf die richtigen Reiter (Regeln: Reiter 90_IMPORT).
'  Unbekannte Blätter werden als neues rotes Blatt übernommen.
' =====================================================================

Private Const WS_IMP As String = "90_IMPORT"
Private Const MAP_ROW1 As Long = 13        ' erste Regel-Zeile (Header in 12)
Private Const ALIAS_ROW1 As Long = 13      ' erste Alias-Zeile (Spalten J/K)
Private Const HDR_ROW As Long = 4          ' Kopfzeile aller Listen-Reiter
Private Const DATA_ROW1 As Long = 5        ' erste Datenzeile

Private mNeuZeilen As Long, mDuplikate As Long, mNeueBlaetter As Long, mBlaetter As Long
Private mStill As Boolean

Public Function MIT_Ping() As String
    MIT_Ping = "pong"
End Function



Public Sub MIT_Import()
    Dim f As Variant
    f = Application.GetOpenFilename( _
        "Excel- und CSV-Dateien (*.xls*;*.csv),*.xls*;*.csv", , _
        "Datei in die Gesamtmappe importieren")
    If VarType(f) = vbBoolean Then Exit Sub
    MIT_ImportDatei CStr(f), False
End Sub

Public Sub MIT_ImportDatei(ByVal pfad As String, ByVal still As Boolean)
    Dim src As Workbook, ws As Worksheet
    Dim calcAlt As XlCalculation
    Dim fehler As String

    On Error GoTo Fehler
    mNeuZeilen = 0: mDuplikate = 0: mNeueBlaetter = 0: mBlaetter = 0
    mStill = still
    On Error Resume Next
    Application.ScreenUpdating = False
    calcAlt = Application.Calculation
    Application.Calculation = xlCalculationManual
    On Error GoTo Fehler

    Set src = Workbooks.Open(pfad, ReadOnly:=True, UpdateLinks:=0)
    For Each ws In src.Worksheets
        If ws.Visible = xlSheetVisible Then
            VerarbeiteBlatt ws, pfad
        End If
    Next ws
    src.Close SaveChanges:=False

    ' Offerten aus 35_OFFERTEN in Pipeline + CRM verteilen (idempotent, robust)
    Dim vAdd As Long
    On Error Resume Next
    vAdd = VerteileOfferten(pfad)
    On Error GoTo Fehler

    Application.Calculation = calcAlt
    Application.Calculate
    Application.ScreenUpdating = True
    If still Then Exit Sub
    MsgBox "Import abgeschlossen:" & vbCrLf & vbCrLf & _
           mBlaetter & " Blätter verarbeitet" & vbCrLf & _
           mNeuZeilen & " neue Zeilen übernommen" & vbCrLf & _
           mDuplikate & " Duplikate übersprungen" & vbCrLf & _
           mNeueBlaetter & " unbekannte Blätter als neue Reiter angelegt" & vbCrLf & _
           vAdd & " Offerten in Pipeline/CRM verteilt" & vbCrLf & vbCrLf & _
           "Details: Reiter 90_IMPORT (Protokoll).", vbInformation, "MiT Import"
    Exit Sub

Fehler:
    fehler = "#" & Err.Number & " " & Err.Description
    On Error Resume Next
    If Not src Is Nothing Then src.Close SaveChanges:=False
    Application.Calculation = calcAlt
    Application.ScreenUpdating = True
    If still Then
        LogEintrag pfad, "-", "-", 0, 0, "ABBRUCH: " & fehler
    Else
        MsgBox "Import abgebrochen: " & fehler, vbExclamation, "MiT Import"
    End If
End Sub

' ---------------------------------------------------------------------
Private Sub VerarbeiteBlatt(wsSrc As Worksheet, ByVal pfad As String)
    Dim hdrRow As Long, ziel As String, keySpec As String, fSpalten As String, modus As String
    Dim erkannt As Boolean
    mBlaetter = mBlaetter + 1
    ' Roh eingefügtes Offerten-Dokument (Label:Wert-Kopf) VOR der Tabellen-Erkennung
    Dim istOff As Boolean
    On Error Resume Next
    istOff = IstOffertenDokument(wsSrc)
    On Error GoTo 0
    If istOff Then
        VerarbeiteOffertenDokument wsSrc, pfad
        Exit Sub
    End If
    erkannt = ErkenneTyp(wsSrc, hdrRow, ziel, keySpec, fSpalten, modus)
    If erkannt Then
        If UCase$(modus) = "IGNORIEREN" Then
            LogEintrag pfad, wsSrc.Name, ziel, 0, 0, "ignoriert (Regel)"
        Else
            UebernehmeDaten wsSrc, hdrRow, ziel, keySpec, fSpalten, pfad
        End If
    Else
        If LeeresBlatt(wsSrc) Then
            LogEintrag pfad, wsSrc.Name, "-", 0, 0, "leer - übersprungen"
        ElseIf mStill Then
            KopiereAlsNeuesBlatt wsSrc, pfad
        ElseIf MsgBox("Blatt '" & wsSrc.Name & "' wurde nicht erkannt." & vbCrLf & _
                      "Als neues Blatt in die Gesamtmappe übernehmen?", _
                      vbYesNo + vbQuestion, "Unbekanntes Blatt") = vbYes Then
            KopiereAlsNeuesBlatt wsSrc, pfad
        Else
            LogEintrag pfad, wsSrc.Name, "-", 0, 0, "übersprungen (Benutzer)"
        End If
    End If
End Sub

Private Function LeeresBlatt(ws As Worksheet) As Boolean
    LeeresBlatt = (Application.WorksheetFunction.CountA(ws.UsedRange) = 0)
End Function

' ---------------------------------------------------------------------
Private Function ErkenneTyp(wsSrc As Worksheet, ByRef hdrRow As Long, ByRef ziel As String, _
                            ByRef keySpec As String, ByRef fSpalten As String, _
                            ByRef modus As String) As Boolean
    Dim wsI As Worksheet, r As Long, sr As Long
    Dim e1 As String, e2 As String, zeile As String
    Set wsI = ThisWorkbook.Worksheets(WS_IMP)
    r = MAP_ROW1
    Do While UCase$(Trim$(CStr(wsI.Cells(r, 1).Value))) = "JA" Or _
             UCase$(Trim$(CStr(wsI.Cells(r, 1).Value))) = "NEIN"
        If UCase$(Trim$(CStr(wsI.Cells(r, 1).Value))) = "JA" Then
            e1 = Norm(wsI.Cells(r, 2).Value)
            e2 = Norm(wsI.Cells(r, 3).Value)
            For sr = 1 To 15
                zeile = ZeilenText(wsSrc, sr)
                If Len(zeile) > 0 Then
                    If InStr(zeile, e1) > 0 And (Len(e2) = 0 Or InStr(zeile, e2) > 0) Then
                        hdrRow = sr
                        ziel = Trim$(CStr(wsI.Cells(r, 4).Value))
                        keySpec = Trim$(CStr(wsI.Cells(r, 5).Value))
                        fSpalten = Trim$(CStr(wsI.Cells(r, 6).Value))
                        modus = Trim$(CStr(wsI.Cells(r, 7).Value))
                        ErkenneTyp = True
                        Exit Function
                    End If
                End If
            Next sr
        End If
        r = r + 1
    Loop
    ErkenneTyp = False
End Function

Private Function ZeilenText(ws As Worksheet, ByVal zeile As Long) As String
    Dim c As Long, s As String
    For c = 1 To 60
        s = s & "|" & Norm(ws.Cells(zeile, c).Value)
    Next c
    If Len(Replace(s, "|", "")) = 0 Then s = ""
    ZeilenText = s
End Function

Private Function Norm(v As Variant) As String
    Dim s As String
    On Error Resume Next
    s = CStr(v)
    On Error GoTo 0
    s = Replace(s, vbLf, " ")
    s = Replace(s, vbCr, " ")
    s = Replace(s, Chr(160), " ")
    Do While InStr(s, "  ") > 0
        s = Replace(s, "  ", " ")
    Loop
    Norm = LCase$(Trim$(s))
End Function

' ---------------------------------------------------------------------
Private Sub UebernehmeDaten(wsSrc As Worksheet, ByVal hdrRow As Long, ByVal zielName As String, _
                            ByVal keySpec As String, ByVal fSpalten As String, ByVal pfad As String)
    Dim wsT As Worksheet
    Dim tKopf As Collection, aliasMap As Collection, fCols As Collection
    Dim srcCols() As Long, tgtCols() As Long, nMap As Long
    Dim lastSrcRow As Long, lastSrcCol As Long
    Dim c As Long, r As Long, i As Long
    Dim h As String, tgtH As String
    Dim keyHdr() As String, keyTgtCol() As Long, nKey As Long
    Dim vorhanden As Collection, key As String
    Dim anchorCol As Long, lastRow As Long, zielRow As Long
    Dim neu As Long, dupl As Long, alle As Long

    On Error Resume Next
    Set wsT = ThisWorkbook.Worksheets(zielName)
    On Error GoTo 0
    If wsT Is Nothing Then
        LogEintrag pfad, wsSrc.Name, zielName, 0, 0, "FEHLER: Ziel-Reiter fehlt"
        Exit Sub
    End If

    Set tKopf = KopfMap(wsT)               ' norm. Header -> Zielspalte
    Set aliasMap = HoleAliasMap()              ' norm. Fremd-Header -> norm. Ziel-Header
    Set fCols = FormelSpalten(fSpalten)    ' Spaltennummern der Formelspalten

    ' Quell-Header -> Ziel-Spalten auflösen
    Dim leerc As Long
    lastSrcCol = 0: leerc = 0
    For c = 1 To 300
        If Len(Norm(wsSrc.Cells(hdrRow, c).Value)) > 0 Then
            lastSrcCol = c: leerc = 0
        Else
            leerc = leerc + 1
            If leerc >= 8 Then Exit For
        End If
    Next c
    If lastSrcCol = 0 Then lastSrcCol = 1
    ReDim srcCols(1 To lastSrcCol): ReDim tgtCols(1 To lastSrcCol)
    Dim istProzent() As Boolean
    ReDim istProzent(1 To lastSrcCol)
    nMap = 0
    For c = 1 To lastSrcCol
        h = Norm(wsSrc.Cells(hdrRow, c).Value)
        If Len(h) > 0 Then
            tgtH = h
            If Not KExists(tKopf, tgtH) Then
                If KExists(aliasMap, h) Then tgtH = KWert(aliasMap, h)
            End If
            If KExists(tKopf, tgtH) Then
                If Not KExists(fCols, CStr(KWert(tKopf, tgtH))) Then   ' Formelspalten nie überschreiben
                    nMap = nMap + 1
                    srcCols(nMap) = c
                    tgtCols(nMap) = KWert(tKopf, tgtH)
                    istProzent(nMap) = (InStr(tgtH, "%") > 0)
                End If
            End If
        End If
    Next c
    If nMap < 2 Then
        LogEintrag pfad, wsSrc.Name, zielName, 0, 0, "FEHLER: <2 Spalten zuordenbar | nMap=" & nMap & _
            " tKopf=" & tKopf.Count & " alias=" & aliasMap.Count & " lastSrcCol=" & lastSrcCol & _
            " srcH1=[" & Norm(wsSrc.Cells(hdrRow, 1).Value) & "] srcH2=[" & Norm(wsSrc.Cells(hdrRow, 2).Value) & _
            "] tK1ex=" & KExists(tKopf, "kunde / unternehmen")
        Exit Sub
    End If

    ' Schlüsselspalten (Dedup)
    nKey = 0
    If Len(keySpec) > 0 Then
        keyHdr = Split(keySpec, ";")
        ReDim keyTgtCol(0 To UBound(keyHdr))
        For i = 0 To UBound(keyHdr)
            h = Norm(keyHdr(i))
            If Not KExists(tKopf, h) Then
                If KExists(aliasMap, h) Then h = KWert(aliasMap, h)
            End If
            If KExists(tKopf, h) Then
                keyTgtCol(nKey) = KWert(tKopf, h)
                nKey = nKey + 1
            End If
        Next i
    End If

    ' Anker-Spalte = erste Schlüsselspalte, sonst erste zugeordnete Spalte
    If nKey > 0 Then anchorCol = keyTgtCol(0) Else anchorCol = tgtCols(1)
    Dim leerz As Long, rr As Long
    lastRow = DATA_ROW1 - 1: leerz = 0: rr = DATA_ROW1
    Do While leerz < 60 And rr < 200000
        If Len(Trim$(CStr(wsT.Cells(rr, anchorCol).Value))) > 0 Then
            lastRow = rr: leerz = 0
        Else
            leerz = leerz + 1
        End If
        rr = rr + 1
    Loop

    ' vorhandene Schlüssel sammeln
    Set vorhanden = New Collection
    If nKey > 0 Then
        For r = DATA_ROW1 To lastRow
            key = ""
            For i = 0 To nKey - 1
                key = key & "||" & Norm(wsT.Cells(r, keyTgtCol(i)).Value)
            Next i
            If Len(Replace(key, "|", "")) > 0 Then KAdd vorhanden, key
        Next r
    End If

    ' Quellzeilen übernehmen
    lastSrcRow = wsSrc.UsedRange.Row + wsSrc.UsedRange.Rows.Count - 1
    If lastSrcRow < hdrRow Then lastSrcRow = hdrRow
    zielRow = lastRow
    Dim startNeu As Long: startNeu = lastRow + 1
    For r = hdrRow + 1 To lastSrcRow
        ' komplett leere (zugeordnete) Zeilen überspringen
        Dim leer As Boolean: leer = True
        For i = 1 To nMap
            If Len(Trim$(CStr(wsSrc.Cells(r, srcCols(i)).Value))) > 0 Then leer = False: Exit For
        Next i
        If Not leer Then
            alle = alle + 1
            key = ""
            If nKey > 0 Then
                Dim ksrc As String
                For i = 0 To nKey - 1
                    ksrc = QuellwertFuerZielspalte(wsSrc, r, keyTgtCol(i), srcCols, tgtCols, nMap)
                    key = key & "||" & ksrc
                Next i
            End If
            If nKey > 0 And KExists(vorhanden, key) Then
                dupl = dupl + 1
            Else
                zielRow = zielRow + 1
                Dim wert As Variant
                For i = 1 To nMap
                    wert = wsSrc.Cells(r, srcCols(i)).Value
                    If istProzent(i) And IsNumeric(wert) Then
                        If wert > 1 Then wert = wert / 100
                    End If
                    wsT.Cells(zielRow, tgtCols(i)).Value = wert
                Next i
                If nKey > 0 Then KAdd vorhanden, key
                neu = neu + 1
            End If
        End If
    Next r

    ' Format + Formeln für neue Zeilen aus Vorlagenzeile (DATA_ROW1) übernehmen
    If neu > 0 Then
        wsT.Rows(DATA_ROW1).Copy
        wsT.Rows(startNeu & ":" & zielRow).PasteSpecial xlPasteFormats
        Application.CutCopyMode = False
        ' Werte wurden schon geschrieben; jetzt Formelspalten füllen
        Dim teil As Variant, sp As Variant
        If Len(fSpalten) > 0 Then
            teil = Split(fSpalten, ";")
            For Each sp In teil
                sp = Trim$(CStr(sp))
                If Len(sp) > 0 Then
                    wsT.Range(sp & DATA_ROW1).Copy wsT.Range(sp & startNeu & ":" & sp & zielRow)
                End If
            Next sp
        End If
    End If

    mNeuZeilen = mNeuZeilen + neu
    mDuplikate = mDuplikate + dupl
    LogEintrag pfad, wsSrc.Name, zielName, neu, dupl, "angehängt"
End Sub

Private Function QuellwertFuerZielspalte(wsSrc As Worksheet, ByVal r As Long, ByVal tgtCol As Long, _
                                         srcCols() As Long, tgtCols() As Long, ByVal nMap As Long) As String
    Dim i As Long
    For i = 1 To nMap
        If tgtCols(i) = tgtCol Then
            QuellwertFuerZielspalte = Norm(wsSrc.Cells(r, srcCols(i)).Value)
            Exit Function
        End If
    Next i
    QuellwertFuerZielspalte = ""
End Function

Private Function KopfMap(wsT As Worksheet) As Collection
    Dim d As New Collection, c As Long, h As String, leer As Long
    leer = 0
    For c = 1 To 300
        h = Norm(wsT.Cells(HDR_ROW, c).Value)
        If Len(h) = 0 Then
            leer = leer + 1
            If leer >= 8 Then Exit For
        Else
            leer = 0
            If Left$(h, 1) <> "_" Then
                If Not KExists(d, h) Then d.Add c, h
            End If
        End If
    Next c
    Set KopfMap = d
End Function

Private Function HoleAliasMap() As Collection
    Dim d As New Collection, wsI As Worksheet, r As Long
    Set wsI = ThisWorkbook.Worksheets(WS_IMP)
    r = ALIAS_ROW1
    Do While Len(Trim$(CStr(wsI.Cells(r, 10).Value))) > 0
        If Not KExists(d, Norm(wsI.Cells(r, 10).Value)) Then
            d.Add Norm(wsI.Cells(r, 11).Value), Norm(wsI.Cells(r, 10).Value)
        End If
        r = r + 1
    Loop
    Set HoleAliasMap = d
End Function

Private Function FormelSpalten(ByVal fSpalten As String) As Collection
    Dim d As New Collection, teil As Variant, sp As Variant
    If Len(fSpalten) > 0 Then
        teil = Split(fSpalten, ";")
        For Each sp In teil
            sp = Trim$(CStr(sp))
            If Len(sp) > 0 Then KAdd d, CStr(ThisWorkbook.Worksheets(1).Range(sp & "1").Column)
        Next sp
    End If
    Set FormelSpalten = d
End Function

' =====================================================================
'  OFFERTEN-VERTEILUNG  (35_OFFERTEN -> 02_PIPELINE + 03_KUNDEN_CRM)
'  Idempotent: legt fehlende Deals/Kunden an, überspringt vorhandene.
'  Kann per Ctrl+Shift+V von Hand ausgelöst werden (MIT_OffertenVerteilen)
'  und läuft automatisch am Ende jedes Imports.
' =====================================================================
Public Sub MIT_OffertenVerteilen()
    Dim added As Long
    On Error Resume Next
    Application.ScreenUpdating = False
    added = VerteileOfferten("(manuell)")
    Application.Calculate
    Application.ScreenUpdating = True
    On Error GoTo 0
    MsgBox "Offerten verteilt:" & vbCrLf & vbCrLf & _
           added & " neue Einträge in 02_PIPELINE / 03_KUNDEN_CRM angelegt." & vbCrLf & _
           "(Bereits vorhandene Offerten wurden übersprungen.)", _
           vbInformation, "Offerten verteilen"
End Sub

Private Function VerteileOfferten(ByVal pfad As String) As Long
    Dim wsO As Worksheet, wsP As Worksheet, wsC As Worksheet
    Dim ko As Collection, kp As Collection, kc As Collection
    Dim r As Long, lastO As Long, lastP As Long, lastC As Long, added As Long
    Dim beleg As String, kunde As String

    On Error GoTo Fertig
    Set wsO = ThisWorkbook.Worksheets("35_OFFERTEN")
    Set wsP = ThisWorkbook.Worksheets("02_PIPELINE")
    Set wsC = ThisWorkbook.Worksheets("03_KUNDEN_CRM")
    Set ko = KopfMap(wsO): Set kp = KopfMap(wsP): Set kc = KopfMap(wsC)

    ' Quellspalten (35_OFFERTEN)
    Dim cBeleg&, cKunde&, cEinsatz&, cKontakt&, cSeg&, cTage&, cStart&, cNetto&
    cBeleg = ColOf(ko, "belegnummer"): cKunde = ColOf(ko, "kunde / firma")
    cEinsatz = ColOf(ko, "einsatzort"): cKontakt = ColOf(ko, "ansprechpartner")
    cSeg = ColOf(ko, "segment"): cTage = ColOf(ko, "tage")
    cStart = ColOf(ko, "mietbeginn"): cNetto = ColOf(ko, "netto chf")
    If cBeleg = 0 Or cKunde = 0 Then GoTo Fertig

    ' Zielspalten Pipeline
    Dim pKunde&, pFleet&, pDauer&, pStart&, pVol&, pStatus&, pWahr&, pAkq&, pSchritt&, pNotiz&, pSeg&
    pKunde = ColOf(kp, "kunde / unternehmen"): pFleet = ColOf(kp, "leistung / fleet")
    pDauer = ColOf(kp, "dauer (tage)"): pStart = ColOf(kp, "start")
    pVol = ColOf(kp, "volumen chf"): pStatus = ColOf(kp, "status")
    pWahr = ColOf(kp, "wahr. %"): pAkq = ColOf(kp, "akquise typ")
    pSchritt = ColOf(kp, "nächster schritt"): pNotiz = ColOf(kp, "notiz intern")
    pSeg = ColOf(kp, "segment")

    ' Zielspalten CRM
    Dim mPrio&, mSeg&, mFirma&, mOrt&, mKontakt&, mStatus&, mSchritt&, mWert&, mWahr&, mNotiz&
    mPrio = ColOf(kc, "prio"): mSeg = ColOf(kc, "segment"): mFirma = ColOf(kc, "firmenname")
    mOrt = ColOf(kc, "ort"): mKontakt = ColOf(kc, "ansprechpartner"): mStatus = ColOf(kc, "status")
    mSchritt = ColOf(kc, "nächster schritt"): mWert = ColOf(kc, "wert chf")
    mWahr = ColOf(kc, "wahrsch. %"): mNotiz = ColOf(kc, "notizen")
    If pKunde = 0 Or pStatus = 0 Or mFirma = 0 Then GoTo Fertig

    lastO = LetzteZeile(wsO, cBeleg)
    lastP = LetzteZeile(wsP, pKunde)
    lastC = LetzteZeile(wsC, mFirma)

    ' Set vorhandener CRM-Firmen
    Dim firmen As Collection: Set firmen = New Collection
    For r = DATA_ROW1 To lastC
        KAdd firmen, Norm(wsC.Cells(r, mFirma).Value)
    Next r

    For r = DATA_ROW1 To lastO
        beleg = Trim$(CStr(wsO.Cells(r, cBeleg).Value))
        If Len(beleg) > 0 Then
            kunde = Trim$(CStr(wsO.Cells(r, cKunde).Value))
            ' --- Pipeline (Dedup: Belegnummer steht in 'Notiz intern') ---
            If pNotiz > 0 Then
                If Not PipelineHatBeleg(wsP, pNotiz, lastP, beleg) Then
                    lastP = lastP + 1
                    NeueVorlagenzeile wsP, lastP, "A;O;P;Q;Y;Z;AA;AB;AC;AD"
                    wsP.Cells(lastP, pKunde).Value = kunde
                    If pSeg > 0 And cSeg > 0 Then wsP.Cells(lastP, pSeg).Value = wsO.Cells(r, cSeg).Value
                    If pFleet > 0 Then wsP.Cells(lastP, pFleet).Value = "Aggregat-Miete (Offerte)"
                    If pDauer > 0 And cTage > 0 Then wsP.Cells(lastP, pDauer).Value = wsO.Cells(r, cTage).Value
                    If pStart > 0 And cStart > 0 Then wsP.Cells(lastP, pStart).Value = wsO.Cells(r, cStart).Value
                    If pVol > 0 And cNetto > 0 Then wsP.Cells(lastP, pVol).Value = wsO.Cells(r, cNetto).Value
                    wsP.Cells(lastP, pStatus).Value = "offered"
                    If pWahr > 0 Then wsP.Cells(lastP, pWahr).Value = 0.5
                    If pAkq > 0 Then wsP.Cells(lastP, pAkq).Value = "Offerte"
                    If pSchritt > 0 Then wsP.Cells(lastP, pSchritt).Value = "Offerte nachfassen"
                    Dim einsatz As String: einsatz = ""
                    If cEinsatz > 0 Then einsatz = CStr(wsO.Cells(r, cEinsatz).Value)
                    wsP.Cells(lastP, pNotiz).Value = "Offerte " & beleg & " · Einsatz: " & einsatz
                    added = added + 1
                End If
            End If
            ' --- CRM (Dedup: Firmenname) ---
            If Not KExists(firmen, Norm(kunde)) And Len(kunde) > 0 Then
                lastC = lastC + 1
                NeueVorlagenzeile wsC, lastC, "A;W"
                If mPrio > 0 Then wsC.Cells(lastC, mPrio).Value = "B"
                If mSeg > 0 And cSeg > 0 Then wsC.Cells(lastC, mSeg).Value = wsO.Cells(r, cSeg).Value
                wsC.Cells(lastC, mFirma).Value = kunde
                If mOrt > 0 And cEinsatz > 0 Then wsC.Cells(lastC, mOrt).Value = wsO.Cells(r, cEinsatz).Value
                If mKontakt > 0 And cKontakt > 0 Then wsC.Cells(lastC, mKontakt).Value = wsO.Cells(r, cKontakt).Value
                If mStatus > 0 Then wsC.Cells(lastC, mStatus).Value = "Offeriert"
                If mSchritt > 0 Then wsC.Cells(lastC, mSchritt).Value = "Offerte " & beleg & " nachfassen"
                If mWert > 0 And cNetto > 0 Then wsC.Cells(lastC, mWert).Value = wsO.Cells(r, cNetto).Value
                If mWahr > 0 Then wsC.Cells(lastC, mWahr).Value = 0.5
                If mNotiz > 0 Then wsC.Cells(lastC, mNotiz).Value = "aus Offerte " & beleg
                KAdd firmen, Norm(kunde)
                added = added + 1
            End If
        End If
    Next r

    If added > 0 Then LogEintrag pfad, "35_OFFERTEN", "02_PIPELINE / 03_KUNDEN_CRM", added, 0, "Offerten verteilt"
Fertig:
    VerteileOfferten = added
End Function

Private Function LetzteZeile(ws As Worksheet, ByVal ankerCol As Long) As Long
    Dim leerz As Long, rr As Long, last As Long
    last = DATA_ROW1 - 1: leerz = 0: rr = DATA_ROW1
    Do While leerz < 60 And rr < 200000
        If Len(Trim$(CStr(ws.Cells(rr, ankerCol).Value))) > 0 Then
            last = rr: leerz = 0
        Else
            leerz = leerz + 1
        End If
        rr = rr + 1
    Loop
    LetzteZeile = last
End Function

Private Function PipelineHatBeleg(ws As Worksheet, ByVal notizCol As Long, _
                                  ByVal lastRow As Long, ByVal beleg As String) As Boolean
    Dim r As Long, b As String
    b = LCase$(beleg)
    For r = DATA_ROW1 To lastRow
        If InStr(LCase$(CStr(ws.Cells(r, notizCol).Value)), b) > 0 Then
            PipelineHatBeleg = True: Exit Function
        End If
    Next r
    PipelineHatBeleg = False
End Function

Private Sub NeueVorlagenzeile(ws As Worksheet, ByVal zielRow As Long, ByVal fSpalten As String)
    ws.Rows(DATA_ROW1).Copy
    ws.Rows(zielRow).PasteSpecial xlPasteFormats
    Application.CutCopyMode = False
    Dim teil As Variant, sp As Variant
    If Len(fSpalten) > 0 Then
        teil = Split(fSpalten, ";")
        For Each sp In teil
            sp = Trim$(CStr(sp))
            If Len(sp) > 0 Then ws.Range(sp & DATA_ROW1).Copy ws.Range(sp & zielRow)
        Next sp
    End If
End Sub

Private Function ColOf(col As Collection, ByVal key As String) As Long
    On Error Resume Next
    ColOf = col.Item(key)
    On Error GoTo 0
End Function

' =====================================================================
'  OFFERTEN-DOKUMENT  (echtes Angebots-Layout: Label:Wert-Kopf + Positionen)
'  Erkennt eine roh eingefügte Offerte (nicht nur die Tabellen-Vorlage) und
'  übernimmt sie in 35_OFFERTEN + 36_OFFERTEN_POSITIONEN. Die Verteilung in
'  02_PIPELINE + 03_KUNDEN_CRM erledigt danach VerteileOfferten (Import-Ende).
' =====================================================================
Private Function IstOffertenDokument(ws As Worksheet) As Boolean
    Dim r As Long, c As Long, t As String, rowtext As String
    On Error GoTo Fertig
    For r = 1 To 45
        rowtext = ZeilenText(ws, r)
        For c = 1 To 30
            t = Norm(ws.Cells(r, c).Value)
            If Right$(t, 1) = ":" Then t = Trim$(Left$(t, Len(t) - 1))
            If t = "belegnummer" Or t = "angebotsnummer" Or t = "offerten-nr" Then
                If Len(WertRechtsOderUnten(ws, r, c)) > 0 Then
                    ' NICHT die Tabellen-Vorlage (deren Kopfzeile hat weitere Offerten-Spalten)
                    If InStr(rowtext, "kunde / firma") = 0 And InStr(rowtext, "einsatzort") = 0 Then
                        IstOffertenDokument = True
                        Exit Function
                    End If
                End If
            End If
        Next c
    Next r
Fertig:
    IstOffertenDokument = False
End Function

Private Sub VerarbeiteOffertenDokument(ws As Worksheet, ByVal pfad As String)
    Dim wsO As Worksheet, wsP As Worksheet
    Dim beleg As String, kunde As String, ko As Collection
    Dim cBeleg As Long, lastO As Long, r As Long, exists As Boolean, rowNew As Long
    On Error GoTo Fehler
    Set wsO = ThisWorkbook.Worksheets("35_OFFERTEN")
    Set wsP = ThisWorkbook.Worksheets("36_OFFERTEN_POSITIONEN")
    beleg = WertNebenLabel(ws, Array("belegnummer", "beleg-nr", "beleg nr", "angebotsnummer", "offerten-nr"))
    If Len(beleg) = 0 Then Exit Sub
    kunde = KundeAusKopf(ws)

    Set ko = KopfMap(wsO)
    cBeleg = ColOf(ko, "belegnummer")
    lastO = LetzteZeile(wsO, cBeleg)
    For r = DATA_ROW1 To lastO
        If Norm(wsO.Cells(r, cBeleg).Value) = Norm(beleg) Then exists = True: Exit For
    Next r

    If exists Then
        mDuplikate = mDuplikate + 1
        LogEintrag pfad, ws.Name, "35_OFFERTEN", 0, 1, "Offerte bereits vorhanden"
        Exit Sub
    End If

    rowNew = lastO + 1
    NeueVorlagenzeile wsO, rowNew, "A;W;X"
    SetzeWennDa wsO, ko, "belegnummer", rowNew, beleg
    SetzeWennDa wsO, ko, "kunde / firma", rowNew, kunde
    SetzeWennDa wsO, ko, "ansprechpartner", rowNew, KontaktAusKopf(ws)
    SetzeWennDa wsO, ko, "einsatzort", rowNew, WertNebenLabel(ws, Array("einsatzort", "objekt"))
    SetzeWennDa wsO, ko, "vertrieb", rowNew, WertNebenLabel(ws, Array("vertrieb", "bearbeiter"))
    SetzeWennDa wsO, ko, "projektleiter", rowNew, WertNebenLabel(ws, Array("projektleiter"))
    SetzeWennDa wsO, ko, "datum", rowNew, WertNebenLabel(ws, Array("datum"))
    SetzeWennDa wsO, ko, "mietbeginn", rowNew, WertNebenLabel(ws, Array("mietbeginn", "mietbeginn:", "beginn"))
    SetzeWennDa wsO, ko, "mietende", rowNew, WertNebenLabel(ws, Array("mietende", "mietende:"))
    SetzeWennDa wsO, ko, "vorgangsnr", rowNew, WertNebenLabel(ws, Array("vorgangsnummer"))
    SetzeWennDa wsO, ko, "kundennr", rowNew, WertNebenLabel(ws, Array("kundennummer"))
    SetzeWennDa wsO, ko, "ihr beleg", rowNew, WertNebenLabel(ws, Array("ihr beleg"))
    SetzeZahlWennDa wsO, ko, "netto chf", rowNew, ZahlNebenLabel(ws, Array("zwischensumme", "total exkl", "summe exkl"))
    SetzeZahlWennDa wsO, ko, "mwst chf", rowNew, ZahlNebenLabel(ws, Array("zzgl. mwst", "mwst", "mehrwertsteuer"))
    SetzeZahlWennDa wsO, ko, "total chf", rowNew, ZahlNebenLabel(ws, Array("endsumme", "total inkl"))
    SetzeZahlWennDa wsO, ko, "tagespreis chf", rowNew, ZahlNebenLabel(ws, Array("mietpreis pro tag", "tagespreis"))
    SetzeWennDa wsO, ko, "status", rowNew, "offered"
    SetzeWennDa wsO, ko, "quelle-datei", rowNew, DateiName(pfad)

    OffertenPositionenLesen ws, wsP, beleg, kunde
    mNeuZeilen = mNeuZeilen + 1
    LogEintrag pfad, ws.Name, "35_OFFERTEN", 1, 0, "Offerten-Dokument erkannt + übernommen"
    Exit Sub
Fehler:
    LogEintrag pfad, ws.Name, "35_OFFERTEN", 0, 0, "Offerten-Doc Fehler: " & Err.Description
End Sub

Private Sub OffertenPositionenLesen(ws As Worksheet, wsPos As Worksheet, _
                                    ByVal beleg As String, ByVal kunde As String)
    Dim hr As Long, c As Long, t As String, found As Boolean, rowtext As String
    On Error GoTo Fertig
    For hr = 1 To 60
        rowtext = ZeilenText(ws, hr)
        If InStr(rowtext, "bezeichnung") > 0 And _
           (InStr(rowtext, "gesamtpreis") > 0 Or InStr(rowtext, "einzelpreis") > 0 Or InStr(rowtext, "artikelnr") > 0) Then
            found = True: Exit For
        End If
    Next hr
    If Not found Then Exit Sub

    Dim cPos&, cArt&, cBez&, cAnz&, cDauer&, cEinzel&, cRabatt&, cGesamt&
    For c = 1 To 40
        t = Norm(ws.Cells(hr, c).Value)
        If t = "pos." Or t = "pos" Then cPos = c
        If InStr(t, "artikelnr") > 0 Then cArt = c
        If InStr(t, "bezeichnung") > 0 Then cBez = c
        If InStr(t, "anzahl") > 0 Or t = "menge" Then cAnz = c
        If InStr(t, "dauer") > 0 Then cDauer = c
        If InStr(t, "einzelpreis") > 0 Then cEinzel = c
        If InStr(t, "rabatt") > 0 Then cRabatt = c
        If InStr(t, "gesamtpreis") > 0 Then cGesamt = c
    Next c
    If cBez = 0 Then Exit Sub

    Dim kp As Collection: Set kp = KopfMap(wsPos)
    Dim tBeleg&, tKunde&, tPos&, tArt&, tBez&, tAnz&, tDauer&, tEinzel&, tRabatt&, tGesamt&
    tBeleg = ColOf(kp, "belegnummer"): tKunde = ColOf(kp, "kunde / firma")
    tPos = ColOf(kp, "pos."): tArt = ColOf(kp, "artikelnr."): tBez = ColOf(kp, "bezeichnung")
    tAnz = ColOf(kp, "anzahl"): tDauer = ColOf(kp, "dauer"): tEinzel = ColOf(kp, "einzelpreis chf")
    tRabatt = ColOf(kp, "rabatt %"): tGesamt = ColOf(kp, "gesamtpreis chf")
    Dim lastT As Long: lastT = LetzteZeile(wsPos, tBeleg)

    Dim r As Long, leer As Long, bez As String, hasNum As Boolean
    leer = 0
    For r = hr + 1 To hr + 400
        bez = Trim$(CStr(ws.Cells(r, cBez).Value))
        hasNum = (cGesamt > 0 And IsNumeric(ws.Cells(r, cGesamt).Value)) Or _
                 (cArt > 0 And Len(Trim$(CStr(ws.Cells(r, cArt).Value))) > 0)
        If Len(bez) = 0 And Not hasNum Then
            leer = leer + 1
            If leer >= 4 Then Exit For
        Else
            leer = 0
            lastT = lastT + 1
            NeueVorlagenzeile wsPos, lastT, "A"
            If tBeleg > 0 Then wsPos.Cells(lastT, tBeleg).Value = beleg
            If tKunde > 0 Then wsPos.Cells(lastT, tKunde).Value = kunde
            If tPos > 0 And cPos > 0 Then wsPos.Cells(lastT, tPos).Value = ws.Cells(r, cPos).Value
            If tArt > 0 And cArt > 0 Then wsPos.Cells(lastT, tArt).Value = ws.Cells(r, cArt).Value
            If tBez > 0 Then wsPos.Cells(lastT, tBez).Value = bez
            If tAnz > 0 And cAnz > 0 Then wsPos.Cells(lastT, tAnz).Value = ws.Cells(r, cAnz).Value
            If tDauer > 0 And cDauer > 0 Then wsPos.Cells(lastT, tDauer).Value = ws.Cells(r, cDauer).Value
            If tEinzel > 0 And cEinzel > 0 And IsNumeric(ws.Cells(r, cEinzel).Value) Then wsPos.Cells(lastT, tEinzel).Value = ws.Cells(r, cEinzel).Value
            If tRabatt > 0 And cRabatt > 0 Then wsPos.Cells(lastT, tRabatt).Value = ProzentWert(ws.Cells(r, cRabatt).Value)
            If tGesamt > 0 And cGesamt > 0 And IsNumeric(ws.Cells(r, cGesamt).Value) Then wsPos.Cells(lastT, tGesamt).Value = ws.Cells(r, cGesamt).Value
        End If
    Next r
Fertig:
End Sub

Private Function WertNebenLabel(ws As Worksheet, labels As Variant) As String
    Dim r As Long, c As Long, t As String, i As Long
    For r = 1 To 45
        For c = 1 To 30
            t = Norm(ws.Cells(r, c).Value)
            If Right$(t, 1) = ":" Then t = Trim$(Left$(t, Len(t) - 1))
            If Len(t) > 0 Then
                For i = LBound(labels) To UBound(labels)
                    If t = CStr(labels(i)) Then
                        WertNebenLabel = WertRechtsOderUnten(ws, r, c)
                        If Len(WertNebenLabel) > 0 Then Exit Function
                    End If
                Next i
            End If
        Next c
    Next r
    WertNebenLabel = ""
End Function

Private Function WertRechtsOderUnten(ws As Worksheet, ByVal r As Long, ByVal c As Long) As String
    Dim k As Long, v As String
    For k = 1 To 6
        v = Trim$(CStr(ws.Cells(r, c + k).Value))
        If Len(v) > 0 Then WertRechtsOderUnten = v: Exit Function
    Next k
    WertRechtsOderUnten = Trim$(CStr(ws.Cells(r + 1, c).Value))
End Function

Private Function ZahlNebenLabel(ws As Worksheet, labels As Variant) As Variant
    Dim r As Long, c As Long, t As String, i As Long, k As Long, vv As Variant
    For r = 1 To 60
        For c = 1 To 30
            t = Norm(ws.Cells(r, c).Value)
            If Len(t) > 0 Then
                For i = LBound(labels) To UBound(labels)
                    If InStr(t, CStr(labels(i))) > 0 Then
                        ' zuerst Wertzellen rechts (getrennte Betragsspalte), dann Label-Zelle selbst
                        For k = 1 To 6
                            vv = ParseCHF(CStr(ws.Cells(r, c + k).Value))
                            If IsNumeric(vv) Then ZahlNebenLabel = vv: Exit Function
                        Next k
                        vv = ParseCHF(CStr(ws.Cells(r, c).Value))
                        If IsNumeric(vv) Then ZahlNebenLabel = vv: Exit Function
                        vv = ParseCHF(CStr(ws.Cells(r + 1, c).Value))
                        If IsNumeric(vv) Then ZahlNebenLabel = vv: Exit Function
                    End If
                Next i
            End If
        Next c
    Next r
    ZahlNebenLabel = ""
End Function

Private Function ParseCHF(ByVal s As String) As Variant
    Dim i As Long, ch As String, keep As String, parts() As String, p As String
    s = LCase$(s)
    keep = ""
    For i = 1 To Len(s)
        ch = Mid$(s, i, 1)
        If (ch >= "0" And ch <= "9") Or ch = "." Or ch = "," Or ch = "'" Or ch = " " Then keep = keep & ch
    Next i
    keep = Replace(keep, "'", "")
    Do While InStr(keep, "  ") > 0: keep = Replace(keep, "  ", " "): Loop
    keep = Trim$(keep)
    If Len(keep) = 0 Then ParseCHF = "": Exit Function
    parts = Split(keep, " ")
    p = ""
    For i = UBound(parts) To LBound(parts) Step -1
        If Len(Trim$(parts(i))) > 0 Then p = Trim$(parts(i)): Exit For
    Next i
    p = Replace(p, ",", ".")
    If IsNumeric(p) Then ParseCHF = CDbl(p) Else ParseCHF = ""
End Function

Private Function ProzentWert(v As Variant) As Variant
    Dim s As String, d As Double
    s = Trim$(CStr(v))
    If Len(s) = 0 Then ProzentWert = "": Exit Function
    s = Replace(s, "%", ""): s = Replace(s, ",", ".")
    If IsNumeric(s) Then
        d = CDbl(s)
        If d > 1 Then d = d / 100
        ProzentWert = d
    Else
        ProzentWert = ""
    End If
End Function

Private Function KundeAusKopf(ws As Worksheet) As String
    Dim r As Long, c As Long, raw As String, t As String
    For r = 1 To 14
        For c = 1 To 4
            raw = Trim$(CStr(ws.Cells(r, c).Value))
            t = Norm(raw)
            If Len(raw) >= 4 Then
                If InStr(t, "mobil in time") = 0 And InStr(t, "angebot") = 0 _
                   And Not IstLabel(t) And EnthaeltBuchstaben(t) _
                   And LCase$(Left$(raw, 5)) <> "herr " And LCase$(Left$(raw, 5)) <> "frau " Then
                    KundeAusKopf = raw
                    Exit Function
                End If
            End If
        Next c
    Next r
    KundeAusKopf = ""
End Function

Private Function KontaktAusKopf(ws As Worksheet) As String
    Dim r As Long, c As Long, raw As String
    For r = 1 To 16
        For c = 1 To 4
            raw = Trim$(CStr(ws.Cells(r, c).Value))
            If LCase$(Left$(raw, 5)) = "herr " Or LCase$(Left$(raw, 5)) = "frau " Then
                KontaktAusKopf = Trim$(Mid$(raw, 6)): Exit Function
            End If
        Next c
    Next r
    KontaktAusKopf = ""
End Function

Private Function IstLabel(ByVal t As String) As Boolean
    Dim labs As Variant, i As Long
    labs = Array("vorgangsnummer", "belegnummer", "datum", "kundennummer", "bearbeiter", _
                 "vertrieb", "projektleiter", "einsatzort", "ihr beleg", "bemerkung", _
                 "angebot", "pos.", "artikelnr", "bezeichnung", "anzahl", "dauer", _
                 "einzelpreis", "rabatt", "gesamtpreis", "zwischensumme", "endsumme", _
                 "mwst", "mietbeginn", "mietende", "mietzeitraum", "einheit")
    For i = LBound(labs) To UBound(labs)
        If InStr(t, CStr(labs(i))) > 0 Then IstLabel = True: Exit Function
    Next i
End Function

Private Function EnthaeltBuchstaben(ByVal s As String) As Boolean
    Dim i As Long, ch As String
    For i = 1 To Len(s)
        ch = LCase$(Mid$(s, i, 1))
        If ch >= "a" And ch <= "z" Then EnthaeltBuchstaben = True: Exit Function
    Next i
End Function

Private Sub SetzeWennDa(ws As Worksheet, kopf As Collection, ByVal key As String, _
                        ByVal row As Long, ByVal v As Variant)
    Dim c As Long: c = ColOf(kopf, key)
    If c > 0 And Len(Trim$(CStr(v))) > 0 Then ws.Cells(row, c).Value = v
End Sub

Private Sub SetzeZahlWennDa(ws As Worksheet, kopf As Collection, ByVal key As String, _
                            ByVal row As Long, ByVal v As Variant)
    Dim c As Long: c = ColOf(kopf, key)
    If c > 0 Then
        If IsNumeric(v) Then ws.Cells(row, c).Value = CDbl(v)
    End If
End Sub

Private Function DateiName(ByVal pfad As String) As String
    Dim p As Long
    p = InStrRev(pfad, "\")
    If InStrRev(pfad, "/") > p Then p = InStrRev(pfad, "/")
    DateiName = Mid$(pfad, p + 1)
End Function

' --- Collection-Helfer (portabel: Windows, Mac, LibreOffice) ---
Private Sub KAdd(col As Collection, ByVal key As String)
    On Error Resume Next
    col.Add True, key
    On Error GoTo 0
End Sub

Private Function KExists(col As Collection, ByVal key As String) As Boolean
    Dim v As Variant
    On Error Resume Next
    v = col.Item(key)
    KExists = (Err.Number = 0)
    On Error GoTo 0
End Function

Private Function KWert(col As Collection, ByVal key As String) As Variant
    KWert = col.Item(key)
End Function

' ---------------------------------------------------------------------
Private Sub KopiereAlsNeuesBlatt(wsSrc As Worksheet, ByVal pfad As String)
    Dim neu As Worksheet, nm As String, basis As String, i As Long
    basis = "IMP " & wsSrc.Name
    basis = SicherName(basis)
    nm = basis
    i = 1
    Do While BlattExistiert(nm)
        i = i + 1
        nm = SicherName(basis & " (" & i & ")")
    Loop
    wsSrc.Copy After:=ThisWorkbook.Sheets(ThisWorkbook.Sheets.Count)
    Set neu = ThisWorkbook.Sheets(ThisWorkbook.Sheets.Count)
    On Error Resume Next
    neu.Name = nm
    neu.UsedRange.Value = neu.UsedRange.Value    ' Formeln/Bezüge kappen
    On Error GoTo 0
    neu.Tab.Color = RGB(192, 0, 0)
    mNeueBlaetter = mNeueBlaetter + 1
    LogEintrag pfad, wsSrc.Name, neu.Name, neu.UsedRange.Rows.Count, 0, "neues Blatt"
End Sub

Private Function SicherName(ByVal s As String) As String
    Dim bad As Variant, b As Variant
    bad = Array("[", "]", ":", "*", "?", "/", "\", "'")
    For Each b In bad
        s = Replace(s, CStr(b), " ")
    Next b
    If Len(s) > 31 Then s = Left$(s, 31)
    SicherName = Trim$(s)
End Function

Private Function BlattExistiert(ByVal nm As String) As Boolean
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets(nm)
    On Error GoTo 0
    BlattExistiert = Not ws Is Nothing
End Function

' ---------------------------------------------------------------------
Private Sub LogEintrag(ByVal pfad As String, ByVal blatt As String, ByVal ziel As String, _
                       ByVal neu As Long, ByVal dupl As Long, ByVal aktion As String)
    Dim wsI As Worksheet, r As Long, startR As Long
    Set wsI = ThisWorkbook.Worksheets(WS_IMP)
    ' Protokoll-Kopf suchen ("Zeitpunkt" in Spalte A)
    startR = 0
    For r = 20 To 200
        If Trim$(CStr(wsI.Cells(r, 1).Value)) = "Zeitpunkt" Then startR = r + 1: Exit For
    Next r
    If startR = 0 Then Exit Sub
    r = startR
    Do While Len(Trim$(CStr(wsI.Cells(r, 1).Value))) > 0
        r = r + 1
    Loop
    Dim p As Long
    p = InStrRev(pfad, "\")
    If InStrRev(pfad, "/") > p Then p = InStrRev(pfad, "/")
    wsI.Cells(r, 1).Value = Format(Now, "DD.MM.YYYY") & " " & Format(Hour(Now), "00") & ":" & Format(Minute(Now), "00")
    wsI.Cells(r, 2).Value = Mid$(pfad, p + 1)
    wsI.Cells(r, 3).Value = blatt
    wsI.Cells(r, 4).Value = ziel
    wsI.Cells(r, 5).Value = neu
    wsI.Cells(r, 6).Value = dupl
    wsI.Cells(r, 7).Value = aktion
End Sub
