import re
import urllib.request

url = 'https://kandidat.udir.no/eksamensinfo/FSP6349'
html = urllib.request.urlopen(url, timeout=20).read().decode('utf-8', 'replace')
print('len', len(html))
for pat in ['api', 'graphql', 'eksamensinfo', 'FSP6349', 'window.__', 'dataLayer', '/content/', 'json']:
    print(pat, bool(re.search(pat, html, re.I)))

print('--- script src ---')
for m in re.finditer(r'<script[^>]+src="([^"]+)"', html, re.I):
    print(m.group(1))

print('--- tail ---')
print(html[-2000:])
