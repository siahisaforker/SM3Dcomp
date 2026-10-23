#include "Game/Player/Normal/PlayerInput.h"

void PlayerInput::resetPrecedingJump()
{
    mFrameFromLastJumpTrig = 10;
    mFrameFromLastRollingTrig = 5;
    mFrameFromLastSwimPaddleTrig = 5;
}
