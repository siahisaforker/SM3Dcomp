#pragma once

#include "sdk/imports/types.h"

extern "C"
{
    NSSLContextHandle NSSLCreateContext(sm3d::s32 unk);
    NSSLError NSSLAddServerPKIGroups(NSSLContextHandle context, sm3d::u32 flags,
                                     sm3d::s32* groups, sm3d::s32* groupCount);
    NSSLError NSSLDestroyContext(NSSLContextHandle context);
    NSSLError NSSLInit();
    int bind(int sockfd, const struct sockaddr* addr, sm3d::u32 addrlen);
    struct hostent* gethostbyname(const char* name);
    int getsockname(int sockfd, struct sockaddr* addr, sm3d::u32* addrlen);
    sm3d::u32 htonl(sm3d::u32 hostlong);
    sm3d::u16 htons(sm3d::u16 hostshort);
    char* inet_ntoa(struct in_addr in);
    int inet_pton(int af, const char* src, void* dst);
    sm3d::u32 ntohl(sm3d::u32 netlong);
    sm3d::u16 ntohs(sm3d::u16 netshort);
    ssize_t recv(int sockfd, void* buf, sm3d::u32 len, int flags);
    ssize_t recvfrom(int sockfd, void* buf, sm3d::u32 len, int flags, struct sockaddr* src_addr,
                     sm3d::u32* addrlen);
    ssize_t send(int sockfd, const void* buf, sm3d::u32 len, int flags);
    ssize_t sendto(int sockfd, const void* buf, sm3d::u32 len, int flags,
                   const struct sockaddr* dest_addr, sm3d::u32 addrlen);
    int setsockopt(int sockfd, int level, int optname, const void* optval, sm3d::u32 optlen);
    int shutdown(int sockfd, int how);
    int socket(int domain, int type, int protocol);
    void socket_lib_init();
}
