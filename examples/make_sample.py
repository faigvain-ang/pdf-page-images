#!/usr/bin/env python3
"""Build a synthetic three-page PDF using only the Python standard library."""

from hashlib import md5
from pathlib import Path
import struct

_PADDING = bytes.fromhex("28bf4e5e4e758a4164004e56fffa01082e2e00b6d0683e802f0ca9fe6453697a")


def _rc4(key: bytes, data: bytes) -> bytes:
    state = list(range(256))
    j = 0
    for i in range(256):
        j = (j + state[i] + key[i % len(key)]) % 256
        state[i], state[j] = state[j], state[i]
    i = j = 0
    result = bytearray()
    for value in data:
        i = (i + 1) % 256
        j = (j + state[i]) % 256
        state[i], state[j] = state[j], state[i]
        result.append(value ^ state[(state[i] + state[j]) % 256])
    return bytes(result)


def build_pdf(*, password: str | None = None) -> bytes:
    """Pages 1/2 are US Letter; page 3 has an intrinsic clockwise 90-degree rotation.

    Optional legacy encryption is only a test fixture, not a security feature.
    """
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [4 0 R 6 0 R 8 0 R] /Count 3 >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    file_id = md5(b"pdf-page-images synthetic sample").digest()
    key = None
    if password is not None:
        user = (password.encode("ascii") + _PADDING)[:32]
        owner_key = md5((b"synthetic-owner" + _PADDING)[:32]).digest()[:5]
        owner = _rc4(owner_key, user)
        key = md5(user + owner + struct.pack("<i", -4) + file_id).digest()[:5]
        user_entry = _rc4(key, _PADDING)
    for number, color in enumerate(("1 0 0", "0 0.6 0", "0 0 1"), 1):
        stream_number = 3 + 2 * number
        rotation = 90 if number == 3 else 0
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Rotate {rotation} "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {stream_number} 0 R >>".encode("ascii")
        )
        stream = (
            f"q {color} rg 72 72 144 144 re f Q\n"
            f"BT /F1 24 Tf 72 700 Td (Synthetic statement - page {number}) Tj ET\n"
            "BT /F1 12 Tf 72 670 Td (Example only - no real personal or financial data.) Tj ET\n"
        ).encode("ascii")
        if key is not None:
            object_key = md5(key + stream_number.to_bytes(3, "little") + b"\x00\x00").digest()[:10]
            stream = _rc4(object_key, stream)
        objects.append(f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"endstream")
    if key is not None:
        objects.append(
            f"<< /Filter /Standard /V 1 /R 2 /Length 40 /O <{owner.hex()}> "
            f"/U <{user_entry.hex()}> /P -4 >>".encode("ascii")
        )
    result = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result.extend(f"{number} 0 obj\n".encode("ascii") + obj + b"\nendobj\n")
    xref = len(result)
    result.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        result.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    encryption = " /Encrypt 10 0 R" if key is not None else ""
    result.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R /ID [<{file_id.hex()}> <{file_id.hex()}>]"
        f"{encryption} >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return bytes(result)


if __name__ == "__main__":
    target = Path(__file__).with_name("statement.pdf")
    target.write_bytes(build_pdf())
    print(target)
