# Black for iOS & Android
An unofficial native iOS and Android port of the original Xbox version of *Black (2006)*, featuring native ahead-of-time static recompilation, touch controls, gyroscope aiming, controller support, and extended graphics settings. No emulator or JIT compilation is required.

The game's x86 machine code is statically recompiled ahead of time to C++ with [XboxXBE-Recomp](https://github.com/TGP482/XboxXBE-Recomp), then natively compiled for ARM64. Rendering is powered by Vulkan (translated to Metal via MoltenVK on iOS), while windowing, audio, and input are handled by SDL3.

> [!NOTE]
> This project does not distribute any copyrighted game assets. You must supply your own copy of the original Xbox game files.

---

## iOS Installation Guide

### 1. Download & Sideload IPA
1. Download the latest `Black-*.ipa` from [GitHub Releases](https://github.com/jimbon25/Black-iOS/releases).
2. Sideload the IPA onto your iOS device using your preferred tool:
   - **KSign** / **ESign** (on-device signing)
   - **TrollStore** (iOS 14.0 – 17.0)
   - **AltStore** / **SideStore** / **Sideloadly**

### 2. Game Data Setup
The recompiler specifically targets the **original Microsoft Xbox** release of *Black* (do **not** use PlayStation 2 ISOs).

1. Download the HDD-ready Xbox game data:
   - Direct download: [Archive.org HDDReady Xbox Black.zip (1.25 GB)](https://dn711309.ca.archive.org/0/items/HDDReadyXboxGames/Black.zip)
   - Repository: [Archive.org HDDReadyXboxGames Collection](https://archive.org/details/HDDReadyXboxGames)
2. Extract the archive on your device or computer. You will have a folder containing `default.xbe` along with game subfolders (`assets/`, `levels/`, etc.).
3. Open the iOS **Files** app:
   - Navigate to **On My iPhone** → **BLACK** (this folder is automatically exposed via iTunes Document Sharing).
   - Place the extracted `Black` folder (or copy `default.xbe` and its folders) directly into this directory:
     ```
     On My iPhone/
     └── BLACK/
         └── Black/
             ├── default.xbe
             ├── assets/
             ├── levels/
             └── sound/
     ```
4. Open the game. It will automatically detect `default.xbe`, initialize the shaders, and launch.

---

## Features

### Graphics & Display
- **Full-Screen Native Resolution**: Native edge-to-edge Retina display scaling.
- **Render Resolution**: Configurable from 20% to 200% scaling for crisp high-resolution visuals.
- **Field of View (FOV)**: Adjustable horizontal FOV (45° to 140°) and separate viewmodel weapon FOV.
- **FMV Scaling**: Option to scale 4:3 video cinematics to *Fill* or preserve original aspect ratio.
- **Post-Processing Filters**: Sharpen, vibrant color profiles, and vintage CRT scanline filters.
- **Unlocked Performance**: Configurable frame rate limits or unlimited FPS at display refresh rate (60 Hz / 120 Hz ProMotion).

### Controls & Input
- **On-Screen Touch Controls**: Virtual analog stick, dynamic look drag, dedicated buttons for fire, aim, melee, reload, grenades, crouch, weapon swap, and suppressor.
- **Customizable Layouts**: Built-in presets (*Default*, *3-Finger*, *4-Finger*) with repositioning and opacity adjustments.
- **Motion & Gyro Aiming**: Gyroscope aiming with customizable sensitivity.
- **Game Controller Support**: Full support for PlayStation (DualSense / DualShock), Xbox Wireless, and MFi controllers via SDL3 with vibration / haptic rumble.

### Built-in Cheats
Built directly into the in-game menu under **OPTIONS → CHEATS**:
- **Weapons**: Infinite Ammo, Infinite Grenades, Rapid Fire (2x – 4x), No Recoil.
- **Player**: God Mode, One-Hit Kill.
- **Progression**: Unlock All Missions, Unlock Black Ops mode.
- **Game Speed**: Adjustable gameplay speed from 25% to 200%.

---

## Building from Source

### iOS (macOS / GitHub Actions)
1. Ensure Xcode 16+ is installed (`macos-15` runner).
2. Run `tools/fetch_deps.sh` to download MoltenVK.
3. Configure and build via CMake:
   ```bash
   cmake -B build-ios -G Xcode \
     -DCMAKE_SYSTEM_NAME=iOS \
     -DCMAKE_OSX_DEPLOYMENT_TARGET=15.0 \
     -DCMAKE_OSX_ARCHITECTURES=arm64
   cmake --build build-ios --config Release --target Black
   ```

---

## Credits & Acknowledgments

- **[TGP482](https://github.com/TGP482/XboxXBE-Recomp)** — Developer of *XboxXBE-Recomp*, the ahead-of-time static recompiler and portable Xbox kernel runtime (Direct3D 8, XAudio/DSound, XAPI).
- **[RanggaCasper](https://github.com/RanggaCasper/Black-Android)** — Developer of the Android native port, custom touch layout system, gyroscope integration, and UI overlays.
- **[j1mb (Dayumm)](https://github.com/jimbon25/Black-iOS)** — iOS port development: Darwin Mach VM memory subsystem, Apple Silicon 16KB hardware page alignment, MoltenVK Metal backend integration, multi-thread GCD surface dispatch, edge-to-edge UI display, and packaging.
- **[The Khronos Group](https://github.com/KhronosGroup/MoltenVK)** — MoltenVK Vulkan-to-Metal portability implementation.
- **[libsdl-org (SDL3)](https://github.com/libsdl-org/SDL)** — Cross-platform windowing, UIKit backend, audio, and gamepad input.
- **[Dear ImGui](https://github.com/ocornut/imgui)**, **[glslang](https://github.com/KhronosGroup/glslang)**, and **[toml++](https://github.com/marzer/tomlplusplus)**.
- **Criterion Games & Electronic Arts** — Original creators of *BLACK (2006)*.

---

*BLACK is a registered trademark of Electronic Arts Inc. This project is a non-commercial, fan-made educational recompilation and is not affiliated with or endorsed by Electronic Arts or Microsoft.*
