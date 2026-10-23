#pragma once

#include "sdk/imports/types.h"

struct AXPBLPF;
struct AXPBBIQUAD;
struct AXDSPADPCM;

extern "C"
{
    void AXDecodeAdpcmData(const sm3d::u8* input, AXDSPADPCM* info,
                           sm3d::s32 sampleCount, sm3d::s16* output);
    AXFrameCallback AXRegisterCallback(AXFrameCallback callback);
    void AXSetMasterVolume(sm3d::u32 volume);
    void AXSetMode(sm3d::u32 mode);
    void AXSetPpcLoadLimit(float limit);
    void AXSetVoiceRmtIIR(AXVoice* voice, void* filter);
    void DRCVS_Process(sm3d::s32** inputs, sm3d::s32** outputs, sm3d::u32 samples);
    sm3d::s32 DRCVS_SetOutputMode(sm3d::u32 mode);
    void AXComputeLpfCoefs(sm3d::u32 frequency, sm3d::u16* a0, sm3d::u16* b0);
    AXResult AXSetAuxReturnVolume(AXDeviceType device, sm3d::u32 deviceId,
                                  sm3d::u32 auxiliary, sm3d::u16 volume);
    void AXSetVoiceBiquad(AXVoice* voice, AXPBBIQUAD* biquad);
    void AXSetVoiceBiquadCoefs(AXVoice* voice, sm3d::u16 b0, sm3d::u16 b1,
                               sm3d::u16 b2, sm3d::u16 a1, sm3d::u16 a2);
    void AXSetVoiceLpf(AXVoice* voice, AXPBLPF* filter);
    void AXSetVoiceLpfCoefs(AXVoice* voice, sm3d::u16 a0, sm3d::u16 b0);
    void AXSetVoiceSamplesAddr(AXVoice* voice, void* samples);
    sm3d::u32 AXSetVoiceMixerSelect(AXVoice* voice, sm3d::u32 mixer);
    sm3d::s32 AXUserBegin();
    sm3d::s32 AXUserEnd();
    sm3d::s32 AXUserIsProtected();
    AXResult AXDeregisterAppFrameCallback(AXFrameCallback callback);
    AXResult AXGetDeviceFinalMixCallback(AXDeviceType type, AXDeviceFinalMixCallback* func);
    AXResult AXGetDeviceMode(AXDeviceType type, AXDeviceMode* mode);
    sm3d::u32 AXGetSwapProfile(AXProfile* profile, sm3d::u32 count);
    sm3d::u32 AXGetVoiceCurrentOffsetEx(AXVoice* voice, const void* samples);
    sm3d::u32 AXGetVoiceLoopCount(AXVoice* voice);
    void AXGetVoiceOffsets(AXVoice* voice, AXVoiceOffsets* offsets);
    sm3d::s32 AXIsVoiceRunning(AXVoice* voice);
    AXResult AXRegisterAppFrameCallback(AXFrameCallback callback);
    AXResult AXRegisterAuxCallback(AXDeviceType type, sm3d::u32 unk0, sm3d::u32 unk1,
                                   AXAuxCallback callback, void* userData);
    AXResult AXRegisterDeviceFinalMixCallback(AXDeviceType type, AXDeviceFinalMixCallback func);
    sm3d::u32 AXRmtAdvancePtr(sm3d::u32 count);
    sm3d::u32 AXRmtGetSamples(sm3d::u32 index, sm3d::s16* samples, sm3d::u32 sampleCount);
    sm3d::u32 AXRmtGetSamplesLeft();
    AXResult AXSetDRCVSDownmixBalance(AXDRCVSOutput output, float balance);
    AXResult AXSetDRCVSLC(AXDRCVSLC lc);
    AXResult AXSetDRCVSMode(AXDRCVSMode mode);
    AXResult AXSetDRCVSOutputGain(AXDRCVSOutput output, float gain);
    AXResult AXSetDRCVSSpeakerPosition(AXDRCVSOutput output, AXDRCVSSpeakerPosition pos);
    AXResult AXSetDRCVSSurroundDepth(AXDRCVSOutput output, float depth);
    AXResult AXSetDRCVSSurroundLevelGain(AXDRCVSSurroundLevelGain gain);
    AXResult AXSetDefaultMixerSelect(sm3d::u32 unk0);
    AXResult AXSetDeviceCompressor(AXDeviceType type, sm3d::u32 unk0);
    AXResult AXSetDeviceLinearUpsampler(AXDeviceType type, sm3d::u32 unk0, sm3d::u32 unk1);
    void AXSetVoiceAdpcm(AXVoice* voice, AXVoiceAdpcm* adpcm);
    void AXSetVoiceAdpcmLoop(AXVoice* voice, AXVoiceAdpcmLoopData* loopData);
    AXResult AXSetVoiceDeviceMix(AXVoice* voice, AXDeviceType type, sm3d::u32 id,
                                 AXVoiceDeviceMixData* mixData);
    void AXSetVoiceEndOffsetEx(AXVoice* voice, sm3d::u32 offset, const void* samples);
    void AXSetVoiceLoop(AXVoice* voice, AXVoiceLoop loop);
    void AXSetVoiceLoopOffsetEx(AXVoice* voice, sm3d::u32 offset, const void* samples);
    void AXSetVoiceOffsets(AXVoice* voice, AXVoiceOffsets* offsets);
    void AXSetVoiceRmtIIRCoefs(AXVoice* voice, sm3d::u16 filter, ...);
    void AXSetVoiceRmtOn(AXVoice* voice, sm3d::u16 on);
    void AXSetVoiceSrc(AXVoice* voice, AXVoiceSrc* src);
    void AXSetVoiceSrcType(AXVoice* voice, AXVoiceSrcType type);
    void AXSetVoiceType(AXVoice* voice, AXVoiceType type);
    void AXSetVoiceVe(AXVoice* voice, AXVoiceVeData* veData);
}
