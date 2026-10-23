#pragma once

#include "types.h"

struct z_stream;
typedef z_stream* z_streamp;
typedef sm3d::u32 z_uLong;
typedef sm3d::u32 z_uLongf;

extern "C"
{
    int compress(sm3d::u8* destination, z_uLongf* destinationLength, const sm3d::u8* source,
                 z_uLong sourceLength);
    int uncompress(sm3d::u8* destination, z_uLongf* destinationLength, const sm3d::u8* source,
                   z_uLong sourceLength);
    int inflate(z_streamp stream, int flush);
    int inflateEnd(z_streamp stream);
    int inflateInit2_(z_streamp stream, int windowBits, const char* version, int streamSize);
}
