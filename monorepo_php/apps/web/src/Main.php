<?php
namespace Mono\Web;

// Class import.
use Mono\Shared\User;
use Mono\Shared\Util;
// Aliased import.
use Mono\Shared\Role as UserRole;
// Import a namespaced FUNCTION (PHP 5.6+).
use function Mono\Shared\hello;
// Import a namespaced CONSTANT.
use const Mono\Shared\DEFAULT_ROLE;
// Grouped import.
use Mono\Utils\{Clamp, TAG as UTILS_TAG};

final class Main {
    public static function run(): void {
        $u    = new User(1, 'alice');
        $role = UserRole::Admin;
        echo Util::formatUser($u) . ' ' . $role->value . PHP_EOL;
        echo hello('world') . PHP_EOL;
        echo 'default=' . DEFAULT_ROLE->value . PHP_EOL;
        echo 'tag=' . UTILS_TAG . ' clamped=' . Clamp::between(42, 0, 10) . PHP_EOL;

        // Ported coverage from the flat php/ fixture.
        require_once __DIR__ . '/Features.php';
        require_once __DIR__ . '/Scopes.php';
        require_once __DIR__ . '/Imports.php';
        require_once __DIR__ . '/Advanced.php';
        require_once __DIR__ . '/Casts.php';
        require_once __DIR__ . '/../../../packages/shared/src/Chain/Origin.php';
        require_once __DIR__ . '/../../../packages/shared/src/Chain/Middle.php';
        require_once __DIR__ . '/../../../packages/shared/src/Chain/Deep.php';
        \Mono\Web\phpFeaturesDemoMono();
        \Mono\Web\run_scope_demo_mono();
        \Mono\Web\imports_demo_mono_php();
        \Mono\Web\advancedDemo();
        \Mono\Web\runCastsDemoPhp();

        // T1 transitive chain — Deep::VALUE_ALIAS must trace back to
        // Origin::ORIGIN_VALUE through the two re-exported constants.
        echo 'transitive: ' . \Mono\Shared\Chain\Deep::VALUE_ALIAS . PHP_EOL;

        // Cycle: CycleA ↔ CycleB.
        require_once __DIR__ . '/CycleA.php';
        require_once __DIR__ . '/CycleB.php';
        echo 'cycle: ' . \Mono\Web\CycleA::kickOff() . PHP_EOL;
    }
}
