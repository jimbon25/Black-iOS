# Black (original Xbox), statically recompiled, as an Android library: libmain.so, loaded by SDL's activity.
# The x86 code is recompiled on the PC first (build.bat): this build takes generated/game as it is, with the SDK's
# portable runtime, the game's sources in src and the Android host in native.

cmake_minimum_required(VERSION 3.22)
project(black LANGUAGES C CXX)
if(APPLE)
    enable_language(OBJC OBJCXX)
endif()

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(REPO ${CMAKE_CURRENT_SOURCE_DIR})
set(NATIVE ${CMAKE_CURRENT_SOURCE_DIR}/native)
set(GAME ${CMAKE_CURRENT_SOURCE_DIR}/src)  # the game's hooks, sound, Direct3D 8 and settings

# the SDK: sdk/ in the repo, a checkout beside it, else downloaded
include(FetchContent)
if(EXISTS ${REPO}/sdk/cmake/XbeRecomp.cmake)
    set(SDK ${REPO}/sdk)
elseif(EXISTS ${REPO}/../XboxXBE-Recomp/cmake/XbeRecomp.cmake)
    get_filename_component(SDK ${REPO}/../XboxXBE-Recomp ABSOLUTE)
else()
    FetchContent_Declare(xbe_sdk GIT_REPOSITORY https://github.com/TGP482/XboxXBE-Recomp.git GIT_TAG main)
    FetchContent_MakeAvailable(xbe_sdk)
    set(SDK ${xbe_sdk_SOURCE_DIR})
endif()

# the recompiled code and the xbe it came from
set(XBE_GENERATED ${REPO}/generated/game CACHE PATH "the recompiled code of default.xbe")
set(XBE_IMAGE ${REPO}/assets/default.xbe CACHE FILEPATH "the xbe it was recompiled from")
set(GEN ${XBE_GENERATED})
set(XBE ${XBE_IMAGE})
if(NOT EXISTS ${GEN}/x86_func_mapping.cpp OR NOT EXISTS ${XBE})
    message(FATAL_ERROR "No recompiled code: put the game in assets/ or iso/ and run build.bat, it writes generated/game")
endif()
file(STRINGS ${REPO}/config/game.toml GAME_PARTITIONS REGEX "^partitions *=")
string(REGEX MATCH "[0-9]+" GAME_PARTITIONS "${GAME_PARTITIONS}")
math(EXPR last "${GAME_PARTITIONS} - 1")
set(GEN_SOURCES ${GEN}/x86_func_mapping.cpp)
foreach(i RANGE ${last})
    list(APPEND GEN_SOURCES ${GEN}/x86_recomp.${i}.cpp)
endforeach()
file(SHA1 ${XBE} xbe_sha1)
file(CONFIGURE OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/image_sha1.cpp CONTENT "extern const char kImageSha1[] = \"${xbe_sha1}\";\n")
# the build's version for the log: the commit when the project is in git, else unknown
set(BUILD_COMMIT "unknown")
find_package(Git QUIET)
if(GIT_EXECUTABLE)
    execute_process(COMMAND ${GIT_EXECUTABLE} rev-parse --short HEAD WORKING_DIRECTORY ${REPO}
                    OUTPUT_VARIABLE head OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET RESULT_VARIABLE failed)
    if(NOT failed AND head)
        set(BUILD_COMMIT ${head})
    endif()
endif()
file(CONFIGURE OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/build_info.h CONTENT "#define BLACK_COMMIT \"${BUILD_COMMIT}\"\n")

# dependencies: SDL3 from the checkout Gradle makes (its Java side goes into the APK), the rest fetched
# dependencies: SDL3
set(SDL_DIR ${CMAKE_CURRENT_SOURCE_DIR}/third_party/SDL)
if(NOT EXISTS ${SDL_DIR}/CMakeLists.txt)
    if(IOS)
        set(SDL_SHARED OFF CACHE BOOL "" FORCE)
        set(SDL_STATIC ON CACHE BOOL "" FORCE)
    else()
        set(SDL_SHARED ON CACHE BOOL "" FORCE)
        set(SDL_STATIC OFF CACHE BOOL "" FORCE)
    endif()
    set(SDL_TEST_LIBRARY OFF CACHE BOOL "" FORCE)
    set(SDL_RENDER OFF CACHE BOOL "" FORCE)
    set(SDL_GPU OFF CACHE BOOL "" FORCE)
    set(SDL_CAMERA OFF CACHE BOOL "" FORCE)
    FetchContent_Declare(SDL3 GIT_REPOSITORY https://github.com/libsdl-org/SDL.git GIT_TAG release-3.2.0 GIT_SHALLOW TRUE)
    FetchContent_MakeAvailable(SDL3)
else()
    set(SDL_SHARED ON CACHE BOOL "" FORCE)
    set(SDL_STATIC OFF CACHE BOOL "" FORCE)
    set(SDL_TEST_LIBRARY OFF CACHE BOOL "" FORCE)
    set(SDL_RENDER OFF CACHE BOOL "" FORCE)
    set(SDL_GPU OFF CACHE BOOL "" FORCE)
    set(SDL_CAMERA OFF CACHE BOOL "" FORCE)
    add_subdirectory(${SDL_DIR} ${CMAKE_CURRENT_BINARY_DIR}/SDL EXCLUDE_FROM_ALL)
endif()

set(ENABLE_OPT OFF CACHE BOOL "" FORCE)
set(ENABLE_HLSL ON CACHE BOOL "" FORCE)
set(ENABLE_GLSLANG_BINARIES OFF CACHE BOOL "" FORCE)
set(ENABLE_SPVREMAPPER OFF CACHE BOOL "" FORCE)
set(GLSLANG_TESTS OFF CACHE BOOL "" FORCE)
set(GLSLANG_ENABLE_INSTALL OFF CACHE BOOL "" FORCE)
set(BUILD_EXTERNAL OFF CACHE BOOL "" FORCE)
FetchContent_Declare(glslang GIT_REPOSITORY https://github.com/KhronosGroup/glslang.git GIT_TAG 16.0.0 GIT_SHALLOW TRUE)
FetchContent_Declare(tomlplusplus GIT_REPOSITORY https://github.com/marzer/tomlplusplus.git GIT_TAG v3.4.0 GIT_SHALLOW TRUE)
FetchContent_Declare(imgui GIT_REPOSITORY https://github.com/ocornut/imgui.git GIT_TAG v1.91.0 GIT_SHALLOW TRUE)
FetchContent_MakeAvailable(glslang tomlplusplus imgui)

# the SDK's runtime but its Windows parts, and those the game replaces (src/sound, src/d3d)
file(GLOB RUNTIME_SOURCES ${SDK}/runtime/*/*.cpp)
list(FILTER RUNTIME_SOURCES EXCLUDE REGEX
     "/runtime/app/|/core/input\\.cpp$|/gpu/(d3d12|render_thread)\\.cpp$|/audio/xaudio2\\.cpp$|/xdk/(dsound|d3d8)\\.cpp$|/kernel/memory\\.cpp$")
# the game's sources: its hooks, sound, Direct3D 8 and settings
file(GLOB GAME_HOST_SOURCES CONFIGURE_DEPENDS ${GAME}/*/*.cpp)
file(GLOB ANDROID_SOURCES CONFIGURE_DEPENDS ${NATIVE}/*.cpp)
set(IMGUI_SOURCES ${imgui_SOURCE_DIR}/imgui.cpp ${imgui_SOURCE_DIR}/imgui_draw.cpp ${imgui_SOURCE_DIR}/imgui_tables.cpp
    ${imgui_SOURCE_DIR}/imgui_widgets.cpp ${imgui_SOURCE_DIR}/backends/imgui_impl_vulkan.cpp)

if(IOS)
    add_executable(Black MACOSX_BUNDLE
                   ${RUNTIME_SOURCES} ${GAME_HOST_SOURCES} ${ANDROID_SOURCES} ${GEN_SOURCES} ${IMGUI_SOURCES}
                   ${CMAKE_CURRENT_BINARY_DIR}/image_sha1.cpp)
    set_target_properties(Black PROPERTIES
        MACOSX_BUNDLE TRUE
        MACOSX_BUNDLE_INFO_PLIST ${REPO}/native/ios/Info.plist
        MACOSX_BUNDLE_BUNDLE_NAME "BLACK"
        MACOSX_BUNDLE_GUI_IDENTIFIER "com.j1mb.black"
        MACOSX_BUNDLE_SHORT_VERSION_STRING "1.5.0"
        MACOSX_BUNDLE_BUNDLE_VERSION "1"
        XCODE_ATTRIBUTE_TARGETED_DEVICE_FAMILY "1,2"
        XCODE_ATTRIBUTE_ENABLE_BITCODE "NO"
    )
    set(TARGET_NAME Black)
else()
    add_library(main SHARED ${RUNTIME_SOURCES} ${GAME_HOST_SOURCES} ${ANDROID_SOURCES} ${GEN_SOURCES} ${IMGUI_SOURCES}
                ${CMAKE_CURRENT_BINARY_DIR}/image_sha1.cpp)
    set(TARGET_NAME main)
endif()

# compat/ for the SDK's x86 header, the SDK harness's for the Winsock and DXGI names its portable runtime uses
target_include_directories(${TARGET_NAME} PRIVATE ${NATIVE}/compat ${SDK}/harness/compat ${NATIVE} ${GAME} ${SDK}/runtime ${GEN}
                           ${CMAKE_CURRENT_BINARY_DIR} ${glslang_SOURCE_DIR})
target_include_directories(${TARGET_NAME} SYSTEM PRIVATE ${imgui_SOURCE_DIR})
# x86 chars are signed, as the game's code and the runtime were written for
target_compile_options(${TARGET_NAME} PRIVATE -fno-strict-aliasing -fsigned-char)
set(HOST_SOURCES ${RUNTIME_SOURCES} ${GAME_HOST_SOURCES} ${ANDROID_SOURCES})
set_source_files_properties(${HOST_SOURCES} PROPERTIES COMPILE_OPTIONS "-include;${NATIVE}/compat/crt.h")
set_source_files_properties(${GEN_SOURCES} PROPERTIES
    COMPILE_OPTIONS "-O2;-w;-fno-strict-aliasing;-fsigned-char")
set_source_files_properties(${NATIVE}/vk_shader.cpp PROPERTIES COMPILE_DEFINITIONS ENABLE_HLSL)
set_source_files_properties(${NATIVE}/game_files.cpp PROPERTIES
    COMPILE_DEFINITIONS "EUROPE_PATCH=\"${GAME}/common/europe.patch\""
    OBJECT_DEPENDS ${GAME}/common/europe.patch)

if(IOS)
    target_include_directories(Black PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/third_party/MoltenVK/include
        ${CMAKE_CURRENT_SOURCE_DIR}/third_party/frameworks/MoltenVK.xcframework/ios-arm64/Headers
    )
    set(MOLTENVK_LIB ${CMAKE_CURRENT_SOURCE_DIR}/third_party/frameworks/MoltenVK.xcframework/ios-arm64/libMoltenVK.a)
    if(NOT EXISTS ${MOLTENVK_LIB})
        message(FATAL_ERROR "Missing MoltenVK static library: ${MOLTENVK_LIB}")
    endif()
    target_link_libraries(Black PRIVATE ${MOLTENVK_LIB})
    target_link_libraries(Black PRIVATE
        $<IF:$<TARGET_EXISTS:SDL3::SDL3-static>,SDL3::SDL3-static,SDL3::SDL3>
        tomlplusplus::tomlplusplus
        glslang glslang-default-resource-limits
        "-framework Metal"
        "-framework MetalKit"
        "-framework IOSurface"
        "-framework UIKit"
        "-framework Foundation"
        "-framework QuartzCore"
        "-framework CoreGraphics"
        "-framework CoreMotion"
        "-framework GameController"
        "-framework AudioToolbox"
        "-framework AVFoundation"
    )
    target_link_options(Black PRIVATE -Wl,-dead_strip)
else()
    target_link_libraries(main PRIVATE SDL3::SDL3 tomlplusplus::tomlplusplus glslang glslang-default-resource-limits
                          vulkan android log)
    target_link_options(main PRIVATE -Wl,-z,max-page-size=16384)
endif()
