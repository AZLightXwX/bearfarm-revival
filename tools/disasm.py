import sys
from elftools.elf.elffile import ELFFile
from capstone import *

so_path, out_path = sys.argv[1], sys.argv[2]
targets = sys.argv[3:] if len(sys.argv) > 3 else []

f = open(so_path, 'rb')
elf = ELFFile(f)
symtab = elf.get_section_by_name('.dynsym')

syms = {}
for s in symtab.iter_symbols():
    if s['st_info']['type'] == 'STT_FUNC' and s['st_size'] > 0:
        syms[s.name] = (s['st_value'], s['st_size'])

text = elf.get_section_by_name('.text')
text_addr = text['sh_addr']
text_data = text.data()
text_off = text['sh_offset']

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_ARM)
md.detail = False

out = open(out_path, 'w', encoding='utf-8')
for name, (addr, size) in sorted(syms.items(), key=lambda kv: kv[1][0]):
    if targets and not any(t in name for t in targets):
        continue
    # ARM/Thumb: st_value has LSB set for thumb
    thumb = addr & 1
    start = addr & ~1
    if not (text_addr <= start < text_addr + len(text_data)):
        continue
    off = start - text_addr
    code = text_data[off:off + size]
    out.write(f"\n===== {name} @ 0x{start:08x} size={size} {'THUMB' if thumb else 'ARM'} =====\n")
    md.mode = CS_MODE_THUMB if thumb else CS_MODE_ARM
    for ins in md.disasm(code, start):
        out.write(f"0x{ins.address:08x}:  {ins.mnemonic} {ins.op_str}\n")
out.close()
print("done, symbols:", len(syms))
