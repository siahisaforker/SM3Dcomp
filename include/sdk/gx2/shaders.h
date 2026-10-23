#pragma once

#include "sdk/gx2/types.h"

extern "C"
{
    void GX2SetFetchShader(const GX2FetchShader* shader);
    void GX2SetVertexShader(const GX2VertexShader* shader);
    void GX2SetPixelShader(const GX2PixelShader* shader);
    void GX2SetGeometryShader(const GX2GeometryShader* shader);
    void GX2SetVertexUniformBlock(sm3d::u32 location, sm3d::u32 size, const void* data);
    void GX2SetPixelUniformBlock(sm3d::u32 location, sm3d::u32 size, const void* data);
    void GX2SetGeometryUniformBlock(sm3d::u32 location, sm3d::u32 size, const void* data);
    void GX2SetVertexUniformReg(sm3d::u32 offset, sm3d::u32 count, const void* data);
    void GX2SetPixelUniformReg(sm3d::u32 offset, sm3d::u32 count, const void* data);
    sm3d::u32 GX2GetVertexShaderGPRs(const GX2VertexShader* shader);
    sm3d::u32 GX2GetPixelShaderGPRs(const GX2PixelShader* shader);
}
