#pragma once

#include "sdk/nn/result.h"

namespace nn
{
namespace ac
{

Result Initialize();
Result Connect();
Result GetAssignedAddress(unsigned long* address);
Result GetAssignedSubnet(unsigned long* subnet);
Result GetLastErrorCode(sm3d::u32* error);

} // namespace ac
} // namespace nn
