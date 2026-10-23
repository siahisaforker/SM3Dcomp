#pragma once

#include "sdk/coreinit.h"
#include "sdk/gx2.h"
#include "sdk/gx2r.h"
#include "sdk/snd_core.h"
#include "sdk/padscore.h"
#include "sdk/proc_ui.h"
#include "sdk/nn_save.h"
#include "sdk/vpad.h"

struct FSDirectoryEntry;
struct FSStateChangeParams;
struct MCPSysProdSettings;
struct MEMBlockHeapTracking;
struct MEMBlockHeap;
struct OSRendezvous;
struct OSSystemInfo;
struct OSThreadQueue;
struct OSCalendarTime;
struct UCSysConfig;
struct GX2ColorBuffer;
struct GX2DepthBuffer;
struct GX2Surface;
struct GX2ContextState;
struct GX2AlphaTestReg;
struct GX2BlendConstantColorReg;
struct GX2BlendControlReg;
struct GX2ColorControlReg;
struct GX2DepthStencilControlReg;
struct GX2PolygonControlReg;
struct GX2AttribStream;
struct AXVoiceOffsets;
struct AXVoiceAdpcm;
struct AXVoiceAdpcmLoopData;
struct AXVoiceDeviceMixData;
struct AXVoiceSrc;
struct AXVoiceVeData;
struct AXVoiceDeviceMode;
struct WENCParams;
struct MICWorkMemory {
    sm3d::u32 sampleMaxCount;
    void* sampleBuffer;
};

struct MICStatus {
    sm3d::s32 state;
    sm3d::s32 availableData;
    sm3d::s32 bufferPos;
};
struct nsysnet_fd_set;
struct sockaddr;
struct hostent;
struct in_addr;
struct timeval;

typedef sm3d::u32 FSDirectoryHandle;
typedef sm3d::u32 MEMFrmHeapFreeMode;
typedef sm3d::s32 UCHandle;
typedef sm3d::s32 NSSLError;
typedef sm3d::s32 NSSLContextHandle;
typedef sm3d::s32 ssize_t;

typedef sm3d::u32 FSPriority;
typedef sm3d::s32 FSVolumeState;
typedef sm3d::s32 FSError;
typedef sm3d::s32 IMError;
typedef sm3d::s32 MCPError;
typedef sm3d::s32 UCError;
typedef sm3d::s32 BSPError;
typedef sm3d::s32 BSPHardwareVersion;
typedef sm3d::s32 OSSharedDataType;
typedef sm3d::s32 OSThreadSpecificID;
typedef sm3d::s32 GX2EndianSwapMode;
typedef sm3d::s32 GX2AspectRatio;
typedef sm3d::s32 GX2TVScanMode;
typedef sm3d::u32 GX2ChannelMask;
typedef sm3d::s32 GX2CompareFunction;
typedef sm3d::s32 GX2TessellationMode;
typedef sm3d::s32 GX2ClearFlags;
typedef sm3d::s32 GX2ApertureHandle;
typedef sm3d::s32 GX2FetchShaderType;
typedef sm3d::s32 GX2ShaderMode;
typedef sm3d::s32 GX2AlphaToMaskMode;
typedef sm3d::s32 GX2LogicOp;
typedef sm3d::s32 GX2FrontFace;
typedef sm3d::u32 GX2RenderTarget;
typedef sm3d::u32 GX2ScanTarget;
typedef sm3d::s32 GX2TexBorderType;
typedef sm3d::s32 AXResult;
typedef sm3d::u32 AXDeviceType;
typedef sm3d::u32 AXDeviceMode;
typedef sm3d::u32 AXDRCVSMode;
typedef sm3d::u32 AXDRCVSLC;
typedef sm3d::u32 AXDRCVSOutput;
typedef sm3d::u32 AXDRCVSSpeakerPosition;
typedef sm3d::u32 AXDRCVSSurroundLevelGain;
typedef sm3d::u16 AXVoiceLoop;
typedef sm3d::u32 AXVoiceSrcType;
typedef sm3d::u32 AXVoiceType;
typedef sm3d::s32 WPADError;
typedef sm3d::s32 WPADExtensionType;
typedef sm3d::s32 WPADSpeakerCmd;
typedef sm3d::s32 MICHandle;
typedef sm3d::s32 MICError;
typedef sm3d::s32 MICInstance;
typedef sm3d::s32 SYSTEM_APP_ID;

typedef void (*AXFrameCallback)();
typedef void (*AXDeviceFinalMixCallback)(void*);
typedef void (*AXAuxCallback)(void*, void*);
typedef void (*WPADCallback)(WPADChan channel, WPADError status);
typedef OSDynLoad_Error (*OSDynLoadAllocFn)(sm3d::s32 size, sm3d::s32 align, void** address);
typedef void (*OSDynLoadFreeFn)(void* address);
typedef void* (*GX2RAllocFunction)(GX2RResourceFlags, sm3d::u32, sm3d::u32);
typedef void (*GX2RFreeFunction)(GX2RResourceFlags, void*);
