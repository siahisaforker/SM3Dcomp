#pragma once

#include "types.h"

struct AXVoice;
struct AXProfile;

typedef sm3d::u32 AXVoiceState;
typedef sm3d::s32 AXVoiceSrcRatioResult;
typedef void (*AXVoiceCallbackFn)(void*);
typedef void (*AXVoiceCallbackExFn)(void*, sm3d::u32, sm3d::u32);

enum AXVoicePlaybackState {
    AX_VOICE_STATE_STOPPED = 0,
    AX_VOICE_STATE_PLAYING = 1
};

extern "C"
{
    void AXInit();
    void AXQuit();
    sm3d::s32 AXIsInit();
    void AXInitProfile(AXProfile* profile, sm3d::u32 count);
    AXVoice* AXAcquireVoice(sm3d::u32 priority, AXVoiceCallbackFn callback, void* context);
    AXVoice* AXAcquireVoiceEx(sm3d::u32 priority, AXVoiceCallbackExFn callback, void* context);
    void AXFreeVoice(AXVoice* voice);
    void AXSetVoiceState(AXVoice* voice, AXVoiceState state);
    void AXSetVoicePriority(AXVoice* voice, sm3d::u32 priority);
    AXVoiceSrcRatioResult AXSetVoiceSrcRatio(AXVoice* voice, float ratio);
}
