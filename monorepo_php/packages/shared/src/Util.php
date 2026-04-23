<?php
namespace Mono\Shared;

final class Util {
    public static function formatUser(User $u): string {
        return "{$u->id}:{$u->name}";
    }
}
