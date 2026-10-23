#pragma once

#include "sdk/imports/types.h"

struct GHSFileBuffer
{
    sm3d::u8* next;
    sm3d::u8* base;
    sm3d::s32 remaining;
    sm3d::u32 flags;
};

extern "C"
{
    extern void (*__atexit_cleanup)(sm3d::s32 code);
    extern void (*__cpp_exception_init_ptr)(void** globals);
    extern void (*__cpp_exception_cleanup_ptr)(void* globals);
    extern sm3d::u16 __gh_FOPEN_MAX;
    extern GHSFileBuffer _iob[20];

    void __gh_set_errno(sm3d::s32 error);
    void __ghsLock();
    void __ghsUnlock();
    void __ghs_flock_file(sm3d::u32 index);
    sm3d::u32* __ghs_flock_ptr(GHSFileBuffer* stream);
    void __ghs_funlock_file(sm3d::u32 index);
    void __ghs_mtx_init(OSMutex** mutex);
    void __ghs_mtx_dst(OSMutex** mutex);
    void __ghs_mtx_lock(OSMutex** mutex);
    void __ghs_mtx_unlock(OSMutex** mutex);
}
