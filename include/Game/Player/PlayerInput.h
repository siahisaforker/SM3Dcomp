#pragma once

#include "types.h"

namespace sm3d {

struct PlayerInput {
    u8 unknown00[0x34];
    u32 jumpTriggerFrames;
    u8 unknown38[0x0C];
    u32 swimPaddleTriggerFrames;
    u8 unknown48[0x08];
    u32 rollingTriggerFrames;
    u8 unknown54[0x2C];

    bool isJumpTrigOn() const;
    bool isPrecedingSwimPaddleTrigOn() const;
    bool isRollingTrigOn() const;
};

typedef char player_input_size_check[sizeof(PlayerInput) == 0x80 ? 1 : -1];




}
