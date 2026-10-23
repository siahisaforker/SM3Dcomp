#pragma once

#include "types.h"

struct MEMHeapHeader;
typedef MEMHeapHeader* MEMHeapHandle;

enum MEMBaseHeapType {
    MEM_BASE_HEAP_MEM1 = 0,
    MEM_BASE_HEAP_MEM2 = 1,
    MEM_BASE_HEAP_FG = 8
};

extern "C"
{
    MEMHeapHandle MEMGetBaseHeapHandle(MEMBaseHeapType type);

    MEMHeapHandle MEMCreateExpHeapEx(void* memory, sm3d::u32 size, sm3d::u16 flags);
    void* MEMDestroyExpHeap(MEMHeapHandle heap);
    void* MEMAllocFromExpHeapEx(MEMHeapHandle heap, sm3d::u32 size, int alignment);
    void MEMFreeToExpHeap(MEMHeapHandle heap, void* block);
    sm3d::u32 MEMGetAllocatableSizeForExpHeapEx(MEMHeapHandle heap, int alignment);

    MEMHeapHandle MEMCreateFrmHeapEx(void* memory, sm3d::u32 size, sm3d::u32 flags);
    void* MEMDestroyFrmHeap(MEMHeapHandle heap);
    void* MEMAllocFromFrmHeapEx(MEMHeapHandle heap, sm3d::u32 size, int alignment);
}
