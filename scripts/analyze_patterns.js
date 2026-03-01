// Analyze unique timing patterns in the database
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

const patternMap = new Map();
const fagkodesByPattern = new Map();

entries.forEach(entry => {
    const match = entry.match(/'([^']+)'\s*:\s*\[([^\]]+)\]/);
    if (match) {
        const fagkode = match[1];
        const pattern = match[2]; // Keep as string for easy comparison
        
        if (!patternMap.has(pattern)) {
            patternMap.set(pattern, patternMap.size);
            fagkodesByPattern.set(pattern, []);
        }
        fagkodesByPattern.get(pattern).push(fagkode);
    }
});

console.log(`Total fagkodes: ${entries.length}`);
console.log(`Unique patterns: ${patternMap.size}\n`);

console.log('Top 10 most common patterns:');
console.log('='.repeat(80));

const sortedPatterns = Array.from(fagkodesByPattern.entries())
    .sort((a, b) => b[1].length - a[1].length)
    .slice(0, 10);

sortedPatterns.forEach(([pattern, codes], index) => {
    console.log(`\n${index + 1}. Pattern: [${pattern}]`);
    console.log(`   Used by ${codes.length} fagkodes`);
    console.log(`   Examples: ${codes.slice(0, 5).join(', ')}${codes.length > 5 ? ', ...' : ''}`);
});

// Calculate potential savings
const currentSize = entries.length * 50; // Rough estimate per line
const newSize = patternMap.size * 50 + entries.length * 15; // Pattern array + simple references
const savings = ((currentSize - newSize) / currentSize * 100).toFixed(1);

console.log('\n' + '='.repeat(80));
console.log(`Estimated size reduction: ${savings}%`);
console.log(`Current: ~${entries.length} lines with full arrays`);
console.log(`Optimized: ~${patternMap.size} pattern definitions + ${entries.length} simple references`);
