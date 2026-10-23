#pragma once

#include "sdk/gx2/types.h"

extern "C"
{
    void GX2InitTextureRegs(GX2Texture* texture);
    void GX2SetVertexTexture(const GX2Texture* texture, sm3d::u32 unit);
    void GX2SetPixelTexture(const GX2Texture* texture, sm3d::u32 unit);
    void GX2SetGeometryTexture(const GX2Texture* texture, sm3d::u32 unit);
    void GX2SetVertexSampler(const GX2Sampler* sampler, sm3d::u32 unit);
    void GX2SetPixelSampler(const GX2Sampler* sampler, sm3d::u32 unit);
    void GX2SetGeometrySampler(const GX2Sampler* sampler, sm3d::u32 unit);
    void GX2Invalidate(GX2InvalidateMode mode, void* buffer, sm3d::u32 size);
}
