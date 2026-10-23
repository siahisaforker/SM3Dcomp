#pragma once

#include "types.h"

struct KPADStatus;
struct KPADUnifiedWpadStatus;

enum WPADChan {
    WPAD_CHAN_0 = 0,
    WPAD_CHAN_1 = 1,
    WPAD_CHAN_2 = 2,
    WPAD_CHAN_3 = 3
};

typedef WPADChan KPADChan;

enum KPADError {
    KPAD_ERROR_OK = 0,
    KPAD_ERROR_NO_SAMPLES = -1,
    KPAD_ERROR_INVALID_CONTROLLER = -2,
    KPAD_ERROR_WPAD_UNINIT = -3,
    KPAD_ERROR_BUSY = -4,
    KPAD_ERROR_UNINITIALIZED = -5
};

extern "C"
{
    void KPADInitEx(KPADUnifiedWpadStatus* buffer, sm3d::u32 count);
    sm3d::u32 KPADReadEx(KPADChan channel, KPADStatus* data, sm3d::u32 size, KPADError* error);
    sm3d::u32 KPADGetMplsWorkSize();
    void KPADSetMplsWorkarea(void* buffer);
    void KPADEnableDPD(KPADChan channel);
    void KPADDisableDPD(KPADChan channel);

    void WPADInit();
    void WPADDisconnect(WPADChan channel);
    void WPADControlMotor(WPADChan channel, sm3d::s32 enabled);
    void WPADEnableURCC(sm3d::s32 enabled);
}
