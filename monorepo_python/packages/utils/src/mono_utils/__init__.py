TAG = "utils"


def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))
