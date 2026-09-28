#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
namespace gba_pins {
inline constexpr char ID[] = "WEACT_ESP32S3_A_N16R2_GBA_V1_20260928";
inline constexpr std::array<int,16> AD = {4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,21};
inline constexpr std::array<int,8> AH = {1,35,36,38,39,40,41,42};
inline constexpr int NCS=47, NRD=2, NWR=37, NCS2=3;
inline constexpr int UART_TX=43, UART_RX=44;
inline constexpr std::array<int,4> CTRL={NCS,NRD,NWR,NCS2};
constexpr std::uint64_t bit(int gpio) { return std::uint64_t{1} << gpio; }
template<std::size_t N> constexpr std::uint64_t mask(const std::array<int,N>& pins) {
    std::uint64_t v=0; for(int p:pins) v |= bit(p); return v;
}
constexpr unsigned popcount(std::uint64_t v) {
    unsigned n=0; while(v) { n += unsigned(v&1U); v >>= 1U; } return n;
}
inline constexpr auto AD_MASK=mask(AD), AH_MASK=mask(AH), CTRL_MASK=mask(CTRL);
inline constexpr auto ALL_MASK=AD_MASK|AH_MASK|CTRL_MASK;
inline constexpr auto FORBIDDEN_MASK=bit(0)|bit(19)|bit(20)|bit(48)|bit(43)|bit(44)|bit(45)|bit(46);
static_assert(popcount(AD_MASK)==16 && popcount(AH_MASK)==8 && popcount(CTRL_MASK)==4);
static_assert(popcount(ALL_MASK)==28,"Duplicate GPIO assignment");
static_assert((ALL_MASK & FORBIDDEN_MASK)==0,"Reserved GPIO used");
static_assert((AD_MASK >> 32U)==0,"AD must stay in bank 0");
static_assert(((AD_MASK|AH_MASK)&(bit(2)|bit(3)|bit(37)))==0);
}
