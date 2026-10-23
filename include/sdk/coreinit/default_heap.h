#pragma once

#include "types.h"

typedef void* (*MEMAllocFromDefaultHeapFn)(sm3d::u32 size);
typedef void* (*MEMAllocFromDefaultHeapExFn)(sm3d::u32 size, sm3d::s32 alignment);
typedef void (*MEMFreeToDefaultHeapFn)(void* address);

extern "C"
{
    extern MEMAllocFromDefaultHeapFn MEMAllocFromDefaultHeap;
    extern MEMAllocFromDefaultHeapExFn MEMAllocFromDefaultHeapEx;
    extern MEMFreeToDefaultHeapFn MEMFreeToDefaultHeap;
}
