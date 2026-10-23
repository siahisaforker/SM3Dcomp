#pragma once

#include "sdk/imports/types.h"

extern "C"
{
    sm3d::s32 ENVGetEnvironmentVariable(const char* name, char* output, sm3d::u32 length);
    FSStatus FSFlushQuota(FSClient* client, FSCmdBlock* block, const char* path,
                          FSErrorFlag errorMask);
    sm3d::s32 FSGetErrorCodeForViewer(FSClient* client, FSCmdBlock* block);
    void OSBlockThreadsOnExit();
    void OSEnforceInorderIO();
    void OSVReport(const char* format, void* varargs);
    sm3d::s32 OSIsAddressRangeDCValid(const void* address, sm3d::u32 length);
    sm3d::u16 OSReadRegister16(sm3d::u32 device, sm3d::u32 registerId);
    void OSWriteRegister16(sm3d::u32 device, sm3d::u32 registerId, sm3d::u16 value);
    sm3d::s32 OSSetScreenCapturePermission(sm3d::s32 enabled);
    sm3d::u32 __OSReadRegister32Ex(sm3d::u32 device, sm3d::u32 registerId);
    void __OSWriteRegister32Ex(sm3d::u32 device, sm3d::u32 registerId, sm3d::u32 value);
    sm3d::u32 OSDriver_Register(char* name, sm3d::u32 nameLength, void* context,
                                void* callbacks);
    FSStatus FSChangeDir(FSClient* client, FSCmdBlock* block, const char* path,
                         FSErrorFlag errorMask);
    FSStatus FSCloseDir(FSClient* client, FSCmdBlock* block, FSDirectoryHandle handle,
                        FSErrorFlag errorMask);
    FSStatus FSGetCwd(FSClient* client, FSCmdBlock* block, char* buffer, sm3d::u32 bufferSize,
                      FSErrorFlag errorMask);
    FSError FSGetLastError(FSClient* client);
    FSError FSGetLastErrorCodeForViewer(FSClient* client);
    FSStatus FSGetStatFile(FSClient* client, FSCmdBlock* block, FSFileHandle handle, FSStat* stat,
                           FSErrorFlag errorMask);
    FSVolumeState FSGetVolumeState(FSClient* client);
    FSStatus FSOpenDir(FSClient* client, FSCmdBlock* block, const char* path,
                       FSDirectoryHandle* handle, FSErrorFlag errorMask);
    FSStatus FSReadDir(FSClient* client, FSCmdBlock* block, FSDirectoryHandle handle,
                       FSDirectoryEntry* entry, FSErrorFlag errorMask);
    FSStatus FSReadFileWithPos(FSClient* client, FSCmdBlock* block, sm3d::u8* buffer,
                               sm3d::u32 size, sm3d::u32 count, sm3d::u32 pos, FSFileHandle handle,
                               sm3d::u32 unk1, FSErrorFlag errorMask);
    FSStatus FSRemove(FSClient* client, FSCmdBlock* block, const char* path, FSErrorFlag errorMask);
    FSStatus FSSetCmdPriority(FSCmdBlock* block, FSPriority priority);
    FSStatus FSSetPosFile(FSClient* client, FSCmdBlock* block, FSFileHandle handle, sm3d::u32 pos,
                          FSErrorFlag errorMask);
    void FSSetStateChangeNotification(FSClient* client, FSStateChangeParams* info);
    IMError IMIsAPDEnabledBySysSettings(sm3d::u32* outValue);
    MCPError MCP_Close(int handle);
    MCPError MCP_GetSysProdSettings(sm3d::s32 handle, MCPSysProdSettings* settings);
    MCPError MCP_Open();
    int MEMAddBlockHeapTracking(MEMHeapHandle heap, MEMBlockHeapTracking* tracking, sm3d::u32 size);
    void* MEMAllocFromBlockHeapEx(MEMHeapHandle heap, sm3d::u32 size, sm3d::s32 align);
    void MEMFreeToBlockHeap(MEMHeapHandle heap, void* data);
    void MEMFreeToFrmHeap(MEMHeapHandle heap, MEMFrmHeapFreeMode mode);
    sm3d::u32 MEMGetAllocatableSizeForFrmHeapEx(MEMHeapHandle heap, int alignment);
    sm3d::u32 MEMGetTrackingLeftInBlockHeap(MEMHeapHandle heap);
    MEMHeapHandle MEMInitBlockHeap(MEMBlockHeap* heap, void* start, void* end,
                                   MEMBlockHeapTracking* blocks, sm3d::u32 size, sm3d::u32 flags);
    void* OSBlockSet(void* dst, sm3d::u8 val, sm3d::u32 size);
    void OSCancelAlarms(sm3d::u32 group);
    void OSConsoleWrite(const char* msg, sm3d::u32 size);
    OSDynLoad_Error OSDynLoad_SetAllocator(OSDynLoadAllocFn allocFn, OSDynLoadFreeFn freeFn);
    void OSEnableForegroundExit();
    sm3d::s32 OSEnableHomeButtonMenu(sm3d::s32 enable);
    sm3d::s32 OSGetSharedData(OSSharedDataType type, sm3d::u32 unk_r4, void** outPtr,
                              sm3d::u32* outSize);
    OSSystemInfo* OSGetSystemInfo();
    void* OSGetThreadSpecific(OSThreadSpecificID id);
    void OSInitRendezvous(OSRendezvous* rendezvous);
    void OSInitThreadQueue(OSThreadQueue* queue);
    sm3d::s32 OSIsDebuggerInitialized();
    sm3d::s32 OSIsDebuggerPresent();
    void OSMemoryBarrier();
    void OSSavesDone_ReadyToRelease();
    void OSSetThreadSpecific(OSThreadSpecificID id, void* value);
    void OSSleepTicks(OSTime ticks);
    void OSTicksToCalendarTime(OSTime time, OSCalendarTime* calendarTime);
    sm3d::s32 OSWaitRendezvous(OSRendezvous* rendezvous, sm3d::u32 coreMask);
    UCError UCClose(UCHandle handle);
    UCHandle UCOpen();
    UCError UCReadSysConfig(UCHandle handle, sm3d::u32 count, UCSysConfig* settings);
    void _Exit(int code);
    BSPError bspGetHardwareVersion(BSPHardwareVersion* version);
}
