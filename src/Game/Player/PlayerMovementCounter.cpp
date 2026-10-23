#include "Game/Player/PlayerMovementCounter.h"

namespace sm3d {

void PlayerMovementCounter::bindDependencies(void* movement, void* collision, void* input, void* property, void* player)
{
    this->player = player;
    this->input = input;
    this->movement = movement;
    this->collision = collision;
    this->property = property;
}

}
