#pragma once

#include "sdk/imports/types.h"

extern "C"
{
    sm3d::u64 _SYSGetSystemApplicationTitleId(SYSTEM_APP_ID id);
    void SYSLaunchSettings();
}
