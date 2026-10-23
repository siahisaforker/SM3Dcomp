#pragma once

#include "sdk/imports/types.h"

struct fd_set;
struct timeval;

typedef sm3d::s32 GX2BlendMode;
typedef sm3d::s32 GX2BlendCombineMode;
typedef sm3d::s32 GX2StencilFunction;
typedef sm3d::s32 GX2PolygonMode;

extern "C"
{
    FSStatus SAVEOpenFileOtherApplication(FSClient* client, FSCmdBlock* command, sm3d::u64 titleId,
                                          sm3d::u8 slot, const char* path, const char* mode,
                                          FSFileHandle* handle, FSErrorFlag errors);

    int select(int count, fd_set* read, fd_set* write, fd_set* except, timeval* timeout);
    int socketclose(int socket);
    int socketlasterr();

    void GX2SetBlendControl(GX2RenderTarget target, GX2BlendMode colorSource,
                            GX2BlendMode colorDestination, GX2BlendCombineMode colorCombine,
                            sm3d::s32 useAlpha, GX2BlendMode alphaSource,
                            GX2BlendMode alphaDestination, GX2BlendCombineMode alphaCombine);
    void GX2SetDepthStencilControl(
        sm3d::s32 depthTest, sm3d::s32 depthWrite, GX2CompareFunction depthCompare,
        sm3d::s32 stencilTest, sm3d::s32 backfaceStencil, GX2CompareFunction frontStencilCompare,
        GX2StencilFunction frontStencilPass, GX2StencilFunction frontStencilDepthFail,
        GX2StencilFunction frontStencilFail, GX2CompareFunction backStencilCompare,
        GX2StencilFunction backStencilPass, GX2StencilFunction backStencilDepthFail,
        GX2StencilFunction backStencilFail);
    void GX2SetPolygonControl(GX2FrontFace frontFace, sm3d::s32 cullFront, sm3d::s32 cullBack,
                              sm3d::s32 polygonMode, GX2PolygonMode frontMode,
                              GX2PolygonMode backMode, sm3d::s32 polygonOffsetFront,
                              sm3d::s32 polygonOffsetBack, sm3d::s32 polygonOffsetParallel);
}
