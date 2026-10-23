#pragma once

#include "types.h"

namespace sm3d
{

struct StageArchive {
    static void formatPath(char* destination, const char* stageName, s32 index, const char* suffix);
};

} // namespace sm3d
