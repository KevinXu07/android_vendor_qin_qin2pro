# Vendor blobs for Qin 2 Pro (qin2pro) — WIP

Proprietary binaries extracted from the stock Android 9 firmware
(`s9863a1h10_Natv-user-gms_SHARKL3_9863A_9.pac`) for the DuoQin
Qin 2 Pro (Unisoc SC9863A / SharkL3), used by the unofficial
LineageOS 19.1 port.

Notable contents:
- PowerVR Rogue userspace (EGL/GLES `lib*_POWERVR_ROGUE`, IMG gralloc,
  `pvrsrvkm.ko` kernel module built from DDK 1.10.5187610 for
  `sharkl3_linux`)
- SPRD HWComposer (legacy ADF — unused; display runs drm_hwcomposer),
  widevine, SPRD HAL services (connmgr/gnss/power/thermal/etc.)

Pairs with:
- `android_device_qin_qin2pro`
- `android_kernel_qin_sprd` (branch `qin2pro-bringup`)
