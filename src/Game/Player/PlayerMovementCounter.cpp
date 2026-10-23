#include "Game/Player/PlayerMovementCounter.h"

namespace sm3d
{

void PlayerMovementCounter::bindDependencies(PlayerMovementSource* movement,
                                             PlayerMovementCollision* collision,
                                             PlayerMovementInput* input,
                                             PlayerMovementProperty* property,
                                             PlayerMovementOwner* player)
{
    // preserve the original store order, GHS otherwise reorders these assignments
    volatile PlayerMovementCounter* ordered = this;
    ordered->player = player;
    ordered->input = input;
    ordered->movement = movement;
    ordered->collision = collision;
    ordered->property = property;
}

} // namespace sm3d
