# Quake II RTX Overdrive + OptiScaler FSR 4 Setup Guide

This guide details the complete configuration, binary modifications, and troubleshooting steps used to get **Quake II RTX Overdrive v1.0.4** running with **AMD FidelityFX Super Resolution 4 (FSR 4)** via **OptiScaler v0.9.4** on AMD Radeon GPUs (RDNA 4 / RX 9060 XT and compatible RDNA hardware).

---

## 1. Architecture & Overview

* **Game**: Quake II RTX Overdrive v1.0.4 (`q2rtx.exe`), a Vulkan path-tracing engine fork integrating 2023 Quake II Remaster campaigns and modern DLSS hooks.
* **Target Hardware**: AMD Radeon RX 9060 XT (RDNA 4 architecture).
* **Translation Proxy**: **OptiScaler v0.9.4** loaded as `winmm.dll`. OptiScaler intercepts NVIDIA NGX / DLSS API calls and translates them to FidelityFX / XeSS backends.
* **Upscaling Engine**: **FSR 4.1.1** neural upscaling model loaded via DirectX 12 interop (`amd_fidelityfx_upscaler_dx12.dll`).

```
+-------------------------------------------------------------+
|               Quake II RTX Overdrive (Vulkan)               |
|      (Invokes DLSS NVSDK_NGX_VULKAN_* API functions)         |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|              OptiScaler Proxy (winmm.dll)                   |
|   - Binary patched to prevent swapchain lifetime crash       |
|   - Authenticode bypass via signed nvngx_dlss.dll            |
|   - Translates DLSS inputs -> FSR                            |
+-------------------------------------------------------------+
                              |
              +---------------+---------------+
              |                               |
       [Native Vulkan]                [Vulkan-on-DX12]
    amd_fidelityfx_vk.dll       amd_fidelityfx_upscaler_dx12.dll
    (Caps out at FSR 3.1.4)               (FSR 4.1.1)
                                              |
                                              v
                                      AMD Radeon RDNA 4
                                      (Neural ML Model)
```

## 2. Initial Installation & Deployment

### Step 1: Download Quake II RTX Overdrive
* Download **Quake II RTX Overdrive v1.0.4** from [mstewart248/Q2RTX-MOD Releases](https://github.com/mstewart248/Q2RTX-MOD/releases).
  - Package: `Q2RTX-Overdrive-v1.0.4-win64.zip` (~1.64 GB).
  - Contains: Engine binaries (`q2rtx.exe`), compiled ray-tracing shaders, stock Q2RTX media (`q2rtx_media.pkz`), and authored PBR definitions for the remaster campaigns.

### Step 2: Backup Stock Game Files
Before deploying mod files into your Steam installation:
* Target Directory: `C:\Program Files (x86)\Steam\steamapps\common\Quake II RTX`
* Create a backup directory named `_original_backup/` and copy the stock executables and libraries into it.

### Step 3: Deploy Overdrive Binaries
* Extract `Q2RTX-Overdrive-v1.0.4-win64.zip`.
* Copy the contents of the `Q2RTX-Overdrive/` folder directly into `C:\Program Files (x86)\Steam\steamapps\common\Quake II RTX\`, overwriting existing files.

### Step 4: Install & Configure OptiScaler
1. Download **OptiScaler v0.9.4** from [optiscaler/OptiScaler Releases](https://github.com/optiscaler/OptiScaler/releases) (`OptiScaler-v0.9.4-final.zip`).
2. Extract the stock runtime companion libraries directly into `C:\Program Files (x86)\Steam\steamapps\common\Quake II RTX\`:
   - `amd_fidelityfx_dx12.dll`
   - `amd_fidelityfx_upscaler_dx12.dll` (FSR 4.1.1 runtime)
   - `amd_fidelityfx_framegeneration_dx12.dll`
   - `amd_fidelityfx_vk.dll` (FSR 3.1.4 Vulkan runtime)
   - `libxess.dll` & `libxell.dll` (Intel XeSS runtimes)
   - `fakenvapi.dll` & `fakenvapi.ini` (NVAPI translation layer)
3. Copy `OptiScaler.dll` into the game folder and rename it to **`winmm.dll`** (so it loads automatically on game startup via Windows multimedia API import).
4. Apply the binary crash fix to `winmm.dll` by running:
   ```cmd
   python patch_optiscaler.py
   ```
   *(This replaces the premature Vulkan object destruction call at offset `0x19cd9d` with NOPs to prevent crashes on video restart).*
5. Deploy an Authenticode-signed **`nvngx_dlss.dll`** (e.g. from *Wolfenstein: Youngblood* or other games) into the root directory to satisfy Quake II RTX's digital signature verification.
6. The customized **`OptiScaler.ini`** provided in this repository is already pre-configured for FSR 4 DX12 interop and the <kbd>Home</kbd> overlay key.

---

## 3. Asset Setup: Merging Game Files

Quake II RTX Overdrive ships the modified engine, shaders, and PBR override materials, but **does not redistribute copyrighted id Software / Nightdive game data**. The assets must be supplied from your existing Steam installations:

### Source Locations (Steam Default)
* **Quake II (2023 Remaster + Classic)**: `C:\Program Files (x86)\Steam\steamapps\common\Quake 2`
* **Quake II RTX**: `C:\Program Files (x86)\Steam\steamapps\common\Quake II RTX`

### Step-by-Step Asset Copying:

1. **Original Campaign (Base Game)**:
   * Copy `Quake 2\baseq2\pak0.pak` (plus `pak1.pak` / `pak2.pak` if present) into `Quake II RTX\baseq2\`.

2. **Official Expansion Packs**:
   * Copy `Quake 2\xatrix\pak0.pak` into `Quake II RTX\xatrix\pak0.pak` (*The Reckoning*).
   * Copy `Quake 2\rogue\pak0.pak` into `Quake II RTX\rogue\pak0.pak` (*Ground Zero*).

3. **2023 Remaster Campaign (`rerelease/`)**:
   * Copy `Quake 2\rerelease\Q2Game.kpf` into `Quake II RTX\rerelease\Q2Game.kpf`.
   * Copy `Quake 2\rerelease\baseq2\pak0.pak` into `Quake II RTX\rerelease\baseq2\pak0.pak`.
   * Copy folder `Quake 2\rerelease\baseq2\music\` into `Quake II RTX\rerelease\baseq2\music\` (optional soundtrack).
   * Copy folder `Quake 2\rerelease\baseq2\video\` into `Quake II RTX\rerelease\baseq2\video\` (optional cinematics).

> [!IMPORTANT]
> **Merge, do NOT overwrite or delete existing folders!** Quake II RTX Overdrive includes custom path-traced lighting and texture overrides in `rerelease/overrides`, `rerelease/materials`, `rerelease/textures`, and `rerelease/models`. These files must remain intact for path tracing to illuminate the remaster campaign properly. Non-relevant files from the remaster (e.g., `quake2ex_steam.exe`, `PartyWin.dll`, `SDL2.dll`) should be omitted.

---

## 4. Problems Diagnosed & Fixes Applied

### Problem 1: Crash on Video Restart / DLSS Mode Toggle (`vid_restart`)
* **Symptom**: Toggling DLSS on/off or changing resolution in-game caused an immediate access violation exception (`0xc0000005`) during `vid_restart`.
* **Root Cause**: In OptiScaler's Vulkan hook `hkvkCreateWin32SurfaceKHR` (at file offset `0x19cd9d` in `winmm.dll`), OptiScaler prematurely executed `call MenuOverlayVk::DestroyVulkanObjects`. During video restarts, Quake II RTX creates the new surface *before* destroying the old swapchain. Destroying the overlay's Vulkan objects mid-lifecycle resulted in use-after-free and NULL pointer dereferences in subsequent `vkQueuePresentKHR` calls.
* **Fix**: Binary-patched `winmm.dll` at file offset `0x19cd9d`:
  - Replaced `E8 5E 34 02 00` (`call MenuOverlayVk::DestroyVulkanObjects`) with 5 NOP instructions (`90 90 90 90 90`).
  - Swapchain resource recreation is cleanly handled by `MenuOverlayVk::CreateSwapchain` when the new swapchain is established.
  - A standalone Python script ([`patch_optiscaler.py`](file:///C:/Program%20Files%20%28x86%29/Steam/steamapps/common/Quake%20II%20RTX/patch_optiscaler.py)) is included in the repository to automate or re-verify this patch.
  - Original unpatched DLL preserved as [`winmm.dll.orig`](file:///C:/Program%20Files%20%28x86%29/Steam/steamapps/common/Quake%20II%20RTX/winmm.dll.orig).

### Problem 2: DLL Clashes & Authenticode Signature Verification
* **Symptom**: Having both `_nvngx.dll` and `winmm.dll` in the game folder caused double-hook collisions and crashes. Furthermore, Quake II RTX verifies NVIDIA digital signatures (Authenticode) on NGX libraries.
* **Fix**:
  - Removed duplicate `_nvngx.dll` and `nvngx.dll` proxies.
  - Standardized on `winmm.dll` as the sole proxy mechanism.
  - Placed an Authenticode-signed `nvngx_dlss.dll` (from *Wolfenstein: Youngblood*) alongside `fakenvapi.dll` to satisfy Quake II RTX's signature verification.

### Problem 3: FSR 4 Not Appearing in OptiScaler Overlay
* **Symptom**: The OptiScaler in-game overlay only showed options up to FSR 3.1; FSR 4 was nowhere to be found.
* **Root Cause**: AMD **never released a native Vulkan SDK for FSR 4**. AMD's FSR 4 model is exclusively implemented on DirectX 12 / DirectML (`amd_fidelityfx_upscaler_dx12.dll`). OptiScaler's native Vulkan backend (`amd_fidelityfx_vk.dll`) only supports FSR 2.3.3 and FSR 3.1.4.
* **Fix**:
  - Configured OptiScaler to use its Vulkan-on-DirectX 12 translation interop backend:
    ```ini
    [Upscalers]
    VulkanUpscaler=fsr31_12

    [FSR]
    UpscalerIndex=0        ; 0 = FSR 4.1.1, 1 = FSR 3.1.5, 2 = FSR 2.3.4
    Fsr4Update=true        ; Enables FSR 4 neural path for RDNA 4 GPUs
    ```
  - In the OptiScaler overlay, the primary upscaler is selected as **`FSR 3.X/4 w/Dx12`**. Under **FFX Settings**, the **FFX Upscaler** dropdown will display and run **`FSR 4.1.1`**.

### Problem 4: Overlay Toggle Key Conflict
* **Fix**: Changed the OptiScaler overlay shortcut from <kbd>Insert</kbd> to <kbd>Home</kbd> in `OptiScaler.ini`:
  ```ini
  [Menu]
  ShortcutKey=0x24       ; VK_HOME
  ```

---

## 5. Repository File Structure

Only custom mod files, modified binaries, configuration files, and scripts are tracked in Git (~25MB), omitting multi-gigabyte game assets and standard third-party release packages:

| File | Description |
|---|---|
| `winmm.dll` | Patched OptiScaler v0.9.4 proxy DLL (our modified binary) |
| `winmm.dll.orig` | Original unpatched OptiScaler DLL backup |
| `patch_optiscaler.py` | Python script to inspect / apply the Vulkan crash patch |
| `OptiScaler.ini` | Custom OptiScaler configuration (FSR 4 DX12 interop, Home key) |
| `fakenvapi.ini` | NVAPI spoofing configuration |
| `q2rtx.exe` / `q2rtxded*.exe` | Quake II RTX Overdrive v1.0.4 engine executables |
| `Launch_Quake2_RTX_Overdrive.bat` | One-click launcher for original Quake II campaign |
| `Launch_Quake2_Remaster_RTX.bat` | One-click launcher for 2023 Remaster campaign |
| `baseq2/q2config.cfg` | Player configuration (`seta pt_dlss "2"`, binds) |
| `baseq2/pt_toggles.cfg` | Path-tracing toggle binds |
| `README.md` | Main setup, FSR 4 integration, and troubleshooting guide |
| `README_UPSTREAM.md` | Original upstream Quake II RTX Overdrive documentation |
| `.gitignore` | Whitelist rule set preserving mod files and ignoring assets & stock DLLs |

*(Note: Standard upstream OptiScaler companion libraries like `amd_fidelityfx_*.dll`, `libxess.dll`, `fakenvapi.dll`, etc. are ignored by Git and supplied directly via the OptiScaler v0.9.4 release package as documented in Step 4).*

---

## 6. How to Launch & Verify

### Launching the Game
- **Original Campaign**: Double-click `Launch_Quake2_RTX_Overdrive.bat` (or run `q2rtx.exe`).
- **2023 Remaster Campaign**: Double-click `Launch_Quake2_Remaster_RTX.bat` (or run `q2rtx.exe +set game rerelease`).

### Verifying FSR 4 In-Game
1. Start or load any single-player level (the DLSS pipeline is only active during 3D gameplay, not in the main menu).
2. Ensure DLSS is enabled in the game options (**Video** → **Advanced** → **DLSS Super Resolution**: Quality / Balanced / Performance, or in console: `pt_dlss 2`).
3. Press <kbd>Home</kbd> to toggle the OptiScaler overlay:
   - Verify the main **Upscaler** dropdown shows **`FSR 3.X/4 w/Dx12`**.
   - Under **FFX Settings**, verify **FFX Upscaler** is set to **`FSR 4.1.1`**.
4. Check the performance HUD overlay: you will see real-time frame timings confirming FSR 4 is upscaling the frame.
