#include "Game/Stage/StageArchive.h"

extern "C" int StageFormatPrint(char* output, const char* format, ...);
extern "C" const char StagePathFormat[];

namespace sm3d
{

void StageArchive::formatPath(char* destination, const char* stageName, s32 index,
                              const char* suffix)
{
    StageFormatPrint(destination, StagePathFormat, stageName, suffix, index);
}

}
