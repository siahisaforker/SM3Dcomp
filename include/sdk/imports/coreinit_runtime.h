#pragma once

#include "types.h"

extern "C"
{
    void* memcpy(void* destination, const void* source, sm3d::u32 bytes);
    void* memmove(void* destination, const void* source, sm3d::u32 bytes);
    void* memset(void* destination, int value, sm3d::u32 bytes);
    void exit(int status);
    void OSReport(const char* format, ...);
    void OSPanic(const char* file, sm3d::u32 line, const char* format, ...);
}
