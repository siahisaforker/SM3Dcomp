cmake_minimum_required(VERSION 3.24)

project(SM3DcompTools VERSION 0.1.0 LANGUAGES C CXX)

if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tools/wiiurpxtool/wiiurpxtool.cpp")
    message(FATAL_ERROR
        "wiiurpxtool is missing. Run `git submodule update --init tools/wiiurpxtool`.")
endif()

include(FetchContent)
set(ZLIB_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(ZLIB_BUILD_SHARED OFF CACHE BOOL "" FORCE)
set(ZLIB_BUILD_STATIC ON CACHE BOOL "" FORCE)
FetchContent_Declare(
    zlib
    GIT_REPOSITORY https://github.com/madler/zlib.git
    GIT_TAG 51b7f2abdade71cd9bb0e7a373ef2610ec6f9daf
    GIT_SHALLOW FALSE
)
FetchContent_MakeAvailable(zlib)

add_executable(wiiurpxtool tools/wiiurpxtool/wiiurpxtool.cpp)
target_link_libraries(wiiurpxtool PRIVATE zlibstatic)
target_compile_features(wiiurpxtool PRIVATE cxx_std_11)
if(NOT WIN32)
    # The upstream source includes <io.h>, but does not use anything from it.
    target_include_directories(wiiurpxtool PRIVATE tools/wiiurpxtool-compat)
endif()

if(MSVC)
    target_compile_options(wiiurpxtool PRIVATE /W4)
else()
    target_compile_options(wiiurpxtool PRIVATE -Wall -Wextra -Wpedantic)
endif()
