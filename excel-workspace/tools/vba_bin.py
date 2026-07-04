#!/usr/bin/env python3
"""Erzeugt vbaProject.bin von Grund auf (MS-CFB + MS-OVBA).

Module: ThisWorkbook (Dokument-Modul) + Standard-Module aus vba_src/*.bas
Verifikation: olevba extrahiert den Quellcode wieder (unabhängiger Parser).
"""
import struct, os
from ovba_compress import compress

CODEPAGE = 1252
PROJECT_NAME = "VBAProject"
PROJECT_ID = "{9F10AB9C-89AC-4C0F-8AFB-8E9B96D4C583}"

FREESECT   = 0xFFFFFFFF
ENDOFCHAIN = 0xFFFFFFFE
FATSECT    = 0xFFFFFFFD

# ---------------------------------------------------------------------------
# MS-OVBA: dir-Stream, PROJECT, PROJECTwm
# ---------------------------------------------------------------------------

def rec(rid, payload):
    return struct.pack("<HI", rid, len(payload)) + payload

def dir_stream(modules):
    """modules: Liste (name, ist_dokument_modul)"""
    out = b""
    out += rec(0x0001, struct.pack("<I", 1))            # SYSKIND Win32
    out += rec(0x0002, struct.pack("<I", 0x409))        # LCID
    out += rec(0x0014, struct.pack("<I", 0x409))        # LCIDINVOKE
    out += rec(0x0003, struct.pack("<H", CODEPAGE))     # CODEPAGE
    out += rec(0x0004, PROJECT_NAME.encode("cp1252"))   # NAME
    out += rec(0x0005, b"") + rec(0x0040, b"")          # DOCSTRING + Unicode
    out += rec(0x0006, b"") + rec(0x003D, b"")          # HELPFILE 1+2
    out += rec(0x0007, struct.pack("<I", 0))            # HELPCONTEXT
    out += rec(0x0008, struct.pack("<I", 0))            # LIBFLAGS
    out += struct.pack("<HI", 0x0009, 4) + struct.pack("<IH", 1, 0)  # VERSION
    out += rec(0x000C, b"") + rec(0x003C, b"")          # CONSTANTS + Unicode

    refs = [
        ("stdole", "*\\G{00020430-0000-0000-C000-000000000046}#2.0#0#C:\\Windows\\system32\\stdole2.tlb#OLE Automation"),
        ("Office", "*\\G{2DF8D04C-5BFA-101B-BDE5-00AA0044DE52}#2.0#0#C:\\Program Files\\Common Files\\Microsoft Shared\\OFFICE14\\MSO.DLL#Microsoft Office 14.0 Object Library"),
    ]
    for name, libid in refs:
        out += rec(0x0016, name.encode("cp1252"))               # REFERENCENAME
        out += rec(0x003E, name.encode("utf-16-le"))            # ...Unicode
        libid_b = libid.encode("cp1252")
        payload = struct.pack("<I", len(libid_b)) + libid_b + b"\x00\x00\x00\x00" + b"\x00\x00"
        out += rec(0x000D, payload)                             # REFERENCEREGISTERED

    out += rec(0x000F, struct.pack("<H", len(modules)))         # MODULES count
    out += rec(0x0013, struct.pack("<H", 0xFFFF))               # COOKIE
    for name, is_doc in modules:
        nm = name.encode("cp1252")
        out += rec(0x0019, nm)                                  # MODULENAME
        out += rec(0x0047, name.encode("utf-16-le"))            # ...Unicode
        out += rec(0x001A, nm)                                  # STREAMNAME
        out += rec(0x0032, name.encode("utf-16-le"))            # ...Unicode
        out += rec(0x001C, b"") + rec(0x0048, b"")              # DOCSTRING
        out += rec(0x0031, struct.pack("<I", 0))                # OFFSET = 0
        out += rec(0x001E, struct.pack("<I", 0))                # HELPCONTEXT
        out += rec(0x002C, struct.pack("<H", 0xFFFF))           # COOKIE
        out += rec(0x0022 if is_doc else 0x0021, b"")           # TYPE
        out += struct.pack("<HI", 0x002B, 0)                    # Terminator
    out += struct.pack("<HI", 0x0010, 0)                        # dir-Terminator
    return out

def encrypt_property(data: bytes, seed: int) -> str:
    """MS-OVBA §2.4.3.2 Data Encryption."""
    version = 2
    projkey = sum(PROJECT_ID.encode("cp1252")) & 0xFF
    out = [seed, seed ^ version, seed ^ projkey]
    enc_prev = out[2]
    unenc_prev = projkey
    def eb(b):
        nonlocal enc_prev, unenc_prev
        e = b ^ ((enc_prev + unenc_prev) & 0xFF)
        out.append(e)
        enc_prev, unenc_prev = e, b
    for _ in range((seed & 6) >> 1):
        eb(0)
    for b in struct.pack("<I", len(data)):
        eb(b)
    for b in data:
        eb(b)
    return "".join(f"{x:02X}" for x in out)

def project_stream(doc_modules, std_modules):
    cmg = encrypt_property(b"\x00\x00\x00\x00", 0x11)   # kein Schutz
    dpb = encrypt_property(b"\x00", 0x23)               # kein Passwort
    gc = encrypt_property(b"\xFF", 0x35)                # sichtbar
    lines = [f'ID="{PROJECT_ID}"']
    for m in doc_modules:
        lines.append(f"Document={m}/&H00000000")
    for m in std_modules:
        lines.append(f"Module={m}")
    lines += [
        f'Name="{PROJECT_NAME}"',
        'HelpContextID="0"',
        'VersionCompatible32="393222000"',
        f'CMG="{cmg}"',
        f'DPB="{dpb}"',
        f'GC="{gc}"',
        "",
        "[Host Extender Info]",
        "&H00000001={3832D640-CF90-11CF-8E43-00A0C911005A};VBE;&H00000000",
        "",
        "[Workspace]",
    ]
    for m in doc_modules + std_modules:
        lines.append(f"{m}=0, 0, 0, 0, C")
    return ("\r\n".join(lines) + "\r\n").encode("cp1252")

def projectwm_stream(all_modules):
    out = b""
    for m in all_modules:
        out += m.encode("cp1252") + b"\x00" + m.encode("utf-16-le") + b"\x00\x00"
    out += b"\x00\x00"
    return out

# ---------------------------------------------------------------------------
# MS-CFB Compound File Writer
# ---------------------------------------------------------------------------

class Entry:
    def __init__(self, name, etype, data=None):
        self.name = name
        self.type = etype          # 5 root, 1 storage, 2 stream
        self.data = data or b""
        self.children = []
        self.id = None
        self.left = FREESECT
        self.right = FREESECT
        self.child = FREESECT
        self.start = ENDOFCHAIN
        self.size = 0

def cfb_name_key(name):
    return (len(name), name.upper())

def build_tree(children):
    """Balancierter BST über die (CFB-sortierten) Kinder; liefert Wurzel-ID."""
    if not children:
        return FREESECT
    children = sorted(children, key=lambda e: cfb_name_key(e.name))
    def bst(lo, hi):
        if lo > hi:
            return FREESECT
        mid = (lo + hi) // 2
        node = children[mid]
        node.left = bst(lo, mid - 1)
        node.right = bst(mid + 1, hi)
        return node.id
    return bst(0, len(children) - 1)

def write_cfb(streams: dict) -> bytes:
    """streams: {'PROJECT': b..., 'VBA/dir': b..., ...}"""
    root = Entry("Root Entry", 5)
    storages = {"": root}
    entries = [root]
    for path, data in streams.items():
        parts = path.split("/")
        parent = ""
        for p in parts[:-1]:
            full = parent + "/" + p if parent else p
            if full not in storages:
                st = Entry(p, 1)
                entries.append(st)
                storages[full] = st
                storages[parent].children.append(st)
            parent = full
        e = Entry(parts[-1], 2, data)
        e.size = len(data)
        entries.append(e)
        storages[parent].children.append(e)

    for i, e in enumerate(entries):
        e.id = i
    for st in storages.values():
        st.child = build_tree(st.children)

    SEC = 512
    MINI = 64
    big = [e for e in entries if e.type == 2 and e.size >= 4096]
    small = [e for e in entries if e.type == 2 and e.size < 4096]

    # Ministream zusammensetzen
    mini_data = b""
    for e in small:
        e.start = len(mini_data) // MINI if e.size > 0 else ENDOFCHAIN
        d = e.data
        pad = (-len(d)) % MINI
        mini_data += d + b"\x00" * pad
    n_mini_sects = len(mini_data) // MINI
    root.size = len(mini_data)

    # MiniFAT
    minifat = []
    pos = 0
    for e in small:
        if e.size == 0:
            continue
        n = (e.size + MINI - 1) // MINI
        for k in range(n - 1):
            minifat.append(pos + k + 1)
        minifat.append(ENDOFCHAIN)
        pos += n
    minifat_bytes = b"".join(struct.pack("<I", x) for x in minifat)
    pad = (-len(minifat_bytes)) % SEC
    minifat_bytes += struct.pack("<I", FREESECT) * (pad // 4)
    n_minifat_sects = len(minifat_bytes) // SEC

    # Directory
    n_dir_sects_guess = (len(entries) * 128 + SEC - 1) // SEC

    # Sektor-Layout: [dir][minifat][ministream][big streams][FAT]
    def layout(n_fat):
        sec = 0
        first_dir = sec; sec += n_dir_sects_guess
        first_minifat = sec if n_minifat_sects else ENDOFCHAIN
        sec += n_minifat_sects
        first_mini = sec if n_mini_sects else ENDOFCHAIN
        n_mini_container = (len(mini_data) + SEC - 1) // SEC
        sec += n_mini_container
        big_starts = []
        for e in big:
            big_starts.append(sec)
            sec += (e.size + SEC - 1) // SEC
        first_fat = sec; sec += n_fat
        return first_dir, first_minifat, first_mini, n_mini_container, big_starts, first_fat, sec

    n_fat = 1
    while True:
        (first_dir, first_minifat, first_mini, n_mini_container,
         big_starts, first_fat, total) = layout(n_fat)
        need = (total + 127) // 128
        if need <= n_fat:
            break
        n_fat = need
    assert n_fat <= 109, "DIFAT-Erweiterung nicht implementiert (nicht nötig)"

    # Kettenaufbau im FAT
    fat = [FREESECT] * (n_fat * 128)
    def chain(start, count):
        for k in range(count - 1):
            fat[start + k] = start + k + 1
        if count > 0:
            fat[start + count - 1] = ENDOFCHAIN
    chain(first_dir, n_dir_sects_guess)
    if n_minifat_sects:
        chain(first_minifat, n_minifat_sects)
    if n_mini_container:
        chain(first_mini, n_mini_container)
    for e, s in zip(big, big_starts):
        e.start = s
        chain(s, (e.size + SEC - 1) // SEC)
    for k in range(n_fat):
        fat[first_fat + k] = FATSECT

    root.start = first_mini if n_mini_container else ENDOFCHAIN

    # Directory-Bytes
    def dir_entry(e):
        name = e.name[:31]
        nb = name.encode("utf-16-le") + b"\x00\x00"
        buf = nb + b"\x00" * (64 - len(nb))
        buf += struct.pack("<H", len(nb))
        buf += struct.pack("<BB", e.type, 1)          # schwarz
        buf += struct.pack("<III", e.left, e.right, e.child)
        buf += b"\x00" * 16                            # CLSID
        buf += struct.pack("<I", 0)                    # state
        buf += b"\x00" * 16                            # Zeiten
        buf += struct.pack("<I", e.start if e.type in (2, 5) and (e.size or e.type == 5) else 0)
        buf += struct.pack("<Q", e.size)
        return buf

    dir_bytes = b"".join(dir_entry(e) for e in entries)
    empty = (b"\x00" * 64 + struct.pack("<H", 0) + struct.pack("<BB", 0, 0) +
             struct.pack("<III", FREESECT, FREESECT, FREESECT) + b"\x00" * 16 +
             struct.pack("<I", 0) + b"\x00" * 16 + struct.pack("<I", 0) + struct.pack("<Q", 0))
    while len(dir_bytes) % SEC:
        dir_bytes += empty

    # Header
    hdr = b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"
    hdr += b"\x00" * 16
    hdr += struct.pack("<HH", 0x003E, 0x0003)
    hdr += struct.pack("<H", 0xFFFE)
    hdr += struct.pack("<HH", 0x0009, 0x0006)
    hdr += b"\x00" * 6
    hdr += struct.pack("<I", 0)                        # dir sectors (v3: 0)
    hdr += struct.pack("<I", n_fat)
    hdr += struct.pack("<I", first_dir)
    hdr += struct.pack("<I", 0)                        # transaction
    hdr += struct.pack("<I", 4096)                     # mini cutoff
    hdr += struct.pack("<I", first_minifat if n_minifat_sects else ENDOFCHAIN)
    hdr += struct.pack("<I", n_minifat_sects)
    hdr += struct.pack("<I", ENDOFCHAIN)               # first DIFAT
    hdr += struct.pack("<I", 0)                        # n DIFAT
    difat = [first_fat + k for k in range(n_fat)]
    difat += [FREESECT] * (109 - len(difat))
    hdr += b"".join(struct.pack("<I", x) for x in difat)
    assert len(hdr) == 512

    # Body zusammensetzen
    body = bytearray(b"\x00" * (total * SEC))
    def put_at(sector, data):
        body[sector * SEC: sector * SEC + len(data)] = data
    put_at(first_dir, dir_bytes)
    if n_minifat_sects:
        put_at(first_minifat, minifat_bytes)
    if n_mini_container:
        put_at(first_mini, mini_data)
    for e, s in zip(big, big_starts):
        put_at(s, e.data)
    fat_bytes = b"".join(struct.pack("<I", x) for x in fat)
    put_at(first_fat, fat_bytes)
    return hdr + bytes(body)

# ---------------------------------------------------------------------------

def build_bin(out_path="vbaProject.bin"):
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vba_src")
    doc_modules = ["ThisWorkbook"]
    std_modules = []
    sources = {}
    sources["ThisWorkbook"] = open(os.path.join(src_dir, "ThisWorkbook.cls"), "rb").read()
    for f in sorted(os.listdir(src_dir)):
        if f.endswith(".bas"):
            name = f[:-4]
            std_modules.append(name)
            sources[name] = open(os.path.join(src_dir, f), "rb").read()
    all_modules = doc_modules + std_modules

    # Quelltexte: CRLF & cp1252 sicherstellen
    for k, v in sources.items():
        txt = v.decode("utf-8")
        txt = txt.replace("\r\n", "\n").replace("\n", "\r\n")
        sources[k] = txt.encode("cp1252")

    streams = {
        "PROJECT": project_stream(doc_modules, std_modules),
        "PROJECTwm": projectwm_stream(all_modules),
        "VBA/_VBA_PROJECT": b"\xCC\x61\xFF\xFF\x00\x00\x00",
        "VBA/dir": compress(dir_stream(
            [(m, True) for m in doc_modules] + [(m, False) for m in std_modules])),
    }
    for m in all_modules:
        streams["VBA/" + m] = compress(sources[m])

    blob = write_cfb(streams)
    open(out_path, "wb").write(blob)
    print(f"OK -> {out_path} ({len(blob)} Bytes), Module: {all_modules}")
    return out_path, sources

if __name__ == "__main__":
    path, sources = build_bin()
    # Verifikation 1: olefile kann Container lesen
    import olefile
    ole = olefile.OleFileIO(path)
    print("OLE-Streams:", ole.listdir())
    # Verifikation 2: olevba extrahiert die Quelltexte (unabhängiger MS-OVBA-Parser)
    from oletools.olevba import VBA_Parser
    p = VBA_Parser(path)
    ok = True
    got = {}
    for (_, _, mod_name, code) in p.extract_all_macros():
        got[mod_name.replace(".bas", "").replace(".cls", "")] = code
    for m, src in sources.items():
        expect = src.decode("cp1252")
        # olevba liefert Quelltext ohne Attribute-Zeilen? -> Vergleich: enthalten
        g = got.get(m, "")
        core = [l for l in expect.splitlines() if not l.startswith("Attribute ")]
        gl = g.splitlines()
        missing = [l for l in core if l not in gl]
        status = "OK" if not missing else f"FEHLT {len(missing)} Zeilen: {missing[:3]}"
        if missing:
            ok = False
        print(f"  Modul {m}: {status}")
    print("VERIFIKATION:", "OK" if ok else "FEHLGESCHLAGEN")
