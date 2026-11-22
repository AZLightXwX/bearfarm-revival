import sys, re

path = sys.argv[1]
data = open(path, 'rb').read()

def extract(minlen=4):
    # ASCII strings
    pat = re.compile(rb'[\x20-\x7e]{%d,}' % minlen)
    for m in pat.finditer(data):
        yield m.group().decode('ascii', 'ignore')
    # UTF-16LE strings
    pat2 = re.compile(rb'(?:[\x20-\x7e]\x00){%d,}' % minlen)
    for m in pat2.finditer(data):
        yield m.group().decode('utf-16-le', 'ignore')

out = sys.argv[2]
seen = set()
with open(out, 'w', encoding='utf-8') as f:
    for s in extract(4):
        if s not in seen:
            seen.add(s)
            f.write(s + '\n')
print('strings:', len(seen))
