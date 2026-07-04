#!/usr/bin/env python3
"""MS-OVBA Kompression (MS-OVBA §2.4.1) — eigene, spez-konforme Implementierung.

Container = 0x01 + Chunks. Chunk = 2-Byte-Header + Daten.
Header: Bits 0-11 = Gesamtgröße-3, Bits 12-14 = 0b011, Bit 15 = komprimiert.
Komprimierte Daten: Gruppen aus FlagByte + 8 Tokens (Literal-Byte oder 2-Byte-CopyToken).
CopyToken: BitCount = max(4, ceil(log2(pos_im_chunk))), LengthBits = 16-BitCount,
           Token = (Offset-1) << LengthBits | (Länge-3).
"""

def _match(data, chunk_start, pos, end):
    """Längster Match (offset, length) im Fenster [chunk_start, pos)."""
    difference = pos - chunk_start
    if difference == 0:
        return 0, 0
    bitcount = 4
    while (1 << bitcount) < difference:
        bitcount += 1
    max_len = ((1 << (16 - bitcount)) - 1) + 3
    best_off, best_len = 0, 0
    # Suche rückwärts (nahe Offsets zuerst — gleich gut, schneller gefunden)
    limit = min(max_len, end - pos)
    if limit < 3:
        return 0, 0
    for off in range(1, difference + 1):
        src = pos - off
        l = 0
        while l < limit and data[src + (l % off)] == data[pos + l]:
            l += 1
        if l > best_len:
            best_len, best_off = l, off
            if l >= limit:
                break
    if best_len < 3:
        return 0, 0
    return best_off, best_len

def _compress_chunk(data, chunk_start, chunk_end):
    """Komprimiert data[chunk_start:chunk_end] (<= 4096 Bytes). Liefert Chunk-Bytes."""
    out = bytearray()
    pos = chunk_start
    while pos < chunk_end:
        flag = 0
        group = bytearray()
        for bit in range(8):
            if pos >= chunk_end:
                break
            off, ln = _match(data, chunk_start, pos, chunk_end)
            if ln >= 3:
                difference = pos - chunk_start
                bitcount = 4
                while (1 << bitcount) < difference:
                    bitcount += 1
                lengthbits = 16 - bitcount
                token = ((off - 1) << lengthbits) | (ln - 3)
                group += token.to_bytes(2, "little")
                flag |= (1 << bit)
                pos += ln
            else:
                group.append(data[pos])
                pos += 1
        out.append(flag)
        out += group
    size = len(data[chunk_start:chunk_end])
    if len(out) >= 4096:
        # nicht komprimierbar -> Raw Chunk (4096 Bytes, ggf. mit Leerzeichen gepolstert)
        raw = bytearray(data[chunk_start:chunk_end])
        raw += b" " * (4096 - len(raw))
        header = 0x3000 | (4098 - 3)          # Flag=0, 0b011, Größe 4098
        return header.to_bytes(2, "little") + bytes(raw)
    total = len(out) + 2
    header = 0xB000 | (total - 3)             # Flag=1, 0b011
    return header.to_bytes(2, "little") + bytes(out)

def compress(data: bytes) -> bytes:
    out = bytearray(b"\x01")
    for start in range(0, len(data), 4096):
        end = min(start + 4096, len(data))
        out += _compress_chunk(data, start, end)
    return bytes(out)

if __name__ == "__main__":
    from oletools.olevba import decompress_stream
    import os
    tests = [
        b"",
        b"a",
        b"#aaabcdefaaaaabcdefaaaaaaaa" * 3,
        ("Attribute VB_Name = \"Test\"\r\nOption Explicit\r\n" * 400).encode("cp1252"),
        os.urandom(10000),                      # inkompressibel -> Raw Chunks
        ("x" * 4096 + "y" * 4096 + "z" * 100).encode(),
        open("/usr/bin/soffice", "rb").read()[:20000],
    ]
    ok = True
    for i, t in enumerate(tests):
        c = compress(t)
        back = decompress_stream(bytearray(c))
        # Raw-Chunk-Polsterung: nur beim letzten Chunk möglich -> Vergleich auf Präfix
        if back == t:
            res = "OK exakt"
        elif back[:len(t)] == t and all(b == 0x20 for b in back[len(t):]):
            res = "OK (Raw-Polster)"
        else:
            res = "FEHLER"; ok = False
        print(f"Test {i}: len {len(t)} -> {len(c)} : {res}")
    print("GESAMT:", "OK" if ok else "FEHLGESCHLAGEN")
