package mono.utils

const val TAG: String = "utils"

fun clamp(n: Int, lo: Int, hi: Int): Int = maxOf(lo, minOf(hi, n))
