"""Static sweeps over a disassembly listing (disasm/<g>/bank_*.asm) plus merged Mesen code/data logs.
Shared by SB3 and SB4 (tools/sb4 uses this file too).

  python tools/sb3/sweep.py cdl  <out.bin> <log> [...]      merge CDL logs (.hex text, Mesen .cdl, raw .bin)
  python tools/sb3/sweep.py dead  <listing dir> <rom> <cdl.bin>        routines (entry points) that never executed
  python tools/sb3/sweep.py pads  <listing dir> <rom> <cdl.bin> sb3|sb4 pad reads compared with constants / tables / counters
  python tools/sb3/sweep.py flags <listing dir> <rom> <cdl.bin>        RAM tested (load/compare + branch) with no direct write
With no arguments it runs a self-check on a tiny hand-made listing.
Mesen CDL bits: 1 code, 2 data, 4 jump target, 8 sub entry point, $10 X8, $20 M8."""
import os, re, sys
from collections import defaultdict

LINE = re.compile(r'^\s+([A-Z]{3}) ?(\S*)\s*; \$([0-9A-F]{6})  ((?:[0-9A-F]{2} )*[0-9A-F]{2})\s+([mM][xX])')
STOP = {'RTS', 'RTL', 'RTI', 'JMP', 'JML', 'BRA', 'BRL', 'STP'}
BR = {'BEQ', 'BNE', 'BCC', 'BCS', 'BMI', 'BPL', 'BVC', 'BVS'}
TEST = {'LDA', 'LDX', 'LDY', 'BIT', 'CMP', 'CPX', 'CPY', 'AND', 'ORA', 'EOR'}
WRITE = {'STA', 'STX', 'STY', 'STZ', 'INC', 'DEC', 'TSB', 'TRB', 'ASL', 'LSR', 'ROL', 'ROR'}
# pad RAM per game: (addresses, dp-indexed offsets used with X = player base)
PADS = {'sb3': (set(range(0x3B, 0x67)) | set(range(0x036F, 0x037E)), set(range(0x3B, 0x67))),
        'sb4': ({0x01CE, 0x01CF, 0x01D0, 0x01D1} | {b + k * 0x100 + o for b in (0x30, 0x88) for k in range(3, 8) for o in (0, 1)},
                {0x30, 0x31, 0x88, 0x89})}
HW = set(range(0x4016, 0x4018)) | set(range(0x4218, 0x4220))


def load_cdl(paths, size):
    c = bytearray(size)
    for p in paths:
        if p.endswith(('.hex', '.txt')):
            h = open(p).read()
            if 'CDLHEX' in h: h = next(l for l in h.splitlines() if l.startswith('CDLHEX')).split()[-1]
            h = h.strip(); h += '0' * (len(h) & 1); d = bytes.fromhex(h)
            # older dumps looped `for i=1,#c` over Mesen's 0-based table: byte 0 is missing and the rest sit one
            # byte early, so shift them back
            if len(d) == size - 1: d = b'\0' + d
        else:
            d = open(p, 'rb').read()
            if d[:5] == b'CDLv2': d = d[9:]
        if len(d) < size - 1 or len(d) > size:
            print('skip (size)', p, len(d)); continue
        for i, b in enumerate(d): c[i] |= b
    return c


def decode_cdl(rom, cdl):
    """Instructions the logs saw run, decoded straight from each run of code bytes with the logged M/X widths
    (exact, unlike the listing's guesses)."""
    sys.argv[2:] = sys.argv[2:] or ['']  # disasm.py looks at argv for its entries file on import
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    import disasm as D
    ins, i, n = {}, 0, min(len(rom), len(cdl))
    while i < n:
        if not cdl[i] & 1: i += 1; continue
        while i < n and cdl[i] & 1:
            name, mode = D.OPS[rom[i]]; m, x = not cdl[i] & 0x20, not cdl[i] & 0x10
            k = D.size_of(mode, not m, not x); arg = int.from_bytes(rom[i + 1:i + k], 'little')
            txt = D.FMT[mode].format(arg, w=2 if k == 2 else 4) if mode not in ('rel', 'rel16', 'bm') else f'${arg:0{2 * (k - 1)}X}'
            ins[0xC00000 + i] = (name, txt, rom[i:i + k], m, x); i += k
    return ins


def parse(listing, rom=None, cdl=None):
    """-> dict addr -> (mnemonic, operand text, bytes, m16, x16) and the label set. With the ROM and the merged
    log, executed code comes from decode_cdl and listing instructions that overlap it or bytes read as data drop out."""
    ins, labels = {}, set()
    for fn in sorted(os.listdir(listing)):
        if not fn.endswith('.asm'): continue
        for l in open(os.path.join(listing, fn)):
            if l.startswith('L_'): labels.add(int(l[2:8], 16)); continue
            m = LINE.match(l)
            if m: ins[int(m[3], 16)] = (m[1], m[2], bytes.fromhex(m[4]), m[5][0] == 'M', m[5][1] == 'X')
    if rom is not None and cdl is not None:
        ex = decode_cdl(rom, cdl)
        cov = {a + j for a, i in ex.items() for j in range(len(i[2]))}  # Mesen flags opcode bytes; operands too
        ins = {a: i for a, i in ins.items() if not any(cdl[a - 0xC00000 + j] & 3 or a + j in cov for j in range(len(i[2])))}
        ins.update(ex)
    return ins, labels


def target(a, i):
    """Static control-flow target of an instruction, or None."""
    op, arg, b, _, _ = i
    if op in BR or op == 'BRA': return (a & 0xFF0000) | ((a + 2 + (b[1] - 256 if b[1] > 127 else b[1])) & 0xFFFF)
    if op == 'BRL': return (a & 0xFF0000) | ((a + 3 + int.from_bytes(b[1:3], 'little')) & 0xFFFF)
    if op in ('JSR', 'JMP') and len(b) == 3 and b[0] in (0x20, 0x4C): return (a & 0xFF0000) | int.from_bytes(b[1:3], 'little')
    if op in ('JSL', 'JML') and len(b) == 4 and b[0] in (0x22, 0x5C): return int.from_bytes(b[1:4], 'little') | 0xC00000
    return None


def ram(a, i):
    """WRAM address an instruction touches directly (no index), else None. dp = $00xx (D=0), abs < $2000 = low WRAM,
    long $7E/$7F. shortcut: abs >= $2000 depends on DB and is skipped."""
    op, arg, b, _, _ = i
    if ',' in arg or '(' in arg or '[' in arg or arg.startswith('#') or op in ('JMP', 'JSR', 'JML', 'JSL', 'PEA', 'PER', 'BRL', 'MVN', 'MVP'): return None
    v = int.from_bytes(b[1:], 'little')
    if len(b) == 2 and op not in BR and op != 'BRA': return v
    if len(b) == 3 and v < 0x2000: return v
    if len(b) == 4 and (v >> 16) in (0x7E, 0x7F, 0x00): return v & 0xFFFF if v >> 16 == 0 and (v & 0xFFFF) < 0x2000 else (v if v >> 16 else None)
    return None


def routines(ins, labels):
    """Entry points: call targets (JSR/JSL), plus blocks after an unconditional stop (or a db gap) that no
    branch or jump reaches (so reached through a pointer, a jump table, or not at all)."""
    calls, refs, prefs = set(), defaultdict(list), defaultdict(list)
    for a, i in ins.items():
        t = target(a, i)
        if t is not None:
            refs[t].append(a)
            if i[0] in ('JSR', 'JSL'): calls.add(t)
    order = sorted(ins)
    for k, a in enumerate(order):  # code pointers built in registers: LDA #hi / XBA / LDA #lo, 16-bit LDA/LDX/LDY #, PEA
        op, arg, b, _, _ = ins[a]; v = None
        if op == 'XBA' and 0 < k < len(order) - 1:
            p, n = ins[order[k - 1]], ins[order[k + 1]]
            if p[0] == n[0] == 'LDA' and len(p[2]) == len(n[2]) == 2 and p[1].startswith('#') and n[1].startswith('#'):
                v = p[2][1] << 8 | n[2][1]
        elif op in ('LDA', 'LDX', 'LDY', 'PEA') and len(b) == 3 and (arg.startswith('#') or op == 'PEA'):
            v = int.from_bytes(b[1:], 'little')
        if v is not None:
            for t in ((a & 0xFF0000) | v, (a & 0xFF0000) | ((v + 1) & 0xFFFF)):
                if t in ins: prefs[t].append(a)
    ent = set(calls)
    for k, a in enumerate(order[1:], 1):
        p = order[k - 1]
        if (ins[p][0] in STOP or p + len(ins[p][2]) != a) and a not in refs: ent.add(a)
    for t, v in prefs.items(): refs[t] += v
    return sorted(e for e in ent if e in ins), refs


def dead(listing, rom, cdl):
    ins, labels = parse(listing, rom, cdl)
    ent, refs = routines(ins, labels)
    rombytes = rom or b''
    order = sorted(ins); pos = {a: k for k, a in enumerate(order)}
    entset = set(ent); out = []
    for e in ent:
        if cdl[e - 0xC00000] & 1: continue
        body = []; k = pos[e]
        while k < len(order):
            a = order[k]; body.append(a)
            if cdl[a - 0xC00000] & 1: break  # ran into executed code: fall-through tail
            k += 1
            if k < len(order) and (order[k] in entset or order[k] != a + len(ins[a][2])): break
        callers = refs.get(e, [])
        # data decoded as code: bytes the game read as data, opcodes real code here never uses, or calls into
        # the middle of nowhere
        if any(cdl[a - 0xC00000 + j] & 2 for a in body for j in range(len(ins[a][2]))): continue
        if any(ins[a][0] in ('BRK', 'COP', 'WDM', 'STP') for a in body): continue
        if any(ins[a][0] in ('JSR', 'JSL', 'JMP', 'JML') and (t := target(a, ins[a])) is not None and t not in ins for a in body): continue
        if ins[body[-1]][0] not in STOP and not cdl[body[-1] - 0xC00000] & 1 and len(body) > 1: continue
        ptr = 0
        if rombytes:  # 16-bit pointers in the same bank and 24-bit pointers
            lo = (e & 0xFFFF).to_bytes(2, 'little'); bank = (e >> 16) & 0x3F
            lo1 = ((e - 1) & 0xFFFF).to_bytes(2, 'little')  # address-1 for RTS/RTL dispatch
            ptr = rombytes.count(lo + bytes([e >> 16])) + rombytes[bank << 16:(bank + 1) << 16].count(lo) + rombytes.count(lo1 + bytes([e >> 16]))
            if not ptr: ptr = -rombytes.count(lo) - rombytes.count(lo1)  # negative: the word only shows up in other banks
        run = [c for c in callers if cdl[c - 0xC00000] & 1]
        kind = ('referenced by code that ran' if run else 'only from code that never ran' if callers
                else 'pointer/table only' if ptr > 0 else 'no reference')
        out.append((e, len(body), callers, ptr, kind, body))
    return ins, out


def summary(ins, body):
    """RAM touched and calls made by a block, for reading the list quickly."""
    r, w, c = set(), set(), set()
    for a in body:
        i = ins[a]; v = ram(a, i); t = target(a, i)
        if v is not None: (w if i[0] in WRITE else r).add(v)
        if i[0] in ('JSR', 'JSL') and t is not None: c.add(t)
    f = lambda s: ' '.join(f'${x:04X}' if x < 0x10000 else f'${x:06X}' for x in sorted(s)[:8]) + (' ...' if len(s) > 8 else '')
    return f'reads {f(r)} | writes {f(w)} | calls {f(c)}'


def pads(listing, rom, cdl, game):
    """Hits: a pad value loaded/tested, then within 8 instructions a compare with an immediate or a table, a
    bit test with an immediate, or a counter (INC/DEC/CMP on RAM) - the shapes of a button code or tap counter."""
    ins, _ = parse(listing, rom, cdl); padset, dpx = PADS[game]; order = sorted(ins); hits = []

    def padsrc(a):
        op, arg, b, _, _ = ins[a]
        if op not in TEST: return None
        v = ram(a, ins[a]); base = int.from_bytes(b[1:], 'little') if len(b) > 1 else None
        if v is not None and v in padset: return f'${v:04X}'
        if len(b) == 3 and base in HW and ',' not in arg: return arg
        if len(b) in (3, 4) and arg.endswith((',X', ',Y')) and (base & 0xFFFF) in padset and base >> 16 in (0, 0x7E): return arg + ' (pad n)'
        if dpx and len(b) == 2 and arg.endswith(',X') and b[1] in dpx: return arg + ' (object)'
    # helpers that read a pad and return it: their callers' compares count too
    helper = {}
    starts = {target(a, i) for a, i in ins.items() if i[0] in ('JSR', 'JSL')}
    idx = {a: k for k, a in enumerate(order)}
    for t in starts:
        if t not in idx: continue
        body = order[idx[t]:idx[t] + 12]
        s = next((padsrc(x) for x in body if padsrc(x)), None)
        if s and any(ins[x][0] in ('RTS', 'RTL') for x in body): helper[t] = s
    for k, a in enumerate(order):
        op, arg, b, m16, _ = ins[a]
        src = padsrc(a)
        if not src and op in ('JSR', 'JSL') and target(a, ins[a]) in helper: src = f'call {target(a, ins[a]):06X} ({helper[target(a, ins[a])]})'
        if not src: continue
        what = []
        for a2 in order[k + 1:k + 9]:
            o2, g2, b2, _, _ = ins[a2]
            if o2 in ('CMP', 'BIT', 'AND', 'EOR') and g2.startswith('#'): what.append(f'{o2} {g2}')
            elif o2 in ('CMP', 'EOR', 'AND') and (',X' in g2 or ',Y' in g2) and not g2.startswith('$0') or o2 == 'CMP' and len(b2) == 4:
                what.append(f'{o2} {g2} (table)')
            elif o2 in ('INC', 'DEC') and len(b2) > 1 and (int.from_bytes(b2[1:], 'little') & 0xFFFF) not in padset: what.append(f'{o2} {g2} (counter)')
            if o2 in STOP: break
        if what and any(not w.startswith('AND') or '(table)' in w for w in what):
            ran = '' if cdl is None else ('ran' if cdl[a - 0xC00000] & 1 else 'never ran')
            hits.append((a, op, src, what, ran))
    return hits


def flags(listing, rom, cdl):
    """RAM read by a test (load/compare/bit, then a branch within 2 instructions) with no direct write anywhere,
    or written only by code that never ran. Indexed/indirect writes, DMA, MVN and the SB3 script VM can still
    write them, so each candidate needs a Mesen write watch."""
    ins, _ = parse(listing, rom, cdl); order = sorted(ins)
    tests, writes = defaultdict(list), defaultdict(list)
    for k, a in enumerate(order):
        i = ins[a]; v = ram(a, i)
        if v is None: continue
        n = 2 if (i[3] and i[0] in ('LDA', 'BIT', 'CMP', 'AND', 'ORA', 'EOR', 'STA', 'STZ', 'INC', 'DEC', 'TSB', 'TRB')) or (i[4] and i[0] in ('LDX', 'LDY', 'CPX', 'CPY', 'STX', 'STY')) else 1
        if i[0] in WRITE:
            for d in range(n): writes[v + d].append(a)
        elif i[0] in TEST and any(ins[x][0] in BR for x in order[k + 1:k + 3]):
            tests[v].append(a)
    out = []
    for v in sorted(tests):
        wr = writes.get(v, [])
        if not wr: out.append((v, tests[v], [], 'never written'))
        elif cdl is not None and not any(cdl[w - 0xC00000] & 1 for w in wr): out.append((v, tests[v], wr, 'written only by code that never ran'))
    return out


def fmt(v): return f'${v:04X}' if v < 0x10000 else f'${v:06X}'


def selfcheck():
    import tempfile
    d = tempfile.mkdtemp()
    open(os.path.join(d, 'bank_C0.asm'), 'w').write('''L_C00000:
    LDA $4E                         ; $C00000  A5 4E        mx
    CMP #$33                        ; $C00002  C9 33        mx
    BNE L_C00008                    ; $C00004  D0 02        mx
    LDA $1234                       ; $C00006  AD 34 12     mx
L_C00008:
    RTL                             ; $C00009  6B           mx
L_C0000A:
    LDA $0FF0                       ; $C0000A  AD F0 0F     mx
    BEQ L_C0000F                    ; $C0000D  F0 00        mx
    RTS                             ; $C0000F  60           mx
''')
    cdl = bytearray(16); cdl[0] = 1
    ins, out = dead(d, None, cdl)
    assert [o[0] for o in out] == [0xC0000A], out
    assert pads(d, None, None, 'sb3')[0][3] == ['CMP #$33']
    assert [f[0] for f in flags(d, None, cdl)] == [0x4E, 0x0FF0], flags(d, None, cdl)
    print('self-check ok')


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: selfcheck(); sys.exit()
    if a[0] == 'cdl':
        size = int(os.environ.get('SIZE', 0)) or max(os.path.getsize(p) - (9 if p.endswith('.cdl') else 0) for p in a[2:] if not p.endswith('.hex'))
        c = load_cdl(a[2:], size); open(a[1], 'wb').write(c)
        print(f'{len(a) - 2} logs, {size} bytes: code {sum(1 for b in c if b & 1)}, data {sum(1 for b in c if b & 2)}, read {sum(1 for b in c if b & 3)}')
    else:  # <cmd> <listing dir> <rom> <cdl.bin> [game]
        rom, cdl = open(a[2], 'rb').read(), open(a[3], 'rb').read()
        if a[0] == 'dead':
            ins, out = dead(a[1], rom, cdl)
            print(f'{len(out)} routines never executed')
            for e, n, callers, ptr, kind, body in out:
                print(f'{e:06X} {n:4d} ins  {kind:32s} callers {" ".join(f"{c:06X}" for c in callers[:4])}  ptr {ptr}  {summary(ins, body)}')
        elif a[0] == 'pads':
            for h in pads(a[1], rom, cdl, a[4]): print(f'{h[0]:06X} {h[1]} {h[2]:14s} {"; ".join(h[3]):60s} {h[4]}')
        elif a[0] == 'flags':
            for v, t, w, why in flags(a[1], rom, cdl):
                print(f'{fmt(v):8s} {why:36s} tested at {" ".join(f"{x:06X}" for x in t[:5])}' + (f'  written at {" ".join(f"{x:06X}" for x in w[:5])}' if w else ''))
