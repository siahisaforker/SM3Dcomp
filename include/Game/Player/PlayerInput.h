#pragma once

#include "types.h"

namespace sm3d {

struct PlayerInput {
    u8 unknown00[0x0C];
    u8 stickOn;
    u8 unknown0D[3];
    f32 moveVec[3];
    f32 moveVecNoArrange[3];
    f32 stickX;
    f32 stickY;
    u8 jumpButtonOn;
    u8 unknown31[3];
    u32 jumpTriggerFrames;
    u8 jumpButtonEnabled;
    u8 dashTrigger;
    u8 dashButtonOn;
    u8 dashButtonReleased;
    u8 unknown3C;
    u8 squatTrigger;
    u8 squatButtonOn;
    u8 hipDropTrigger;
    u8 hipDropButtonOn;
    u8 fireBallTrigger;
    u8 unknown42[2];
    u32 swimPaddleTriggerFrames;
    u8 swimPaddleTrigger;
    u8 unknown49[7];
    u32 rollingTriggerFrames;
    u8 bubbleTrigger;
    u8 climbAttackTrigger;
    u8 climbAttackButtonOn;
    u8 holdButtonOn;
    u8 unknown58[2];
    u8 releaseTrigger;
    u8 unknown5B[9];
    u32 invalidatedFrame;
    u8 unknown68[0x18];

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

typedef char player_input_size_check[sizeof(PlayerInput) == 0x80 ? 1 : -1];




}
