#include "Game/Player/PlayerMovementCounter.h"

#include "Game/Player/PlayerMovementTypes.h"

namespace sm3d
{

extern "C"
{
    PlayerMovementState* getMovementState(PlayerMovementSource* source);
    u32 hasMovementState(PlayerMovementState* state);
    u32 hasOtherMovementState(PlayerMovementState* state);
    u32 hasThirdMovementState(PlayerMovementState* state);

    void projectVector(Vec3f* result, const Vec3f* direction, const Vec3f* normal);
    f32 vectorLength(const Vec3f* vector);
}

void PlayerMovementCounter::update()
{
    // required for matching, cannot figure out the regswap
#if defined(INLINE_HACKS)

#include "PlayerMovementCounterUpdateInline.inc"

#else // tried to make this as semantically similar as possible, should be functionally equivalent
    PlayerMovementCollision* currentCollision = collision;
    if (!currentCollision->isAllowed())
    {
        frameCount = 0;
        return;
    }

    PlayerMovementState* state = getMovementState(movement);
    if (hasMovementState(state))
    {
        Vec3f projected;
        projectVector(&projected, &property->direction(), &property->normal());

        PlayerMovementInput* currentInput = input;
        if (currentInput->checkCondition())
        {
            f32 length = vectorLength(&projected);
            f32 threshold = player->getThreshold();

            if (length > threshold)
            {
                u32 maximumFrames = player->getMaximumFrames();
                if (frameCount < maximumFrames)
                {
                    ++frameCount;
                }
                return;
            }
        }

        if (frameCount != 0)
        {
            --frameCount;
        }
        return;
    }

    if (hasOtherMovementState(state) || hasThirdMovementState(state))
    {
        PlayerMovementInput* currentInput = input;
        Vec3f* movementVector = currentInput->getMovementVector();
        if (vectorLength(movementVector) >= 0.8f)
        {
            return;
        }
    }
    frameCount = 0;
#endif
}

} // namespace sm3d
