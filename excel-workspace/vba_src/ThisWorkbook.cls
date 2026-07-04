Attribute VB_Name = "ThisWorkbook"
Attribute VB_Base = "0{00020819-0000-0000-C000-000000000046}"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Attribute VB_TemplateDerived = False
Attribute VB_Customizable = True
Option Explicit

Private Sub Workbook_Open()
    On Error Resume Next
    Application.OnKey "^+i", "MIT_Import"
    Application.OnKey "^+m", "MIT_NeuerMonatsreport"
    Application.OnKey "^+b", "MIT_NeuesBlatt"
    Application.OnKey "^+e", "MIT_ExportBlatt"
End Sub

Private Sub Workbook_BeforeClose(Cancel As Boolean)
    On Error Resume Next
    Application.OnKey "^+i"
    Application.OnKey "^+m"
    Application.OnKey "^+b"
    Application.OnKey "^+e"
End Sub
