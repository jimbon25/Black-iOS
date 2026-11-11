#pragma once

namespace game {

// Update enemy tracking list for ESP/Aimbot (call once per frame)
void UpdateEnemyList();

// Draw ESP lines from player to enemies (call during HUD render pass)
void DrawEspLines();

// Apply aimbot cursor adjustment (call during mouse/touch input processing)
void ApplyAimbot(float& yaw, float& pitch);

}  // namespace game
