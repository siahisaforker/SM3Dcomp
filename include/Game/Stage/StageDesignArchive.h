#pragma once

#include "types.h"

struct StageDesignArchive {
    void* load(void* archive, s32 designIndex);
};
