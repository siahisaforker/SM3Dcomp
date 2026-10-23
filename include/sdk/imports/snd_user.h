#pragma once

#include "sdk/imports/types.h"

struct AXFXBuffers;
struct AXFXChorusExp;
struct MixControl;

typedef void* (*AXFXAllocFn)(sm3d::u32 bytes);
typedef void (*AXFXFreeFn)(void* pointer);

extern "C"
{
    void AXFXGetHooks(AXFXAllocFn* alloc, AXFXFreeFn* freeFn);
    void AXFXSetHooks(AXFXAllocFn alloc, AXFXFreeFn freeFn);
    void AXFXChorusExpCallback(AXFXBuffers* buffers, AXFXChorusExp* chorus);
    sm3d::s32 AXFXChorusExpGetMemSize(AXFXChorusExp* chorus);
    sm3d::s32 AXFXChorusExpInit(AXFXChorusExp* chorus);
    sm3d::s32 AXFXChorusExpSettingsUpdate(AXFXChorusExp* chorus);
    void AXFXChorusExpShutdown(AXFXChorusExp* chorus);

    void MIXAssignChannel(AXVoice* voice);
    void MIXInit();
    void MIXInitDeviceControl(AXVoice* voice, sm3d::u32 device,
                              sm3d::u32 deviceIndex, MixControl* control, sm3d::u32 mode);
    void MIXInitInputControl(AXVoice* voice, sm3d::u16 input, sm3d::u32 mode);
    void MIXReleaseChannel(AXVoice* voice);
    void MIXSetDeviceAux(AXVoice* voice, sm3d::u32 device, sm3d::u32 deviceIndex,
                         sm3d::u32 auxiliary, sm3d::s16 volume);
    void MIXSetInput(AXVoice* voice, sm3d::u16 input);
    void MIXSetSoundMode(sm3d::u32 mode);
    void MIXUpdateSettings();
}
