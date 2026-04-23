<?php
namespace Mono\Utils;

const TAG = 'utils';

final class Clamp {
    public static function between(int $n, int $lo, int $hi): int {
        return max($lo, min($hi, $n));
    }
}
