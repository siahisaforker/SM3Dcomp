#pragma once

#include "types.h"

struct FSClient;
struct FSCmdBlock;
struct FSStat;

typedef sm3d::u32 FSFileHandle;

enum FSErrorFlag {
    FS_ERROR_FLAG_NONE = 0,
    FS_ERROR_FLAG_NOT_FOUND = 8,
    FS_ERROR_FLAG_ALL = 0xffffffffu
};

enum FSStatus {
    FS_STATUS_OK = 0,
    FS_STATUS_CANCELLED = -1,
    FS_STATUS_END = -2,
    FS_STATUS_NOT_FOUND = -6,
    FS_STATUS_FATAL_ERROR = -0x400
};

extern "C"
{
    void FSInit();
    void FSShutdown();
    FSStatus FSAddClient(FSClient* client, FSErrorFlag errorMask);
    FSStatus FSDelClient(FSClient* client, FSErrorFlag errorMask);
    void FSInitCmdBlock(FSCmdBlock* command);
    FSStatus FSOpenFile(FSClient* client, FSCmdBlock* command, const char* path, const char* mode,
                        FSFileHandle* file, FSErrorFlag errorMask);
    FSStatus FSCloseFile(FSClient* client, FSCmdBlock* command, FSFileHandle file,
                         FSErrorFlag errorMask);
    FSStatus FSReadFile(FSClient* client, FSCmdBlock* command, sm3d::u8* buffer, sm3d::u32 size,
                        sm3d::u32 count, FSFileHandle file, sm3d::u32 flags, FSErrorFlag errorMask);
    FSStatus FSWriteFile(FSClient* client, FSCmdBlock* command, sm3d::u8* buffer, sm3d::u32 size,
                         sm3d::u32 count, FSFileHandle file, sm3d::u32 flags,
                         FSErrorFlag errorMask);
    FSStatus FSGetStat(FSClient* client, FSCmdBlock* command, const char* path, FSStat* stat,
                       FSErrorFlag errorMask);
}
