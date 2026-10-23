#pragma once

#include "types.h"

typedef void (*ProcUISaveCallback)();
typedef sm3d::u32 (*ProcUISaveCallbackEx)(void*);
typedef sm3d::u32 (*ProcUICallback)(void*);

enum ProcUICallbackType {
    PROCUI_CALLBACK_ACQUIRE = 0,
    PROCUI_CALLBACK_RELEASE = 1,
    PROCUI_CALLBACK_EXIT = 2,
    PROCUI_CALLBACK_NET_IO_START = 3,
    PROCUI_CALLBACK_NET_IO_STOP = 4,
    PROCUI_CALLBACK_HOME_BUTTON_DENIED = 5
};

enum ProcUIStatus {
    PROCUI_STATUS_IN_FOREGROUND = 0,
    PROCUI_STATUS_IN_BACKGROUND = 1,
    PROCUI_STATUS_RELEASE_FOREGROUND = 2,
    PROCUI_STATUS_EXITING = 3
};

extern "C"
{
    void ProcUIInit(ProcUISaveCallback saveCallback);
    void ProcUIInitEx(ProcUISaveCallbackEx saveCallback, void* argument);
    ProcUIStatus ProcUIProcessMessages(sm3d::s32 block);
    void ProcUIRegisterCallback(ProcUICallbackType type, ProcUICallback callback, void* argument,
                                sm3d::u32 priority);
    void ProcUIClearCallbacks();
    void ProcUIDrawDoneRelease();
    void ProcUIShutdown();
}
