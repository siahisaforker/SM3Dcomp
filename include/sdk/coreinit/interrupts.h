#pragma once

#include "types.h"

extern "C"
{
    sm3d::s32 OSDisableInterrupts();
    sm3d::s32 OSRestoreInterrupts(sm3d::s32 enabled);
}
