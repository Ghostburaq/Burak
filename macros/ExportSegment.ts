/**
 * Office Script: Massenexport pro Segment in neues Worksheet.
 * Erzeugt z.B. Sheet "Export: Pharma_Chemie" mit allen Datensätzen dieses Segments.
 *
 * Eingabe via Parameter (für Power Automate / Button) oder hartcodiert.
 */
function main(workbook: ExcelScript.Workbook, segment: string = "Pharma/Chemie") {
  const src = workbook.getWorksheet("📋 Kunden-Datenbank");
  const used = src.getUsedRange();
  if (!used) { console.log("Quell-Sheet leer."); return; }
  const values = used.getValues();

  const sheetName = "Export: " + segment.replace(/[\/\\:*?\[\]]/g, "_").substring(0, 25);
  let dst = workbook.getWorksheet(sheetName);
  if (dst) dst.delete();
  dst = workbook.addWorksheet(sheetName);

  // Header (row 3 in source = index 2)
  const headers = values[2];
  dst.getRangeByIndexes(0, 0, 1, headers.length).setValues([headers]);
  dst.getRangeByIndexes(0, 0, 1, headers.length).getFormat().getFont().setBold(true);

  let written = 0;
  const out: (string | number | boolean)[][] = [];
  for (let r = 3; r < values.length; r++) {
    if (values[r][2] === segment) {
      out.push(values[r] as (string | number | boolean)[]);
      written++;
    }
  }
  if (out.length > 0) {
    dst.getRangeByIndexes(1, 0, out.length, headers.length).setValues(out);
  }
  dst.getUsedRange()?.getFormat().autofitColumns();
  console.log(`${written} Datensätze aus '${segment}' nach '${sheetName}' kopiert.`);
}
