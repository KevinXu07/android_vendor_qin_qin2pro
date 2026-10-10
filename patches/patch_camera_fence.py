#!/usr/bin/env python3
"""Redirect the stock P camera imports to the scoped libui Fence bridge.

Pair these blobs with legacy_camera_fence_abi.patch from the device tree.
Only two undefined dynamic-symbol names change, at the same length.
Modern Fence callers and fdsan remain unchanged.
"""
from pathlib import Path
import hashlib
root = Path(__file__).resolve().parent.parent
for arch in ("lib64", "lib"):
    blob = root / f"proprietary/vendor/{arch}/hw/camera.sp9863a.so"
    data = blob.read_bytes()
    for old in (b"_ZN7android5FenceC1Ei\0", b"_ZN7android5Fence4waitEi\0"):
        new = old.replace(b"5Fence", b"5FencP")
        assert len(old) == len(new)
        if data.count(old):
            assert data.count(old) == 1
            data = data.replace(old, new)
        else:
            assert data.count(new) == 1
    if data != blob.read_bytes(): blob.write_bytes(data)
    print(arch, hashlib.sha256(data).hexdigest())
