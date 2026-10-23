#include "Game/Stage/StageArchive.h"

extern "C" int sprintf(char* output, const char* format, ...);
extern "C" const char StagePathFormat[];

void StageArchive::formatPath(char* destination, const char* stageName, s32 index,
                              const char* suffix)
{
    sprintf(destination, StagePathFormat, stageName, suffix, index);
}
