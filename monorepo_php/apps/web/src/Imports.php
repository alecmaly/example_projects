<?php
namespace Mono\Web;

// 1. Classic file include.
require_once __DIR__ . '/Scopes.php';

// 2. Namespaced class import — cross-workspace-package.
use Mono\Shared\User;
use Mono\Shared\Util;
// 3. Aliased.
use Mono\Shared\Util as SharedUtil;
// 4. Grouped (PHP 7+).
use Mono\Shared\{Role, DEFAULT_ROLE};
// 5. use function (namespaced function — `files` autoload).
use function Mono\Shared\hello;
// 6. use const.
use const Mono\Shared\DEFAULT_ROLE as KONST_DEFAULT;

// 7. Cross-package util pkg.
use Mono\Utils\Clamp;
use const Mono\Utils\TAG;

function imports_demo_mono_php(): void {
    $u = new User(1, "alice");
    echo Util::formatUser($u) . PHP_EOL;           // named
    echo SharedUtil::formatUser($u) . PHP_EOL;     // aliased
    echo hello("x") . PHP_EOL;                     // use function
    echo (KONST_DEFAULT === DEFAULT_ROLE ? "ok" : "?") . PHP_EOL;
    echo "tag=" . TAG . " clamp=" . Clamp::between(42, 0, 10) . PHP_EOL;
}
