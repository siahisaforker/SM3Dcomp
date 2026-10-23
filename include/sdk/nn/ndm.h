#pragma once

#include "sdk/nn/result.h"

namespace nn
{
namespace ndm
{

Result Finalize();
Result ResumeDaemons(sm3d::u32 mask);

} // namespace ndm
} // namespace nn
