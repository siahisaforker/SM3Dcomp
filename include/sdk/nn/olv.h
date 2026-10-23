#pragma once

#include "sdk/nn/result.h"

struct FFLStoreData;

namespace nn
{
namespace olv
{

struct DownloadedDataBase {
private:
    DownloadedDataBase();
    ~DownloadedDataBase();

public:
    sm3d::u32 GetAppDataSize() const;
    Result GetAppData(sm3d::u8* output, sm3d::u32* outputSize, sm3d::u32 size) const;
    Result GetBodyMemo(sm3d::u8* output, sm3d::u32* outputSize, sm3d::u32 size) const;
    Result GetBodyText(wchar_t* output, sm3d::u32 length) const;
    sm3d::u32 GetFeeling() const;
    Result GetMiiData(FFLStoreData* data) const;
    wchar_t* GetMiiNickname() const;
    wchar_t* GetTopicTag() const;
    sm3d::u32 GetUserPid() const;
    bool TestFlags(sm3d::u32 flags) const;
};
struct UploadParamBase {
private:
    UploadParamBase();
    ~UploadParamBase();

public:
    Result SetAppData(const sm3d::u8* data, sm3d::u32 size);
};

struct UploadPostDataParam {
private:
    UploadPostDataParam();
    ~UploadPostDataParam();

public:
    void SetSearchKey(const wchar_t* key, sm3d::u8 index);
    void SetTopicTag(const wchar_t* tag);
};

struct InitializeParam {
private:
    InitializeParam();

public:
    Result SetWork(sm3d::u8* buffer, sm3d::u32 size);
};

struct DownloadedPostData {
private:
    DownloadedPostData();

public:
    sm3d::u8* GetPostId() const;
};

struct DownloadedTopicData {
private:
    DownloadedTopicData();
};

struct StartPortalAppParam {
private:
    StartPortalAppParam();

public:
    Result SetPostId(const char* postId);
};

struct DownloadPostDataListParam {
private:
    DownloadPostDataListParam();

public:
    Result SetFlags(sm3d::u32 flags);
    Result SetPostDataMaxNum(sm3d::u32 count);
    Result SetSearchKey(const wchar_t* searchKey);
};

struct UploadEmpathyToPostDataParam {
private:
    UploadEmpathyToPostDataParam();

public:
    Result SetPostId(const char* postId);
};

struct UploadPostDataByPostAppParam {
private:
    UploadPostDataByPostAppParam();
    ~UploadPostDataByPostAppParam();

public:
    Result AddStampData(const sm3d::u8* data, sm3d::u32 size);
    void SetFlags(sm3d::u32 flags);
    void SetWork(sm3d::u8* buffer, sm3d::u32 size);
};

Result GetResultByPostApp();
Result StartPortalApp(const StartPortalAppParam* param);
Result UploadEmpathyToPostData(const UploadEmpathyToPostDataParam* param);
Result UploadPostDataByPostApp(const UploadPostDataByPostAppParam* param);
Result Initialize(const InitializeParam* param);
Result Finalize();
bool IsInitialized();
sm3d::u32 GetErrorCode(const Result& result);
Result DownloadPostDataList(DownloadedTopicData* topic, DownloadedPostData* posts,
                            sm3d::u32* count, sm3d::u32 maxCount,
                            const DownloadPostDataListParam* options);

} // namespace olv
} // namespace nn
