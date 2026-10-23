#pragma once

#include "sdk/nn/result.h"

typedef void (*FPAsyncCallback)(nn::Result result, void* context);

namespace nn
{
namespace fp
{

Result Initialize();
bool IsInitialized();
sm3d::u32 GetMyPrincipalId();
Result GetFriendList(sm3d::u32* principals, sm3d::u32* count, sm3d::u32 slot, sm3d::u32 capacity);
Result LoginAsync(FPAsyncCallback callback, void* context);
Result RegisterAccountAsync(FPAsyncCallback callback, void* context);
sm3d::u32 ResultToErrorCode(Result result);

} // namespace fp
} // namespace nn
