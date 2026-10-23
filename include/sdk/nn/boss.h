#pragma once

#include "sdk/nn/result.h"

namespace nn
{
namespace boss
{

struct TaskSetting;

struct TaskResult {
private:
    explicit TaskResult(Result result);

public:
    sm3d::u32 ErrorCode() const;
};

struct Task {
private:
    Task();
    ~Task();

public:
    bool IsRegistered() const;
    Result Register(TaskSetting& settings);
    Result Initialize(const char* name, sm3d::u32 persistentId);
    Result StartScheduling(bool immediately);
    Result Unregister();
};

struct PlayReportSetting {
private:
    PlayReportSetting();
    ~PlayReportSetting();

public:
    bool Set(sm3d::u32 key, sm3d::u32 value);
    void Initialize(void* buffer, sm3d::u32 size);
};

Result Initialize();
bool IsInitialized();

} // namespace boss
} // namespace nn
