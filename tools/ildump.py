import sys
import dnfile
from dncil.cil.body import CilMethodBody
from dncil.cil.error import MethodBodyFormatError
from dncil.clr.token import Token, StringToken, InvalidToken
from dncil.cil.opcode import OpCodes

path = sys.argv[1]
target_class = sys.argv[2].lower()
target_method = sys.argv[3].lower()

pe = dnfile.dnPE(path)
md = pe.net.mdtables

# map methoddef row index -> (class, name)
method_index_of_class = {}
for td in md.TypeDef.rows:
    for entry in td.MethodList:
        method_index_of_class[entry.row_index] = (str(td.TypeNamespace), str(td.TypeName))

def get_method_body(row_index):
    row = md.MethodDef.rows[row_index - 1]
    if row.Rva == 0:
        return None
    off = pe.get_offset_from_rva(row.Rva)
    fh = open(path, 'rb')
    fh.seek(off)
    data = fh.read(0x2000)
    fh.close()
    try:
        from dncil.cil.body.reader import CilMethodBodyReaderBytes
        return CilMethodBody(CilMethodBodyReaderBytes(bytes(data)))
    except MethodBodyFormatError:
        return None

def resolve_token(tok):
    if isinstance(tok, StringToken):
        try:
            return '"' + pe.net.user_strings.get_us(tok.rid).value + '"'
        except Exception:
            return tok.value
    try:
        table = pe.net.mdtables.tables.get(tok.table)
        if table is not None:
            row = table.rows[tok.rid - 1]
            name = getattr(row, 'Name', None)
            parent = ''
            if hasattr(row, 'Class'):
                try:
                    parent = (row.Class.row.TypeNamespace or '') + '.' if row.Class.row else ''
                    parent += row.Class.row.TypeName if row.Class.row else ''
                except Exception:
                    pass
            if name is not None:
                return f"{parent}::{name}" if parent else str(name)
    except Exception:
        pass
    return tok.value

def dump(mi_range, class_name):
    for mi in mi_range:
        ns, tn = method_index_of_class[mi]
        if target_class not in (ns + '.' + tn).lower():
            continue
        row = md.MethodDef.rows[mi - 1]
        if target_method not in str(row.Name).lower():
            continue
        print(f"=== {ns}.{tn}::{row.Name} ===")
        body = get_method_body(mi)
        if body is None:
            print("  (no body)")
            continue
        for insn in body.instructions:
            op = str(insn.opcode)
            operand = ''
            if insn.operand is not None:
                if isinstance(insn.operand, Token):
                    operand = resolve_token(insn.operand)
                else:
                    operand = str(insn.operand)
            print(f"  IL_{insn.offset - body.offset:04X}: {op} {operand}")

n = len(md.MethodDef.rows)
dump(range(1, n + 1), target_class)
