#pragma once

#include "sdk/gx2/types.h"

extern "C"
{
    void GX2SetTVEnable(sm3d::s32 enabled);
    void GX2SetDRCEnable(sm3d::s32 enabled);
    void GX2CalcTVSize(GX2TVRenderMode mode, GX2SurfaceFormat format, GX2BufferingMode buffering,
                       sm3d::u32* size, sm3d::u32* extra);
    void GX2CalcDRCSize(GX2DrcRenderMode mode, GX2SurfaceFormat format, GX2BufferingMode buffering,
                        sm3d::u32* size, sm3d::u32* extra);
    void GX2SetTVBuffer(void* buffer, sm3d::u32 size, GX2TVRenderMode mode, GX2SurfaceFormat format,
                        GX2BufferingMode buffering);
    void GX2SetDRCBuffer(void* buffer, sm3d::u32 size, GX2DrcRenderMode mode,
                         GX2SurfaceFormat format, GX2BufferingMode buffering);
    void GX2SwapScanBuffers();
    void GX2SetSwapInterval(sm3d::u32 interval);
}
