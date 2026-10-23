#pragma once

#include "types.h"

struct OSThread;
struct OSMutex;
struct OSCondition;
struct OSEvent;
struct OSMessage;
struct OSMessageQueue;

enum OSEventMode {
    OS_EVENT_MODE_MANUAL = 0,
    OS_EVENT_MODE_AUTO = 1
};

enum OSMessageFlags {
    OS_MESSAGE_FLAGS_NONE = 0,
    OS_MESSAGE_FLAGS_BLOCKING = 1,
    OS_MESSAGE_FLAGS_HIGH_PRIORITY = 2
};

extern "C"
{
    void OSInitMutex(OSMutex* mutex);
    void OSLockMutex(OSMutex* mutex);
    sm3d::s32 OSTryLockMutex(OSMutex* mutex);
    void OSUnlockMutex(OSMutex* mutex);

    void OSInitCond(OSCondition* condition);
    void OSSignalCond(OSCondition* condition);
    void OSWaitCond(OSCondition* condition, OSMutex* mutex);

    void OSInitEvent(OSEvent* event, sm3d::s32 initial, OSEventMode mode);
    void OSSignalEvent(OSEvent* event);
    void OSResetEvent(OSEvent* event);
    void OSWaitEvent(OSEvent* event);
    sm3d::s32 OSWaitEventWithTimeout(OSEvent* event, sm3d::s64 timeout);

    void OSInitMessageQueue(OSMessageQueue* queue, OSMessage* messages, sm3d::s32 count);
    sm3d::s32 OSSendMessage(OSMessageQueue* queue, OSMessage* message, OSMessageFlags flags);
    sm3d::s32 OSReceiveMessage(OSMessageQueue* queue, OSMessage* message, OSMessageFlags flags);
}
