# Qin camera blob compatibility patches

The checked-in blobs include these patches. Do not overwrite them with
an unpatched extraction. The scripts are idempotent.

## P Fence lifetime

patch_camera_fence.py changes the stock camera's two undefined Fence
constructor/wait imports in both ELF architectures to FencP aliases.
Pair them with the device platform patch
patches/frameworks_native/legacy_camera_fence_abi.patch. The P blob inlines
close(fd) in its destructor; Android 12's unique_fd constructor tags
ownership, causing fdsan aborts after the first preview frames. The scoped
bridge retains the old 8-byte object layout. It keeps fdsan and modern
platform Fence ownership checks.

## Arm64 software scaler

CPP supports at most 768 output pixels per row. The 800x600 redisplay used
after a full-resolution capture needs the software fallback. The stock
arm64 cmr_scale_start narrows img_frm.addr_vir pointers into the legacy
32-bit CPP ioctl structure, then the software path dereferences them.

camera_scale64.S retains both complete Y/UV pointer pairs in a private
32-byte allocation tail after the ioctl config and callback fields.
The allocation grows from 256 to 288 bytes. The fallback restores the
64-bit pointers into its frame structures and returns the output fd in
its callback as the hardware path does. The kernel ioctl layout and
hardware limits are unchanged; the 32-bit blob is unaffected.

patch_camera_scale64.py uses 60 bytes of verified empty padding at
0x97000 and extends the existing RX PT_LOAD to cover it. It changes four
branches and one allocation instruction, without moving sections,
symbol addresses or data. It accepts the exact original or patched ELF.

To assemble from the LOS root, use AOSP GCC 4.9's aarch64-linux-android-as
on camera_scale64.S, then aarch64-linux-android-ld with -Ttext=0x97000,
-e qin_scale_save_input, --defsym=save_input_return=0x395ac,
--defsym=save_output_return=0x39648, --defsym=restore_return=0x39f98 and
--defsym=fd_return=0x3a05c. Use objcopy -O binary --only-section=.text
to extract the 60-byte binary and pass it to patch_camera_scale64.py.

Verified with the v136 kernel and userdebug/permissive: continuous
preview, user-confirmed moving scene, software scaling return 0, and a
decoded 3120x4160 JPEG published to MediaStore. Enforcing and video
recording need separate validation.
