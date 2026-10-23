#pragma once

#include "types.h"
#include "sdk/gx2/types.h"
#include "sdk/gx2/display.h"
#include "sdk/gx2/shaders.h"
#include "sdk/gx2/texture.h"
#include "sdk/gx2/sampler.h"

enum GX2PrimitiveMode {
    GX2_PRIMITIVE_MODE_POINTS = 1,
    GX2_PRIMITIVE_MODE_LINES = 2,
    GX2_PRIMITIVE_MODE_LINE_STRIP = 3,
    GX2_PRIMITIVE_MODE_TRIANGLES = 4,
    GX2_PRIMITIVE_MODE_TRIANGLE_FAN = 5,
    GX2_PRIMITIVE_MODE_TRIANGLE_STRIP = 6,
    GX2_PRIMITIVE_MODE_RECTS = 17,
    GX2_PRIMITIVE_MODE_QUADS = 19
};

enum GX2IndexType {
    GX2_INDEX_TYPE_U16_LE = 0,
    GX2_INDEX_TYPE_U32_LE = 1,
    GX2_INDEX_TYPE_U16 = 4,
    GX2_INDEX_TYPE_U32 = 9
};

extern "C"
{
    void GX2Init(sm3d::u32* attributes);
    void GX2Shutdown();
    void GX2Flush();
    sm3d::s32 GX2DrawDone();
    void GX2WaitForVsync();

    void GX2SetAttribBuffer(sm3d::u32 index, sm3d::u32 size, sm3d::u32 stride, const void* buffer);
    void GX2DrawEx(GX2PrimitiveMode primitive, sm3d::u32 count, sm3d::u32 offset,
                   sm3d::u32 instances);
    void GX2DrawIndexedEx(GX2PrimitiveMode primitive, sm3d::u32 count, GX2IndexType indexType,
                          const void* indices, sm3d::u32 offset, sm3d::u32 instances);
    void GX2SetScissor(sm3d::u32 x, sm3d::u32 y, sm3d::u32 width, sm3d::u32 height);
    void GX2SetViewport(float x, float y, float width, float height, float nearZ, float farZ);
}
