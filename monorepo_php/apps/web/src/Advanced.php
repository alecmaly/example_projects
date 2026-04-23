<?php
namespace Mono\Web;

// PHP advanced-feature coverage ported from the flat php/. Covers:
// trait (with `use Trait`), anonymous class, generator (yield),
// Exception throw/catch chain, closure with `use (&$var)`,
// password_hash stdlib.

// --- Trait definition + usage.
trait LoggableTrait {
    public function log(string $message): void {
        echo "Logging: " . $message . PHP_EOL;
    }
}

class AnimalAdv {
    use LoggableTrait;                                       // trait mixed in

    protected string $name;
    public function __construct(string $name) { $this->name = $name; }

    public function speak(): string { return "{$this->name} makes a sound"; }
}

class DogAdv extends AnimalAdv {
    private string $breed;
    public function __construct(string $name, string $breed) {
        parent::__construct($name);
        $this->breed = $breed;
    }
    public function speak(): string {
        return parent::speak() . " (woof, {$this->breed})";
    }

    // --- anonymous class returned from a method.
    public function getAnonymous() {
        return new class {
            public function anonymousMethod(): string {
                return "from-anonymous-class";
            }
        };
    }
}

// --- interface + abstract class + implements.
interface Speakable {
    public function speak(): string;
}

interface Describable {
    public function describe(): string;
}

abstract class AbstractAnimal implements Speakable, Describable {
    protected string $name;
    public function __construct(string $name) { $this->name = $name; }
    abstract public function speak(): string;                   // abstract method
    public function describe(): string {
        return "I am {$this->name} and I " . $this->speak();
    }
}

final class Cat extends AbstractAnimal {
    public function speak(): string { return "meow"; }
}

// --- generator (yield).
function fibonacciGenerator(int $n) {
    $a = 0; $b = 1;
    for ($i = 0; $i < $n; $i++) {
        yield $a;
        [$a, $b] = [$b, $a + $b];
    }
}

// --- custom Exception hierarchy.
class DomainException extends \RuntimeException {}

function divideNumbers(float $a, float $b): float {
    if ($b === 0.0) {
        throw new DomainException("Cannot divide by zero");
    }
    return $a / $b;
}

function advancedDemo(): void {
    $d = new DogAdv("Rex", "collie");
    echo $d->speak() . PHP_EOL;
    $d->log("called from DogAdv");                          // trait method

    $c = new Cat("Whiskers");
    echo $c->describe() . PHP_EOL;                          // abstract+interface chain

    echo $d->getAnonymous()->anonymousMethod() . PHP_EOL;   // anonymous class

    // Generator.
    foreach (fibonacciGenerator(8) as $n) {
        echo "fib: $n" . PHP_EOL;
    }

    // Closure with by-reference capture.
    $counter = 0;
    $bump = function() use (&$counter) { $counter++; };
    $bump(); $bump();
    echo "counter: $counter" . PHP_EOL;

    // Exception handling with specific subclass.
    try {
        divideNumbers(10, 0);
    } catch (DomainException $e) {
        echo "caught domain: " . $e->getMessage() . PHP_EOL;
    } catch (\Exception $e) {
        echo "caught generic: " . $e->getMessage() . PHP_EOL;
    } finally {
        echo "finally" . PHP_EOL;
    }

    // Stdlib call.
    $hashed = password_hash("password123", PASSWORD_DEFAULT);
    echo "hashed len=" . strlen($hashed) . PHP_EOL;
}

// --- readonly class (PHP 8.2) — all props immutable post-construction.
readonly class Coordinate {
    public function __construct(public float $x, public float $y) {}
}

// --- first-class callable syntax (PHP 8.1): function(...) reference.
function firstClassCallables(): array {
    $upper = strtoupper(...);
    $hash  = md5(...);
    return [$upper("hi"), $hash("hi")];
}

// --- never return type — method always throws.
class Aborter {
    public function abort(string $reason): never {
        throw new \RuntimeException($reason);
    }
}

// --- custom attribute class with args + application to class AND method.
#[\Attribute(\Attribute::TARGET_CLASS | \Attribute::TARGET_METHOD)]
class DemoRoute {
    public function __construct(public string $path, public array $methods = ['GET']) {}
}

#[DemoRoute('/api/v1', methods: ['GET', 'POST'])]
class DemoController {
    #[DemoRoute('/sub', methods: ['POST'])]
    public function handleSub(): string {
        return "sub";
    }
}
