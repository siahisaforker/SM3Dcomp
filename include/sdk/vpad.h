#pragma once

#include "types.h"

enum VPADChan {
    VPAD_CHAN_0 = 0,
    VPAD_CHAN_1 = 1
};

enum VPADReadError {
    VPAD_READ_SUCCESS = 0,
    VPAD_READ_NO_SAMPLES = -1,
    VPAD_READ_INVALID_CONTROLLER = -2,
    VPAD_READ_BUSY = -4,
    VPAD_READ_UNINITIALIZED = -5
};

enum VPADButtons {
    VPAD_BUTTON_A = 0x8000,
    VPAD_BUTTON_B = 0x4000,
    VPAD_BUTTON_X = 0x2000,
    VPAD_BUTTON_Y = 0x1000,
    VPAD_BUTTON_LEFT = 0x0800,
    VPAD_BUTTON_RIGHT = 0x0400,
    VPAD_BUTTON_UP = 0x0200,
    VPAD_BUTTON_DOWN = 0x0100,
    VPAD_BUTTON_ZL = 0x0080,
    VPAD_BUTTON_ZR = 0x0040,
    VPAD_BUTTON_L = 0x0020,
    VPAD_BUTTON_R = 0x0010,
    VPAD_BUTTON_PLUS = 0x0008,
    VPAD_BUTTON_MINUS = 0x0004,
    VPAD_BUTTON_HOME = 0x0002,
    VPAD_BUTTON_SYNC = 0x0001,
    VPAD_BUTTON_TV = 0x00010000,
    VPAD_BUTTON_STICK_R = 0x00020000,
    VPAD_BUTTON_STICK_L = 0x00040000
};

struct VPADStatus;
struct VPADTouchData;

extern "C"
{
    void VPADInit();
    sm3d::s32 VPADRead(VPADChan channel, VPADStatus* samples, sm3d::u32 count,
                       VPADReadError* error);
    sm3d::s32 VPADControlMotor(VPADChan channel, sm3d::u8* pattern, sm3d::u8 length);
    void VPADStopMotor(VPADChan channel);
    void VPADGetTPCalibratedPoint(VPADChan channel, VPADTouchData* calibrated,
                                  const VPADTouchData* raw);
}
