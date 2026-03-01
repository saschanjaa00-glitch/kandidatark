// Convert database to use pattern references
const fs = require('fs');
const path = require('path');

const filePath = path.join('c:', 'Users', 'sasch', 'Kandidatark', 'data', 'examDatabaseCompact.js');
const content = fs.readFileSync(filePath, 'utf-8');

// Extract text dictionary
const textDictMatch = content.match(/window\.examTextDictionary\s*=\s*\[([^\]]+(?:\][^\]]*)*)\];/s);
if (!textDictMatch) {
    console.log('Could not find text dictionary');
    process.exit(1);
}
const textDictContent = textDictMatch[0];

// Extract database
const dbMatch = content.match(/window\.examDatabaseCompact\s*=\s*\{([^}]+)\}/s);
if (!dbMatch) {
    console.log('Could not find database');
    process.exit(1);
}

const dbContent = dbMatch[1];
const entries = dbContent.match(/'[^']+'\s*:\s*\[[^\]]+\]/g);

// Build pattern map
const patternMap = new Map();
const patternList = [];
const newEntries = [];

entries.forEach(entry => {
    const match = entry.match(/'([^']+)'\s*:\s*\[([^\]]+)\]/);
    if (match) {
        const fagkode = match[1];
        const pattern = match[2];
        
        if (!patternMap.has(pattern)) {
            patternMap.set(pattern, patternList.length);
            patternList.push(`[${pattern}]`);
        }
        
        const patternIndex = patternMap.get(pattern);
        newEntries.push(`    '${fagkode}': ${patternIndex}`);
    }
});

// Generate new file content
let output = textDictContent + '\n\n';

output += 'window.examPatterns = [\n';
output += '    ' + patternList.join(',\n    ') + '\n';
output += '];\n\n';

output += 'window.examDatabaseCompact = {\n';
output += newEntries.join(',\n') + '\n';
output += '};\n';

// Write to file
fs.writeFileSync(filePath, output, 'utf-8');

console.log('✅ Database optimized!');
console.log(`   Patterns: ${patternList.length}`);
console.log(`   Fagkodes: ${newEntries.length}`);
console.log(`   Original size: ${content.length} bytes`);
console.log(`   New size: ${output.length} bytes`);
console.log(`   Savings: ${((content.length - output.length) / content.length * 100).toFixed(1)}%`);
