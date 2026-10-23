#pragma once

#include "types.h"

struct Vec3f {
    f32 x;
    f32 y;
    f32 z;
};

struct PlayerMovementSource;
struct PlayerMovementState;

struct PlayerMovementCollision {
    u32 isAllowed();
};

struct PlayerMovementInput {
    Vec3f* getMovementVector();
    u32 checkCondition();
};

struct PlayerMovementProperty {
    const Vec3f& direction() const;
    const Vec3f& normal() const;
};

struct PlayerMovementOwner {
    f32 getThreshold();
    u32 getMaximumFrames();
};
