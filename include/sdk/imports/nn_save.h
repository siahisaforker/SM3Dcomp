#pragma once

#include "sdk/imports/types.h"

extern "C"
{
    SAVEStatus SAVEGetSharedDataTitlePath(sm3d::u64 titleID, const char* path, char* buffer,
                                          sm3d::u32 bufferSize);
    SAVEStatus SAVEGetSharedSaveDataPath(sm3d::u64 titleID, const char* path, char* buffer,
                                         sm3d::u32 bufferSize);
    FSStatus SAVEGetStatOtherApplication(FSClient* client, FSCmdBlock* block, sm3d::u64 titleId,
                                         const char* path, FSStat* stat, FSErrorFlag errorMask);
    FSStatus SAVEOpenDir(FSClient* client, FSCmdBlock* block, sm3d::u8 slotNo, const char* path,
                         FSDirectoryHandle* handle, FSErrorFlag errorMask);
}
