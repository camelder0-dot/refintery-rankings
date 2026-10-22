#!/usr/bin/env node
/** Export the frozen data matrices as UTF-8 CSV.
 * Initial authoring uses @oai/artifact-tool when available.
 * --stdlib reproduces the exact CSV using Node alone; no spreadsheet package needed.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const args = process.argv.slice(2);
const rootIndex = args.indexOf('--root');
if (rootIndex >= 0 && !args[rootIndex + 1]) throw new Error('--root requires a repository path');
const root = rootIndex >= 0
  ? path.resolve(args[rootIndex + 1])
  : path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const useStandardLibrary = args.includes('--stdlib');
const previewIndex = args.indexOf('--preview-dir');
const previewDirectory = previewIndex >= 0 ? args[previewIndex + 1] : null;
const data = JSON.parse(await fs.readFile(path.join(root, 'artifacts/export-tables.json'), 'utf8'));
let workbook;
if (!useStandardLibrary) {
  const { Workbook } = await import('@oai/artifact-tool');
  workbook = Workbook.create();
}

function csvCell(value) {
  if (value === null || value === undefined) return '';
  const text = String(value);
  return /[",\r\n]/.test(text) ? '"' + text.replaceAll('"', '""') + '"' : text;
}

for (const table of data.tables) {
  const matrix = [table.headers, ...table.rows];
  if (matrix.some(row => row.length !== table.headers.length)) {
    throw new Error(`Non-rectangular matrix: ${table.name}`);
  }
  if (matrix.flat().some(value => typeof value === 'string' && /^[=+@\t\r]/.test(value))) {
    throw new Error(`Unexpected spreadsheet formula/control prefix in a text field: ${table.name}`);
  }
  let values = matrix;
  if (workbook) {
    const sheet = workbook.worksheets.add(table.name);
    const range = sheet.getRangeByIndexes(0, 0, matrix.length, table.headers.length);
    range.format.numberFormat = matrix.map(row => row.map(value => typeof value === 'string' ? '@' : 'General'));
    range.values = matrix;
    range.format.font = { name: 'Arial', size: 10 };
    range.format.rowHeight = 24;
    range.format.columnWidth = 18;
    sheet.showGridLines = false;
    const header = sheet.getRangeByIndexes(0, 0, 1, table.headers.length);
    header.format.fill = '#24374A';
    header.format.font.color = '#FFFFFF';
    header.format.font.bold = true;
    header.format.rowHeight = 36;
    header.format.wrapText = true;
    sheet.getRange('A:A').format.columnWidth = 13;
    sheet.getRange('B:B').format.columnWidth = table.name === 'Teams' ? 26 : 24;
    sheet.getRange('C:C').format.columnWidth = table.name === 'Teams' ? 59 : 27;
    sheet.getRange('D:D').format.columnWidth = table.name === 'Teams' ? 16 : 72;
    sheet.freezePanes.freezeRows(1);
    // The spreadsheet runtime may normalize ISO strings to Date objects.
    // Preserve the source's exact spelling only after confirming the same instant.
    values = range.values.map((row, rowIndex) => row.map((value, columnIndex) => {
      const original = matrix[rowIndex][columnIndex];
      if (typeof original === 'string'
          && /^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)?$/.test(original)
          && (value instanceof Date || typeof value === 'string')
          && Number.isFinite(Date.parse(original))
          && new Date(value).getTime() === Date.parse(original)) return original;
      return value;
    }));
    if (JSON.stringify(values) !== JSON.stringify(matrix)) {
      const differences = [];
      for (let row = 0; row < matrix.length; row++) {
        for (let column = 0; column < matrix[row].length; column++) {
          if (values[row]?.[column] !== matrix[row][column]) {
            differences.push({ row, column, input: matrix[row][column], output: values[row]?.[column] });
          }
        }
      }
      throw new Error(`Spreadsheet authoring changed input values: ${table.name}: ${JSON.stringify(differences.slice(0, 5))}`);
    }
  }
  const output = values.map(row => row.map(csvCell).join(',')).join('\n') + '\n';
  await fs.writeFile(path.join(root, table.output), output, 'utf8');
  console.log(`Exported ${table.rows.length} rows: ${table.output}`);
}

if (workbook) {
  workbook.recalculate();
  const errors = await workbook.inspect({
    kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',
    options: { useRegex: true, maxResults: 20 }, maxChars: 1000,
  });
  console.log(errors.ndjson);
  if (previewDirectory) {
    await fs.mkdir(previewDirectory, { recursive: true });
    for (const [sheetName, range] of [['Teams', 'A1:F18'], ['Leadership', 'A1:D10']]) {
      const preview = await workbook.render({ sheetName, range, scale: 1.5, format: 'png' });
      await fs.writeFile(path.join(previewDirectory, sheetName.toLowerCase() + '.png'), new Uint8Array(await preview.arrayBuffer()));
    }
  }
}
