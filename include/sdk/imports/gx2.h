#pragma once

#include "sdk/imports/types.h"

struct GX2OutputStream;

extern "C"
{
    void GX2ExpandDepthBuffer(GX2DepthBuffer* buffer);
    sm3d::u32 GX2GetSurfaceFormatBits(GX2SurfaceFormat format);
    sm3d::u64 GX2GPUTimeToCPUTime(sm3d::u64 time);
    void GX2SampleTopGPUCycle(sm3d::u64* outCycle);
    void GX2SampleBottomGPUCycle(sm3d::u64* outCycle);
    void GX2SetStreamOutBuffer(sm3d::u32 index, GX2OutputStream* stream);
    void GX2SetStreamOutContext(sm3d::u32 index, GX2OutputStream* stream, sm3d::u32 mode);
    void GX2SaveStreamOutContext(sm3d::u32 index, GX2OutputStream* stream);
    void GX2SetTVGamma(float gamma);
    void GX2SetDRCGamma(float gamma);
    void GX2SetPixelSamplerBorderColor(sm3d::u32 unit, float red, float green,
                                        float blue, float alpha);
    void GX2SetVertexSamplerBorderColor(sm3d::u32 unit, float red, float green,
                                         float blue, float alpha);
    void GX2SetGeometrySamplerBorderColor(sm3d::u32 unit, float red, float green,
                                           float blue, float alpha);
    void GX2AllocateTilingApertureEx(GX2Surface* surface, sm3d::u32 level, sm3d::u32 depth,
                                     GX2EndianSwapMode endian, GX2ApertureHandle* outHandle,
                                     void** outAddress);
    void GX2BeginDisplayListEx(void* displayList, sm3d::u32 bytes, sm3d::s32 unk1);
    void GX2CalcColorBufferAuxInfo(GX2ColorBuffer* surface, sm3d::u32* outSize,
                                   sm3d::u32* outAlignment);
    void GX2CalcDepthBufferHiZInfo(GX2DepthBuffer* depthBuffer, sm3d::u32* outSize,
                                   sm3d::u32* outAlignment);
    sm3d::u32 GX2CalcFetchShaderSizeEx(sm3d::u32 attribs, GX2FetchShaderType fetchShaderType,
                                       GX2TessellationMode tesellationMode);
    sm3d::u32 GX2CalcGeometryShaderInputRingBufferSize(sm3d::u32 ringItemSize);
    sm3d::u32 GX2CalcGeometryShaderOutputRingBufferSize(sm3d::u32 ringItemSize);
    void GX2CalcSurfaceSizeAndAlignment(GX2Surface* surface);
    void GX2CallDisplayList(const void* displayList, sm3d::u32 bytes);
    void GX2ClearBuffersEx(GX2ColorBuffer* colorBuffer, GX2DepthBuffer* depthBuffer, float red,
                           float green, float blue, float alpha, float depth, sm3d::u8 stencil,
                           GX2ClearFlags clearMode);
    void GX2ClearColor(GX2ColorBuffer* colorBuffer, float red, float green, float blue,
                       float alpha);
    void GX2ClearDepthStencilEx(GX2DepthBuffer* depthBuffer, float depth, sm3d::u8 stencil,
                                GX2ClearFlags clearMode);
    void GX2CopyColorBufferToScanBuffer(const GX2ColorBuffer* buffer, GX2ScanTarget scanTarget);
    void GX2CopySurface(const GX2Surface* src, sm3d::u32 srcLevel, sm3d::u32 srcDepth,
                        GX2Surface* dst, sm3d::u32 dstLevel, sm3d::u32 dstDepth);
    void GX2DirectCallDisplayList(const void* displayList, sm3d::u32 bytes);
    sm3d::u32 GX2EndDisplayList(void* displayList);
    void GX2FreeTilingAperture(GX2ApertureHandle handle);
    void GX2GetContextStateDisplayList(const GX2ContextState* state, void* outDisplayList,
                                       sm3d::u32* outSize);
    sm3d::s32 GX2GetCurrentDisplayList(void** outDisplayList, sm3d::u32* outSize);
    sm3d::s32 GX2GetDisplayListWriteStatus();
    sm3d::u32 GX2GetGeometryShaderGPRs(const GX2GeometryShader* shader);
    sm3d::u32 GX2GetGeometryShaderStackEntries(const GX2GeometryShader* shader);
    sm3d::u32 GX2GetPixelShaderStackEntries(const GX2PixelShader* shader);
    void GX2GetSwapStatus(sm3d::u32* swapCount, sm3d::u32* flipCount, OSTime* lastFlip,
                          OSTime* lastVsync);
    GX2AspectRatio GX2GetSystemTVAspectRatio();
    GX2TVScanMode GX2GetSystemTVScanMode();
    sm3d::u32 GX2GetVertexShaderStackEntries(const GX2VertexShader* shader);
    void GX2InitColorBufferRegs(GX2ColorBuffer* colorBuffer);
    void GX2InitDepthBufferHiZEnable(GX2DepthBuffer* depthBuffer, sm3d::s32 enable);
    void GX2InitDepthBufferRegs(GX2DepthBuffer* depthBuffer);
    void GX2InitFetchShaderEx(GX2FetchShader* fetchShader, sm3d::u8* buffer, sm3d::u32 attribCount,
                              const GX2AttribStream* attribs, GX2FetchShaderType type,
                              GX2TessellationMode tessMode);
    void GX2InitSamplerBorderType(GX2Sampler* sampler, GX2TexBorderType borderType);
    void GX2InitSamplerDepthCompare(GX2Sampler* sampler, GX2CompareFunction depthCompare);
    void GX2RSetAllocator(GX2RAllocFunction allocFn, GX2RFreeFunction freeFn);
    void GX2SetAlphaTest(sm3d::s32 alphaTest, GX2CompareFunction func, float ref);
    void GX2SetAlphaTestReg(const GX2AlphaTestReg* reg);
    void GX2SetAlphaToMask(sm3d::s32 alphaToMask, GX2AlphaToMaskMode mode);
    void GX2SetBlendConstantColor(float red, float green, float blue, float alpha);
    void GX2SetBlendConstantColorReg(const GX2BlendConstantColorReg* reg);
    void GX2SetBlendControlReg(const GX2BlendControlReg* reg);
    void GX2SetClearDepthStencil(GX2DepthBuffer* depthBuffer, float depth, sm3d::u8 stencil);
    void GX2SetColorBuffer(const GX2ColorBuffer* colorBuffer, GX2RenderTarget target);
    void GX2SetColorControl(GX2LogicOp rop3, sm3d::u8 targetBlendEnable, sm3d::s32 multiWriteEnable,
                            sm3d::s32 colorWriteEnable);
    void GX2SetColorControlReg(const GX2ColorControlReg* reg);
    void GX2SetContextState(GX2ContextState* state);
    void GX2SetCullOnlyControl(GX2FrontFace frontFace, sm3d::s32 cullFront, sm3d::s32 cullBack);
    void GX2SetDRCScale(sm3d::u32 x, sm3d::u32 y);
    void GX2SetDefaultState();
    void GX2SetDepthBuffer(const GX2DepthBuffer* depthBuffer);
    void GX2SetDepthOnlyControl(sm3d::s32 depthTest, sm3d::s32 depthWrite,
                                GX2CompareFunction depthCompare);
    void GX2SetDepthStencilControlReg(const GX2DepthStencilControlReg* reg);
    void GX2SetGeometryShaderInputRingBuffer(const void* buffer, sm3d::u32 size);
    void GX2SetGeometryShaderOutputRingBuffer(void* buffer, sm3d::u32 size);
    void GX2SetLineWidth(float width);
    void GX2SetMaxTessellationLevel(float max);
    void GX2SetMinTessellationLevel(float min);
    void GX2SetPointLimits(float min, float max);
    void GX2SetPointSize(float width, float height);
    void GX2SetPolygonControlReg(const GX2PolygonControlReg* reg);
    void GX2SetPolygonOffset(float frontOffset, float frontScale, float backOffset, float backScale,
                             float clamp);
    void GX2SetPrimitiveRestartIndex(sm3d::u32 index);
    void GX2SetRasterizerClipControl(sm3d::s32 rasterizer, sm3d::s32 zclipEnable);
    void GX2SetShaderModeEx(GX2ShaderMode mode, sm3d::u32 numVsGpr, sm3d::u32 numVsStackEntries,
                            sm3d::u32 numGsGpr, sm3d::u32 numGsStackEntries, sm3d::u32 numPsGpr,
                            sm3d::u32 numPsStackEntries);
    void GX2SetStencilMask(sm3d::u8 frontMask, sm3d::u8 frontWriteMask, sm3d::u8 frontRef,
                           sm3d::u8 backMask, sm3d::u8 backWriteMask, sm3d::u8 backRef);
    void GX2SetStreamOutEnable(sm3d::s32 enable);
    void GX2SetSurfaceSwizzle(GX2Surface* surface, sm3d::u32 swizzle);
    void GX2SetTVScale(sm3d::u32 x, sm3d::u32 y);
    void GX2SetTargetChannelMasks(GX2ChannelMask mask0, GX2ChannelMask mask1, GX2ChannelMask mask2,
                                  GX2ChannelMask mask3, GX2ChannelMask mask4, GX2ChannelMask mask5,
                                  GX2ChannelMask mask6, GX2ChannelMask mask7);
    void GX2SetTessellation(GX2TessellationMode tessellationMode, GX2PrimitiveMode primitiveMode,
                            GX2IndexType indexType);
    void GX2SetupContextStateEx(GX2ContextState* state, sm3d::s32 unk1);
    sm3d::u32 GX2TempGetGPUVersion();
}
