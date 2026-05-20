/**
 * Office Script: Status → 'in Gespräch', Wahrsch. 50%.
 */
function main(workbook: ExcelScript.Workbook) {
  const sheet = workbook.getWorksheet("📋 Kunden-Datenbank");
  const range = workbook.getSelectedRange();
  if (!range) { console.log("Bitte Zeile(n) markieren."); return; }
  const startRow = range.getRowIndex() + 1;
  const endRow = startRow + range.getRowCount() - 1;
  const today = Math.floor((Date.now() - new Date(1899, 11, 30).getTime()) / 86400000);
  let n = 0;
  for (let r = startRow; r <= endRow; r++) {
    if (r < 4) continue;
    if (!sheet.getCell(r - 1, 3).getValue()) continue;
    sheet.getCell(r - 1, 12).setValue("in Gespräch");
    sheet.getCell(r - 1, 19).setValue(50);
    sheet.getCell(r - 1, 21).setValue(today);
    sheet.getCell(r - 1, 21).setNumberFormat("dd.mm.yyyy");
    n++;
  }
  console.log(`${n} Zeile(n) auf 'in Gespräch' (50%) gesetzt.`);
}
