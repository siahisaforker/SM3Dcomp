#pragma once

#include "types.h"

struct StageArchive {
    static void formatPath(char* destination, const char* stageName, s32 index, const char* suffix);
};
