#pragma once

#include "types.h"

struct OSThread;
typedef sm3d::u8 OSThreadAttributes;
typedef int (*OSThreadEntryPointFn)(int argc, const char** argv);

extern "C"
{
    sm3d::s32 OSCreateThread(OSThread* thread, OSThreadEntryPointFn entry, sm3d::s32 argc,
                             char* argv, void* stack, sm3d::u32 stackSize, sm3d::s32 priority,
                             OSThreadAttributes attributes);
    OSThread* OSGetCurrentThread();
    sm3d::s32 OSGetThreadPriority(OSThread* thread);
    sm3d::s32 OSSetThreadPriority(OSThread* thread, sm3d::s32 priority);
    sm3d::s32 OSSetThreadAffinity(OSThread* thread, sm3d::u32 affinity);
    sm3d::s32 OSResumeThread(OSThread* thread);
    sm3d::s32 OSJoinThread(OSThread* thread, int* result);
    sm3d::s32 OSIsThreadTerminated(OSThread* thread);
    void OSExitThread(sm3d::s32 result);
    void OSSetThreadName(OSThread* thread, const char* name);
    void OSYieldThread();
}
