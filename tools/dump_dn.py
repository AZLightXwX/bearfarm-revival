import sys, os, re, json
import dnfile

def get_user_strings(pe):
    us = pe.net.user_strings
    heap_size = us.struct.Size
    out = []
    idx = 1
    seen = set()
    while idx < heap_size:
        try:
            vb, size = us.get_with_size(idx)
        except Exception:
            break
        if size <= 0:
            break
        if vb:
            try:
                v = vb.decode('utf-16-le', errors='ignore')
            except Exception:
                v = vb.decode('utf-8', errors='ignore')
            if v and v not in seen:
                seen.add(v)
                out.append(v)
        idx += size
    return out

def dump(path, outdir):
    base = os.path.splitext(os.path.basename(path))[0]
    pe = dnfile.dnPE(path)
    md = pe.net.mdtables
    os.makedirs(outdir, exist_ok=True)

    types, methods, fields = [], [], []
    if md.TypeDef:
        for row in md.TypeDef.rows:
            ns = row.TypeNamespace or ''
            nm = row.TypeName or ''
            types.append(f"{ns}.{nm}" if ns else nm)
    if md.MethodDef:
        for row in md.MethodDef.rows:
            methods.append(str(row.Name))
    if md.Field:
        for row in md.Field.rows:
            fields.append(str(row.Name))

    ustrings = get_user_strings(pe)

    for name, data in ((base + '.types.txt', types), (base + '.methods.txt', methods),
                       (base + '.fields.txt', fields), (base + '.ustrings.txt', ustrings)):
        with open(os.path.join(outdir, name), 'w', encoding='utf-8') as f:
            f.write('\n'.join(data))

    return {
        'dll': base, 'types': len(types), 'methods': len(methods),
        'fields': len(fields), 'ustrings': len(ustrings),
        'sample_types': types[:10],
    }

if __name__ == '__main__':
    src, outdir = sys.argv[1], sys.argv[2]
    for fn in sorted(os.listdir(src)):
        if not fn.lower().endswith('.dll'):
            continue
        try:
            print(json.dumps(dump(os.path.join(src, fn), outdir), ensure_ascii=False))
        except Exception as e:
            print(json.dumps({'dll': fn, 'error': str(e)}, ensure_ascii=False))
