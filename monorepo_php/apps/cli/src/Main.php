<?php
namespace Mono\Cli;

use Mono\Shared\User;
use Mono\Shared\Util;

final class Main {
    public static function run(): void {
        echo Util::formatUser(new User(99, 'cli-user')) . PHP_EOL;
    }
}
