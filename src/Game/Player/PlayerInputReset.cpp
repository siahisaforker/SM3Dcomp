#include "Game/Player/PlayerInput.h"

namespace sm3d
{

void PlayerInput::resetPrecedingJump()
{
    jumpTriggerFrames = 10;
    rollingTriggerFrames = 5;
    swimPaddleTriggerFrames = 5;
}

} // namespace sm3d
