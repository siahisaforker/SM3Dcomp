#pragma once

#include "types.h"

struct PlayerParam {
    bool readInteger(s32* value, const char* key);
    bool readFloat(f32* value, const char* key);
};
