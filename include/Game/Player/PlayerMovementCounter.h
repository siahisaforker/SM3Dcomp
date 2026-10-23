#pragma once

#include "types.h"

namespace sm3d {

struct PlayerMovementCounter {
    u32 vtable;
    u32 frameCount;
    void* volatile movement;
    void* volatile collision;
    void* volatile input;
    void* volatile property;
    void* volatile player;

    void bindDependencies(void* movement, void* collision, void* input, void* property, void* player);
};

typedef char player_movement_counter_size_check[sizeof(PlayerMovementCounter) == 0x1C ? 1 : -1];

}
