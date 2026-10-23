#pragma once

#include "types.h"

struct CURL;
struct CURLM;
struct CURLMsg;
struct curl_slist {
    char* data;
    curl_slist* next;
};
struct curl_httppost;
struct fd_set;

typedef int CURLcode;
typedef int CURLMcode;
typedef int CURLoption;

typedef void* (*curl_malloc_callback)(sm3d::u32);
typedef void (*curl_free_callback)(void*);
typedef void* (*curl_realloc_callback)(void*, sm3d::u32);
typedef char* (*curl_strdup_callback)(const char*);
typedef void* (*curl_calloc_callback)(sm3d::u32, sm3d::u32);

extern "C"
{
    CURL* curl_easy_init();
    void curl_easy_cleanup(CURL* handle);
    CURLcode curl_easy_setopt(CURL* handle, CURLoption option, ...);
    CURLcode curl_easy_pause(CURL* handle, int bitmask);
    CURLcode curl_global_init_mem(long flags, curl_malloc_callback allocate,
                                  curl_free_callback release, curl_realloc_callback reallocate,
                                  curl_strdup_callback duplicate, curl_calloc_callback calloc);
    void curl_formfree(curl_httppost* form);
    CURLM* curl_multi_init();
    CURLMcode curl_multi_cleanup(CURLM* multi);
    CURLMcode curl_multi_add_handle(CURLM* multi, CURL* easy);
    CURLMcode curl_multi_remove_handle(CURLM* multi, CURL* easy);
    CURLMcode curl_multi_perform(CURLM* multi, int* running);
    CURLMcode curl_multi_fdset(CURLM* multi, fd_set* read, fd_set* write, fd_set* except,
                               int* maxfd);
    CURLMcode curl_multi_timeout(CURLM* multi, long* milliseconds);
    CURLMsg* curl_multi_info_read(CURLM* multi, int* remaining);
    curl_slist* curl_slist_append(curl_slist* list, const char* string);
    void curl_slist_free_all(curl_slist* list);
}
