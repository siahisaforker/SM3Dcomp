#pragma once

#include "sdk/coreinit/filesystem.h"

enum SAVEStatus {
    SAVE_STATUS_OK = 0,
    SAVE_STATUS_NOT_FOUND = -6,
    SAVE_STATUS_STORAGE_FULL = -12
};

extern "C"
{
    SAVEStatus SAVEInit();
    void SAVEShutdown();
    SAVEStatus SAVEInitSaveDir(sm3d::u8 slot);
    FSStatus SAVEFlushQuota(FSClient* client, FSCmdBlock* command, sm3d::u8 slot,
                            FSErrorFlag errors);
    FSStatus SAVEGetFreeSpaceSize(FSClient* client, FSCmdBlock* command, sm3d::u8 slot,
                                  sm3d::u64* size, FSErrorFlag errors);
    FSStatus SAVEGetStat(FSClient* client, FSCmdBlock* command, sm3d::u8 slot, FSStat* stat,
                         FSErrorFlag errors);
    FSStatus SAVEOpenFile(FSClient* client, FSCmdBlock* command, sm3d::u8 slot, const char* path,
                          const char* mode, FSFileHandle* file, FSErrorFlag errors);
    FSStatus SAVERemove(FSClient* client, FSCmdBlock* command, sm3d::u8 slot, const char* path,
                        FSErrorFlag errors);
}
