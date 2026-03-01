// Quick analysis of what index values are used
const fs = require('fs');
const path = require('path');

const filePath = path.join('c:', 'Users', 'sasch', 'Kandidatark', 'data', 'examDatabaseCompact.js');
const content = fs.readFileSync(filePath, 'utf-8');

// Extract all entries
const dbMatch = content.match(/window\.examDatabaseCompact\s*=\s*\{([^}]+)\}/s);
if (!dbMatch) {
    console.log('Could not find database');
    process.exit(1);
}

const dbContent = dbMatch[1];
const entries = dbContent.match(/'[^']+'\s*:\s*\[[^\]]+\]/g);

const indexCounts = {};

entries.forEach(entry => {
    const match = entry.match(/\[([^\]]+)\]/);
    if (match) {
        const values = match[1].split(',').map(v => v.trim().replace(/'/g, ''));
        const lastValue = values[values.length - 1];
        
        // Check if it's a regular index (not null)
        if (lastValue !== 'null' && !isNaN(parseInt(lastValue))) {
            const index = parseInt(lastValue);
            indexCounts[index] = (indexCounts[index] || 0) + 1;
        }
    }
});

console.log('Index usage in database:');
console.log('='.repeat(40));
Object.keys(indexCounts)
    .map(k => parseInt(k))
    .sort((a, b) => a - b)
    .forEach(index => {
        console.log(`Index ${index}: ${indexCounts[index]} fagkoder`);
    });
