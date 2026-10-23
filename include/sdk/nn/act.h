#pragma once

#include "sdk/nn/result.h"

struct FFLStoreData;
struct ACTNexAuthenticationResult;

namespace nn
{
namespace act
{

typedef sm3d::u8 SlotNo;
typedef sm3d::u32 PersistentId;
typedef sm3d::u32 PrincipalId;
typedef sm3d::u64 TransferableId;

Result AcquireNexServiceToken(ACTNexAuthenticationResult* result, sm3d::u32 gameId);
Result Initialize();
Result Finalize();
Result GetAccountId(char* accountId);
sm3d::u32 GetErrorCode(const Result& result);
Result GetMii(FFLStoreData* mii);
Result GetMiiName(wchar_t* name);
Result GetParentalControlSlotNoEx(SlotNo* result, SlotNo slot);
PersistentId GetPersistentIdEx(SlotNo slot);
PrincipalId GetPrincipalId();
SlotNo GetSlotNo();
TransferableId GetTransferableId(sm3d::u32 value);
Result GetTransferableIdEx(TransferableId* result, sm3d::u32 value, SlotNo slot);
bool HasNfsAccount();
bool IsNetworkAccount();

} // namespace act
} // namespace nn
