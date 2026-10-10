// SPDX-License-Identifier: Apache-2.0
// libcamoem.so (arm64) preserves complete img_frm virtual addresses in a
// private tail after the 240-byte legacy CPP ioctl config and callbacks.
// Keep the 32-bit kernel ABI and the scaler's 768-pixel limit unchanged.
.text
.global qin_scale_save_input, qin_scale_save_output, qin_scale_restore, qin_scale_fd
.extern save_input_return, save_output_return, restore_return, fd_return
qin_scale_save_input:
    str q0, [x21, #0x100]
    xtn v0.2s, v0.2d
    b save_input_return
qin_scale_save_output:
    str q0, [x21, #0x110]
    xtn v0.2s, v0.2d
    b save_output_return
qin_scale_restore:
    ldr q2, [x20, #0x110]
    stur q2, [x21, #0xa0]
    ldr q2, [x20, #0x100]
    stur q2, [x29, #-0x88]
    b restore_return
qin_scale_fd:
    str x8, [sp, #0xf0]
    ldr w8, [x20, #0x68]
    str w8, [sp, #0x110]
    b fd_return
