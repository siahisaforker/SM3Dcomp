#include "Game/Player/PlayerInput.h"

namespace sm3d
{

void PlayerInput::invalidateFrame(u32 frame)
{
    invalidatedFrame = frame;
}

} // namespace sm3d
