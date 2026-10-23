#pragma once

#include "sdk/imports/types.h"

extern "C"
{
    MICError MICClose(MICHandle handle);
    MICError MICGetState(MICHandle handle, int state, sm3d::u32* outStateVal);
    MICError MICGetStatus(MICHandle handle, MICStatus* outStatus);
    MICHandle MICInit(MICInstance instance, int unused, MICWorkMemory* workMemory,
                      MICError* outError);
    MICError MICOpen(MICHandle handle);
    MICError MICSetDataConsumed(MICHandle handle, int dataAmountConsumed);
    MICError MICSetState(MICHandle handle, int state, sm3d::u32 stateVal);
    MICError MICUninit(MICHandle handle);
}
