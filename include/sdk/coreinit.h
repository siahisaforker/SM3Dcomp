#pragma once

#include "types.h"
#include "sdk/coreinit/filesystem.h"
#include "sdk/coreinit/heap.h"
#include "sdk/coreinit/default_heap.h"
#include "sdk/coreinit/sync.h"
#include "sdk/coreinit/thread.h"
#include "sdk/coreinit/time.h"
#include "sdk/coreinit/alarm.h"
#include "sdk/coreinit/interrupts.h"

typedef void* OSDynLoad_Module;
typedef sm3d::u32 OSDynLoad_Error;

enum OSDynLoad_ExportType {
    OS_DYNLOAD_EXPORT_FUNC = 0,
    OS_DYNLOAD_EXPORT_DATA = 1
};

extern "C"
{
    sm3d::u32 OSGetCoreCount();
    sm3d::u32 OSGetCoreId();
    sm3d::u32 OSGetMainCoreId();
    sm3d::s32 OSIsMainCore();

    void* OSBlockMove(void* destination, const void* source, sm3d::u32 size, sm3d::s32 flush);
    void DCFlushRange(void* address, sm3d::u32 size);
    void DCFlushRangeNoSync(void* address, sm3d::u32 size);
    void DCInvalidateRange(void* address, sm3d::u32 size);
    void DCZeroRange(void* address, sm3d::u32 size);

    OSTick OSGetTick();
    OSTime OSGetTime();
    OSTime OSGetSystemTime();

    OSDynLoad_Error OSDynLoad_Acquire(const char* name, OSDynLoad_Module* module);
    OSDynLoad_Error OSDynLoad_FindExport(OSDynLoad_Module module, OSDynLoad_ExportType type,
                                         const char* name, void** address);
}
