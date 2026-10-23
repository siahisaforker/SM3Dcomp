#pragma once

namespace sm3d {

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long long u64;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
typedef signed long long s64;
typedef float f32;
typedef double f64;

typedef char u32_size_check[sizeof(u32) == 4 ? 1 : -1];
typedef char u64_size_check[sizeof(u64) == 8 ? 1 : -1];

}
