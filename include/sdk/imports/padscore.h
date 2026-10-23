#pragma once

#include "sdk/imports/types.h"

extern "C"
{
    sm3d::u32 WENCGetEncodeData(WENCParams* params, sm3d::s32 continuing, const sm3d::s16* samples,
                                sm3d::u32 sampleCount, sm3d::u8* outEncodedData);
    void WPADRegisterAllocator(void* (*allocate)(sm3d::u32 bytes),
                               sm3d::s32 (*deallocate)(void* block));
    sm3d::s32 WPADCanSendStreamData(WPADChan channel);
    sm3d::s32 WPADControlSpeaker(WPADChan channel, WPADSpeakerCmd mode, WPADCallback callback);
    sm3d::u8 WPADGetSpeakerVolume(void);
    WPADError WPADProbe(WPADChan channel, WPADExtensionType* outExtensionType);
    WPADError WPADSendStreamData(WPADChan channel, const void* data, sm3d::u32 size);
}
