#!/usr/bin/env python3
"""Apply the Qin camera arm64 software-scaler fix to the exact stock ELF.

Build camera_scale64.S with the AOSP GCC assembler, link .text at 0x97000,
objcopy to a binary, then pass that binary as the only argument. This patch
never changes the kernel's CPP structure, hardware limits, or 32-bit blob.
"""
from pathlib import Path
import hashlib
import struct
import sys

blob = Path(__file__).resolve().parent.parent / "proprietary/vendor/lib64/libcamoem.so"
data = bytearray(blob.read_bytes())
original_hash = "c4838caae48d5451b8acae63f54caf30d58ee4588b267b5a4b599f14be79363a"
cave = Path(sys.argv[1]).read_bytes()
assert len(cave) == 60
base = 0x97000
hooks = [(0x395a8, 0), (0x39644, 12), (0x39f94, 24), (0x3a058, 44)]
def branch(src, dst):
    assert (dst - src) % 4 == 0 and -(1 << 27) <= dst - src < (1 << 27)
    return struct.pack("<I", 0x14000000 | (((dst - src) // 4) & 0x3ffffff))
if all(data[pc:pc+4] == branch(pc, base+off) for pc, off in hooks):
    assert data[base:base+len(cave)] == cave
    assert hashlib.sha256(data).hexdigest() == "6d3e2c61d3fe82a477ee32fa4b8665920f3f459d835f66f9ab7648d7ca11b9e3"
    print("Already patched", hashlib.sha256(data).hexdigest())
    sys.exit(0)
assert hashlib.sha256(data).hexdigest() == original_hash, "Unexpected libcamoem ELF"
assert data[:5] == b"\x7fELF\x02"
assert struct.unpack_from("<H", data, 18)[0] == 183  # AArch64
phoff = struct.unpack_from("<Q", data, 32)[0]
entsize, count = struct.unpack_from("<HH", data, 54)
rx = None
for i in range(count):
    pos = phoff + i * entsize
    typ, flags, offset, va, _, size, memsize, _ = struct.unpack_from("<IIQQQQQQ", data, pos)
    if typ == 1 and flags == 5 and offset == 0 and va == 0:
        assert size == memsize == 0x96e14
        rx = pos
    if typ == 1 and offset:
        assert offset > base + len(cave) and va > base + len(cave)
assert rx is not None
assert not any(data[0x96e14:base+len(cave)]), "RX padding is occupied"
data[base:base+len(cave)] = cave
struct.pack_into("<QQ", data, rx+32, base+len(cave), base+len(cave))
# Allocate a private tail; neither ioctl length nor callback offsets change.
assert data[0x394b0:0x394b4] == bytes.fromhex("e1031832")
data[0x394b0:0x394b4] = struct.pack("<I", 0x52800001 | (0x120 << 5))
for pc, off in hooks:
    data[pc:pc+4] = branch(pc, base+off)
blob.write_bytes(data)
print("Patched", hashlib.sha256(data).hexdigest())
