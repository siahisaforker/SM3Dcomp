#pragma once

#include "types.h"
#include "math/seadVector.h"

struct PlayerInput {
    void* inputVTable;
    void* arrangementVTable;
    void* jumpControlVTable;
    u8 mIsStickOn;
    sead::Vector3f mMoveVec;
    sead::Vector3f mMoveVecNoArrange;
    sead::Vector2f mStick;
    u8 mIsJumpButtonOn;
    u32 mFrameFromLastJumpTrig;
    u8 mIsJumpButtonEnabled;
    u8 mIsDashTrigOn;
    u8 mIsDashButtonOn;
    u8 mIsDashButtonReleased;
    u8 _3c;
    u8 mIsSquatTrigOn;
    u8 mIsSquatButtonOn;
    u8 mIsHipDropTrigOn;
    u8 mIsHipDropButtonOn;
    u8 mIsFireBallTrigOn;
    u8 mIsTailAttackTrigOn;
    u32 mFrameFromLastSwimPaddleTrig;
    u8 mIsSwimPaddleTrigOn;
    u8 mIsSwimPaddleButtonOn;
    u8 mIsStoneStatueTrigOn;
    u8 mIsStoneStatueSustainButtonOn;
    u8 mIsRollingButtonOn;
    u32 mFrameFromLastRollingTrig;
    u8 mIsBubbleTrigOn;
    u8 mIsClimbAttackTrigOn;
    u8 mIsClimbAttackButtonOn;
    u8 mIsHoldButtonOn;
    u8 mIsHoldShakeOn;
    u8 mIsHoldTrigOn;
    u8 mIsReleaseTrigOn;
    u8 mIsSpinAttackTrigOn;
    f32 mRouteDependenceX;
    f32 mRouteDependenceY;
    u32 mInvalidFrame;
    void* mActorForAreaSearch;
    void* mCollision;
    f32 mAlongWallRate;
    s32 mAlongWallKeepFrame;
    u8 mIsWaitFirstLanding;
    const void* mKeyConfig;

    void resetPrecedingJump();
    void invalidateFrame(u32 frame);
    void disableJumpButton();
    void enableJumpButton();
    u8 isStickOn() const;
    const sead::Vector3f& getMoveVec() const;
    const sead::Vector3f& getMoveVecNoArrange() const;
    f32 getStickX() const;
    f32 getStickY() const;
    s32 getFrameFromLastJumpTrig() const;
    u8 isJumpButtonOn() const;
    u8 isDashTrigOn() const;
    u8 isDashButtonOn() const;
    u8 isDashButtonReleased() const;
    u8 isSquatTrigOn() const;
    u8 isSquatButtonOn() const;
    u8 isHipDropTrigOn() const;
    u8 isHipDropButtonOn() const;
    u8 isFireBallTrigOn() const;
    u8 isSwimPaddleTrigOn() const;
    u8 isBubbleTrigOn() const;
    u8 isClimbAttackTrigOn() const;
    u8 isClimbAttackButtonOn() const;
    u8 isHoldButtonOn() const;
    u8 isReleaseTrigOn() const;

    bool isJumpTrigOn() const;
    bool isPrecedingSwimPaddleTrigOn() const;
    bool isRollingTrigOn() const;
};
