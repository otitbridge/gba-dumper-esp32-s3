#include "../../firmware/main/pinmap.hpp"
int main() { return gba_pins::popcount(gba_pins::ALL_MASK)==28 ? 0 : 1; }
