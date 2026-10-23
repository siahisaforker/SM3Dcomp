#include "Game/Player/PlayerInput.h"

namespace sm3d {

void PlayerInput::disableJumpButton()
{
    jumpButtonEnabled = 0;
}

void PlayerInput::enableJumpButton()
{
    jumpButtonEnabled = 1;
}

u8 PlayerInput::isStickOn() const
{
    return stickOn;
}

const f32* PlayerInput::getMoveVec() const
{
    return moveVec;
}

const f32* PlayerInput::getMoveVecNoArrange() const
{
    return moveVecNoArrange;
}

f32 PlayerInput::getStickX() const
{
    return stickX;
}

f32 PlayerInput::getStickY() const
{
    return stickY;
}

u32 PlayerInput::getFrameFromLastJumpTrig() const
{
    return jumpTriggerFrames;
}

u8 PlayerInput::isJumpButtonOn() const
{
    return jumpButtonOn;
}

u8 PlayerInput::isDashTrigOn() const
{
    return dashTrigger;
}

u8 PlayerInput::isDashButtonOn() const
{
    return dashButtonOn;
}

u8 PlayerInput::isDashButtonReleased() const
{
    return dashButtonReleased;
}

u8 PlayerInput::isSquatTrigOn() const
{
    return squatTrigger;
}

u8 PlayerInput::isSquatButtonOn() const
{
    return squatButtonOn;
}

u8 PlayerInput::isHipDropTrigOn() const
{
    return hipDropTrigger;
}

u8 PlayerInput::isHipDropButtonOn() const
{
    return hipDropButtonOn;
}

u8 PlayerInput::isFireBallTrigOn() const
{
    return fireBallTrigger;
}

u8 PlayerInput::isSwimPaddleTrigOn() const
{
    return swimPaddleTrigger;
}

u8 PlayerInput::isBubbleTrigOn() const
{
    return bubbleTrigger;
}

u8 PlayerInput::isClimbAttackTrigOn() const
{
    return climbAttackTrigger;
}

u8 PlayerInput::isClimbAttackButtonOn() const
{
    return climbAttackButtonOn;
}

u8 PlayerInput::isHoldButtonOn() const
{
    return holdButtonOn;
}

u8 PlayerInput::isReleaseTrigOn() const
{
    return releaseTrigger;
}

}
