<?php
namespace Mono\Web;

// Labeled scope test cases for PHP — monorepo edition.
// Cross-package refs target Mono\Shared (workspace) + Mono\Shared\ScopesNs.

use Mono\Shared\User as SharedUser;              // used by S09
use Mono\Shared\Util as Util;
use Mono\Shared\Util as UtilAlias;               // S09.def
use Mono\Shared\ScopesNs\Widget;                  // S14.import

$MONO_MODULE_VAR = "mod-initial";                 // S04.def

function mono_s01_local(): void {
    $local_a = "S01.local";                       // S01.def
    echo $local_a . PHP_EOL;                      // S01.read
}

function mono_s02_closure_read(): void {
    $outer_a = "S02.outer";                       // S02.outer.def
    $inner = function() use ($outer_a) {          // S02.inner.read
        echo $outer_a . PHP_EOL;
    };
    $inner();
}

function mono_s03_closure_write(): int {
    $counter = 0;                                 // S03.outer.def
    $bump = function() use (&$counter) {          // S03.inner.write
        $counter++;
    };
    $bump(); $bump();
    return $counter;                              // S03.outer.read
}

function mono_s05_same_module_write(): void {
    global $MONO_MODULE_VAR;
    $MONO_MODULE_VAR = "rotated";                 // S05.write
    echo $MONO_MODULE_VAR . PHP_EOL;              // S05.read
}

function mono_s06_cross_read(): string {
    $u = new SharedUser(1, "alice");
    return UtilAlias::formatUser($u);             // S06.read via cross-pkg class
}

function mono_s07_cross_write(): void {
    // No native mutable class-level state in our shared pkg — mutate via
    // a global side-effect to model the cross-pkg write path.
    $GLOBALS['CROSS_WRITE_SENTINEL'] = "S07";     // S07.write
}

function mono_s08_shadowing(): void {
    $MONO_MODULE_VAR = "shadowed";                // S08.shadow.def
    echo $MONO_MODULE_VAR . PHP_EOL;              // S08.shadow.read
}

function mono_s09_aliased_import(): void {
    // Exercise aliased use via the `UtilAlias` import above.
    echo UtilAlias::formatUser(new SharedUser(9, "s9")) . PHP_EOL;   // S09.read
}

class MonoScopeBase {
    public static int $staticX = 1;               // S12.static.def / S13.base.def
    public int $x;                                // S11.instance.def
    public function __construct(int $x) { $this->x = $x; }
    public function readInstance(int $x): int {
        return $x + $this->x;                     // S11.param.read + S11.instance.read
    }
}

class MonoScopeDerived extends MonoScopeBase {
    public function __construct() { parent::__construct(5); }
    public function readInherited(): int {
        return self::$staticX;                    // S13.derived.read
    }
}

function mono_s14_qualified(): string {
    return (new Widget("hi"))->label;             // S14.read
}

function run_scope_demo_mono(): void {
    mono_s01_local();
    mono_s02_closure_read();
    echo mono_s03_closure_write() . PHP_EOL;
    mono_s05_same_module_write();
    echo mono_s06_cross_read() . PHP_EOL;
    mono_s07_cross_write();
    mono_s08_shadowing();
    mono_s09_aliased_import();
    echo (new MonoScopeBase(42))->readInstance(100) . PHP_EOL;
    echo (new MonoScopeDerived())->readInherited() . PHP_EOL;
    echo mono_s14_qualified() . PHP_EOL;
}
