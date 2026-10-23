#pragma once

#include "sdk/gx2/types.h"

extern "C"
{
    void GX2InitSampler(GX2Sampler* sampler, GX2TexClampMode clamp, GX2TexXYFilterMode filter);
    void GX2InitSamplerClamping(GX2Sampler* sampler, GX2TexClampMode clampX, GX2TexClampMode clampY,
                                GX2TexClampMode clampZ);
    void GX2InitSamplerLOD(GX2Sampler* sampler, float minimum, float maximum, float bias);
    void GX2InitSamplerXYFilter(GX2Sampler* sampler, GX2TexXYFilterMode mag, GX2TexXYFilterMode min,
                                GX2TexAnisoRatio anisotropy);
    void GX2InitSamplerZMFilter(GX2Sampler* sampler, GX2TexZFilterMode z, GX2TexMipFilterMode mip);
}
