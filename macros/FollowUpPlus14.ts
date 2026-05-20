/**
 * Office Script: Follow-up +14 Tage für markierte Zeilen.
 * Lauffähig in Excel for the Web (Automatisieren → Skript-Editor).
 */
function main(workbook: ExcelScript.Workbook) {
  const sheet = workbook.getWorksheet("📋 Kunden-Datenbank");
  const range = workbook.getSelectedRange();
  if (!range) {
    console.log("Bitte zuerst eine Zeile markieren.");
    return;
  }
  const startRow = range.getRowIndex() + 1;
  const endRow = startRow + range.getRowCount() - 1;
  const target = new Date();
  target.setDate(target.getDate() + 14);
  // Excel-Serial-Datum
  const serial = Math.floor((target.getTime() - new Date(1899, 11, 30).getTime()) / 86400000);

  let n = 0;
  for (let r = startRow; r <= endRow; r++) {
    if (r < 4) continue;
    const firma = sheet.getCell(r - 1, 3).getValue();
    if (!firma) continue;
    const cell = sheet.getCell(r - 1, 16);  // col Q (0-indexed 16)
    cell.setValue(serial);
    cell.setNumberFormat("dd.mm.yyyy");
    n++;
  }
  console.log(`${n} Zeile(n): Follow-up auf ${target.toLocaleDateString("de-CH")} gesetzt.`);
}
