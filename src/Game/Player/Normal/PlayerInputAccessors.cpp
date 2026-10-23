#include "Game/Player/Normal/PlayerInput.h"

void PlayerInput::disableJumpButton()
{
    mIsJumpButtonEnabled = 0;
}

void PlayerInput::enableJumpButton()
{
    mIsJumpButtonEnabled = 1;
}

u8 PlayerInput::isStickOn() const
{
    return mIsStickOn;
}

const sead::Vector3f& PlayerInput::getMoveVec() const
{
    return mMoveVec;
}

const sead::Vector3f& PlayerInput::getMoveVecNoArrange() const
{
    return mMoveVecNoArrange;
}

f32 PlayerInput::getStickX() const
{
    return mStick.x;
}

f32 PlayerInput::getStickY() const
{
    return mStick.y;
}

s32 PlayerInput::getFrameFromLastJumpTrig() const
{
    return mFrameFromLastJumpTrig;
}

u8 PlayerInput::isJumpButtonOn() const
{
    return mIsJumpButtonOn;
}

u8 PlayerInput::isDashTrigOn() const
{
    return mIsDashTrigOn;
}

u8 PlayerInput::isDashButtonOn() const
{
    return mIsDashButtonOn;
}

u8 PlayerInput::isDashButtonReleased() const
{
    return mIsDashButtonReleased;
}

u8 PlayerInput::isSquatTrigOn() const
{
    return mIsSquatTrigOn;
}

u8 PlayerInput::isSquatButtonOn() const
{
    return mIsSquatButtonOn;
}

u8 PlayerInput::isHipDropTrigOn() const
{
    return mIsHipDropTrigOn;
}

u8 PlayerInput::isHipDropButtonOn() const
{
    return mIsHipDropButtonOn;
}

u8 PlayerInput::isFireBallTrigOn() const
{
    return mIsFireBallTrigOn;
}

u8 PlayerInput::isSwimPaddleTrigOn() const
{
    return mIsSwimPaddleTrigOn;
}

u8 PlayerInput::isBubbleTrigOn() const
{
    return mIsBubbleTrigOn;
}

u8 PlayerInput::isClimbAttackTrigOn() const
{
    return mIsClimbAttackTrigOn;
}

u8 PlayerInput::isClimbAttackButtonOn() const
{
    return mIsClimbAttackButtonOn;
}

u8 PlayerInput::isHoldButtonOn() const
{
    return mIsHoldButtonOn;
}

u8 PlayerInput::isReleaseTrigOn() const
{
    return mIsReleaseTrigOn;
}
