#pragma once

#include "math/seadVector.h"

struct PlayerActionAirMove {
    void checkEndTurn();
    void update();
    void calcMoveVec(sead::Vector3f* result) const;
};
