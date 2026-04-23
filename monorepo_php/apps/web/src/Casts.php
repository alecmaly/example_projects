<?php
namespace Mono\Web;

// 1. Explicit type-cast operators.
function castOps(): void {
    $s = "42";
    $i = (int)$s;                         // int cast
    $f = (float)"3.14";                   // float cast
    $b = (bool)"yes";                     // bool cast
    $a = (array)"scalar";                 // scalar → single-element array
    $o = (object)['a' => 1];              // array → stdClass
    $s2 = (string)$i;
    echo "$i $f " . ($b ? 'T' : 'F') . " " . print_r($a, true) . " " . $s2 . PHP_EOL;
    echo $o->a . PHP_EOL;
}

// 2. settype (in-place conversion).
function settypeDemo(): void {
    $x = "123";
    settype($x, "integer");
    echo "settype=" . gettype($x) . " val=$x" . PHP_EOL;
}

// 3. Function-form conversions.
function fnConversions(): void {
    echo intval("42abc") . PHP_EOL;       // 42
    echo floatval("3.14") . PHP_EOL;
    echo strval(1 + 2) . PHP_EOL;
    echo boolval(0) ? "T" : "F";
    echo PHP_EOL;
}

// 4. instanceof / get_class.
function typeTests(mixed $x): void {
    if ($x instanceof \DateTime)  echo "is DateTime" . PHP_EOL;
    echo "class: " . (is_object($x) ? get_class($x) : gettype($x)) . PHP_EOL;
}

// 5. __toString magic method.
class Dollar {
    public function __construct(public readonly int $cents) {}
    public function __toString(): string {
        return '$' . number_format($this->cents / 100, 2);
    }
}

// 6. Union-type parameter + narrowing.
function show(int|string $x): string {
    return is_int($x) ? "int=$x" : "str=$x";
}

function runCastsDemoPhp(): void {
    castOps();
    settypeDemo();
    fnConversions();
    typeTests(new \DateTime());
    typeTests("not a datetime");
    echo (string) new Dollar(1299) . PHP_EOL;
    echo show(42) . " / " . show("hi") . PHP_EOL;
}
