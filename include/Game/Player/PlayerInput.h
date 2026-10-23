#pragma once

#include "types.h"

namespace sm3d
{

struct PlayerInput {
    void* inputVTable;
    void* arrangementVTable;
    void* jumpControlVTable;
    u8 stickOn;
    f32 moveVec[3];
    f32 moveVecNoArrange[3];
    f32 stickX;
    f32 stickY;
    u8 jumpButtonOn;
    u32 jumpTriggerFrames;
    u8 jumpButtonEnabled;
    u8 dashTrigger;
    u8 dashButtonOn;
    u8 dashButtonReleased;
    u8 reserved;
    u8 squatTrigger;
    u8 squatButtonOn;
    u8 hipDropTrigger;
    u8 hipDropButtonOn;
    u8 fireBallTrigger;
    u8 tailAttackTrigger;
    u32 swimPaddleTriggerFrames;
    u8 swimPaddleTrigger;
    u8 swimPaddleButtonOn;
    u8 stoneStatueTrigger;
    u8 stoneStatueSustainButtonOn;
    u8 rollingButtonOn;
    u32 rollingTriggerFrames;
    u8 bubbleTrigger;
    u8 climbAttackTrigger;
    u8 climbAttackButtonOn;
    u8 holdButtonOn;
    u8 holdShakeOn;
    u8 holdTriggerOn;
    u8 releaseTrigger;
    u8 spinAttackTrigger;
    f32 routeDependenceX;
    f32 routeDependenceY;
    u32 invalidatedFrame;
    void* areaSearchActor;
    void* playerCollision;
    f32 alongWallRate;
    s32 alongWallKeepFrame;
    u8 waitFirstLanding;
    const void* keyConfig;

    void resetPrecedingJump();
    void invalidateFrame(u32 frame);
    void disableJumpButton();
    void enableJumpButton();
    u8 isStickOn() const;
    const f32* getMoveVec() const;
    const f32* getMoveVecNoArrange() const;
    f32 getStickX() const;
    f32 getStickY() const;
    u32 getFrameFromLastJumpTrig() const;
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

} // namespace sm3d
