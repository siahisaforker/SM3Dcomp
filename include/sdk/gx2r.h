#pragma once

#include "types.h"

enum GX2RResourceFlags {
    GX2R_RESOURCE_BIND_NONE = 0,
    GX2R_RESOURCE_BIND_TEXTURE = 1,
    GX2R_RESOURCE_BIND_COLOR_BUFFER = 2,
    GX2R_RESOURCE_BIND_DEPTH_BUFFER = 4,
    GX2R_RESOURCE_BIND_VERTEX_BUFFER = 16,
    GX2R_RESOURCE_BIND_INDEX_BUFFER = 32,
    GX2R_RESOURCE_BIND_UNIFORM_BLOCK = 64,
    GX2R_RESOURCE_USAGE_CPU_READ = 1 << 11,
    GX2R_RESOURCE_USAGE_CPU_WRITE = 1 << 12,
    GX2R_RESOURCE_USAGE_GPU_READ = 1 << 13,
    GX2R_RESOURCE_USAGE_GPU_WRITE = 1 << 14
};

struct GX2RBuffer {
    GX2RResourceFlags flags;
    sm3d::u32 elemSize;
    sm3d::u32 elemCount;
    void* buffer;
};

extern "C"
{
    sm3d::s32 GX2RCreateBuffer(GX2RBuffer* buffer);
    void GX2RDestroyBufferEx(GX2RBuffer* buffer, GX2RResourceFlags flags);
    void* GX2RLockBufferEx(GX2RBuffer* buffer, GX2RResourceFlags flags);
    void GX2RUnlockBufferEx(GX2RBuffer* buffer, GX2RResourceFlags flags);
}
