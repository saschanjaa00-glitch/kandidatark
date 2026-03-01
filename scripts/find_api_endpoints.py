import re
import urllib.request

js = urllib.request.urlopen('https://kandidat.udir.no/eksamensinfo.js', timeout=30).read().decode('utf-8', 'replace')
print('JS length:', len(js))

# Extract candidate URL-like strings
urls = set(re.findall(r'https?://[^"\'"\s]+', js))
print('Total URLs found:', len(urls))
for u in sorted(urls):
    if '/api' in u.lower() or 'kandidat.udir.no' in u.lower() or 'udir.no' in u.lower():
        print(u)

print('\n--- Strings containing /api ---')
for m in re.finditer(r'[^"\']{0,120}/api[^"\']{0,200}', js):
    s = m.group(0)
    if 'http' in s or 'kandidat' in s or 'eksamen' in s:
        print(s)
