#!/usr/bin/env bash
set -euo pipefail

mkdir -p third_party/frameworks third_party/MoltenVK /tmp/mvk_extract

MVK_VERSION="v1.4.2"
TAR_URL="https://github.com/KhronosGroup/MoltenVK/releases/download/${MVK_VERSION}/MoltenVK-ios.tar"

echo "==> Downloading MoltenVK ${MVK_VERSION} for iOS (~34 MB)..."
curl -sSL -o /tmp/MoltenVK-ios.tar "${TAR_URL}"

echo "==> Extracting MoltenVK..."
tar -xf /tmp/MoltenVK-ios.tar -C /tmp/mvk_extract/

if [ -d "/tmp/mvk_extract/MoltenVK/MoltenVK/static/MoltenVK.xcframework" ]; then
    cp -r /tmp/mvk_extract/MoltenVK/MoltenVK/static/MoltenVK.xcframework third_party/frameworks/
    cp -r /tmp/mvk_extract/MoltenVK/MoltenVK/static/MoltenVK.xcframework third_party/MoltenVK/
fi

if [ -d "/tmp/mvk_extract/MoltenVK/MoltenVK/include" ]; then
    cp -r /tmp/mvk_extract/MoltenVK/MoltenVK/include third_party/MoltenVK/
fi

rm -rf /tmp/mvk_extract /tmp/MoltenVK-ios.tar
echo "==> MoltenVK iOS framework & headers ready in third_party/MoltenVK/."
