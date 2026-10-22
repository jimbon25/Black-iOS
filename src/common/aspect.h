#pragma once
#include <algorithm>
#include <atomic>

#include "app/app.h"

namespace game {

// the output's shape, 4:3 at the narrowest: the frame is shown that wide
inline float Aspect() {
    app::Mode m = app::Output();
    if (m.width && m.height) {
        return std::max(float(m.width) / float(m.height), 4.0f / 3.0f);
    }
    return 16.0f / 9.0f;
}
// the share of the frame's width a 4:3 picture takes
inline float Narrow() { return 4.0f / 3.0f / Aspect(); }
inline bool Wide() { return Aspect() > 1.34f; }

}  // namespace game
