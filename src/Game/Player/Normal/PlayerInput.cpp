#include "Game/Player/Normal/PlayerInput.h"

bool PlayerInput::isJumpTrigOn() const
{
    return mFrameFromLastJumpTrig < 10;
}

bool PlayerInput::isPrecedingSwimPaddleTrigOn() const
{
    return mFrameFromLastSwimPaddleTrig < 5;
}

bool PlayerInput::isRollingTrigOn() const
{
    return mFrameFromLastRollingTrig < 5;
}
