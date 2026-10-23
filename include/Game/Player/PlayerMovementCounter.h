#pragma once

#include "types.h"

namespace sm3d
{

struct PlayerMovementSource;
struct PlayerMovementCollision;
struct PlayerMovementInput;
struct PlayerMovementProperty;
struct PlayerMovementOwner;

struct PlayerMovementCounter {
    void* vtable;
    u32 frameCount;
    PlayerMovementSource* movement;
    PlayerMovementCollision* collision;
    PlayerMovementInput* input;
    PlayerMovementProperty* property;
    PlayerMovementOwner* player;

    void bindDependencies(PlayerMovementSource* movement, PlayerMovementCollision* collision,
                          PlayerMovementInput* input, PlayerMovementProperty* property,
                          PlayerMovementOwner* player);
    void update();
};

} // namespace sm3d
