pub const TAG: &str = "utils";

pub fn clamp<T: Ord>(n: T, lo: T, hi: T) -> T {
    std::cmp::max(lo, std::cmp::min(hi, n))
}
