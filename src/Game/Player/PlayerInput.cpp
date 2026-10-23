#include "Game/Player/PlayerInput.h"

namespace sm3d {

bool PlayerInput::isJumpTrigOn() const
{
    return jumpTriggerFrames < 10;
}

bool PlayerInput::isPrecedingSwimPaddleTrigOn() const
{
    return swimPaddleTriggerFrames < 5;
}

bool PlayerInput::isRollingTrigOn() const
{
    return rollingTriggerFrames < 5;
}

}
