const fs = require('fs');
const path = require('path');

const root = 'c:/Users/sasch/Kandidatark';
const dataPath = path.join(root, 'data', 'examDatabaseCompact.js');

const source = fs.readFileSync(dataPath, 'utf8');
const sandboxWindow = {};
global.window = sandboxWindow;

eval(source);

const db = sandboxWindow.examDatabaseCompact || {};

const textDict = [];
const textIndexByValue = new Map();

const codes = Object.keys(db).sort();
const compactDb = {};

for (const code of codes) {
  const entry = db[code] || [];
  const del1Start = entry[0] ?? null;
  const del1End = entry[1] ?? null;
  const del2Start = entry[2] ?? null;
  const del2End = entry[3] ?? null;
  const helpText = typeof entry[4] === 'string' ? entry[4] : '';

  let helpRef = null;
  if (helpText && helpText.trim().length > 0) {
    if (!textIndexByValue.has(helpText)) {
      textIndexByValue.set(helpText, textDict.length);
      textDict.push(helpText);
    }
    helpRef = textIndexByValue.get(helpText);
  }

  compactDb[code] = [del1Start, del1End, del2Start, del2End, helpRef];
}

const esc = (value) => String(value).replace(/\\/g, '\\\\').replace(/'/g, "\\'");
const q = (value) => (value === null ? 'null' : `'${esc(value)}'`);

const out = [];
out.push('window.examTextDictionary = [');
for (const text of textDict) {
  out.push(`    '${esc(text)}',`);
}
out.push('];');
out.push('');
out.push('window.examDatabaseCompact = {');
for (const code of codes) {
  const [d1s, d1e, d2s, d2e, helpRef] = compactDb[code];
  out.push(`    '${code}': [${q(d1s)}, ${q(d1e)}, ${q(d2s)}, ${q(d2e)}, ${helpRef === null ? 'null' : helpRef}],`);
}
out.push('};');
out.push('');

fs.writeFileSync(dataPath, out.join('\n'), 'utf8');

const beforeBytes = Buffer.byteLength(source, 'utf8');
const afterBytes = Buffer.byteLength(out.join('\n'), 'utf8');
console.log(`Codes: ${codes.length}`);
console.log(`Unique help texts: ${textDict.length}`);
console.log(`Before bytes: ${beforeBytes}`);
console.log(`After bytes: ${afterBytes}`);
console.log(`Saved bytes: ${beforeBytes - afterBytes}`);
