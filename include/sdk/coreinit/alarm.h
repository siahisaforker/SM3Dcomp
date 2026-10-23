#pragma once

#include "sdk/coreinit/time.h"

struct OSAlarm;
struct OSContext;
typedef void (*OSAlarmCallback)(OSAlarm*, OSContext*);

extern "C"
{
    void OSCreateAlarm(OSAlarm* alarm);
    sm3d::s32 OSSetAlarm(OSAlarm* alarm, OSTime time, OSAlarmCallback callback);
    sm3d::s32 OSSetPeriodicAlarm(OSAlarm* alarm, OSTime start, OSTime interval,
                                 OSAlarmCallback callback);
    sm3d::s32 OSCancelAlarm(OSAlarm* alarm);
    void* OSGetAlarmUserData(OSAlarm* alarm);
    void OSSetAlarmUserData(OSAlarm* alarm, void* data);
}
