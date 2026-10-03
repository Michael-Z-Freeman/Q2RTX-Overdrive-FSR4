"""
patch_optiscaler.py:
Patches OptiScaler v0.9.4 winmm.dll to eliminate the Vulkan device lifetime
crash in hkvkCreateWin32SurfaceKHR during in-game video restarts (vid_restart).
"""
import sys
import os
import shutil

def patch_file(dll_path):
    if not os.path.isabs(dll_path):
        dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), dll_path)

    if not os.path.exists(dll_path):
        print(f"[-] File not found: {dll_path}")
        return False

    bak_path = dll_path + ".orig"
    if not os.path.exists(bak_path):
        shutil.copyfile(dll_path, bak_path)
        print(f"[+] Created original backup: {bak_path}")

    with open(dll_path, "rb") as f:
        data = bytearray(f.read())

    foff = 0x19cd9d
    expected = bytes([0xe8, 0x5e, 0x34, 0x02, 0x00])
    current = data[foff:foff+5]

    if current == expected:
        data[foff:foff+5] = b'\x90\x90\x90\x90\x90'
        with open(dll_path, "wb") as f:
            f.write(data)
        print(f"[+] Successfully patched {dll_path} with 5 NOPs at {hex(foff)}.")
        return True
    elif current == b'\x90\x90\x90\x90\x90':
        print(f"[*] {dll_path} is already patched with NOPs at {hex(foff)}.")
        return True
    else:
        print(f"[-] Unexpected bytes at {hex(foff)}: {current.hex(' ')} (expected: {expected.hex(' ')})")
        return False

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "winmm.dll"
    patch_file(target)
