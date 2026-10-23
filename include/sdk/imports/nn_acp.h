#pragma once

#include "sdk/imports/types.h"

extern "C"
{
    sm3d::s32 ACPMiiWrap(void* output, sm3d::u32 outputSize, const void* input,
                         sm3d::u32 inputSize);
    sm3d::s32 ACPMiiUnwrap(void* output, sm3d::u32 outputSize, const void* input,
                           sm3d::u32 inputSize);
}
