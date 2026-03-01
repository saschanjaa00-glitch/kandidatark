import urllib.request
import re

js = urllib.request.urlopen('https://kandidat.udir.no/eksamensinfo.js', timeout=30).read().decode('utf-8', 'replace')

for pat in [r'/api/eksamen-info[^"\']*', r'hjelpemidler', r'automatisk tekstgenerator', r'oversettelsesprogram']:
    print(f'=== Pattern: {pat} ===')
    count = 0
    for m in re.finditer(pat, js, flags=re.IGNORECASE):
        i = m.start()
        print(js[max(0, i-220):i+280])
        print('---')
        count += 1
        if count >= 5:
            break
    print('matches shown:', count)
    print()
