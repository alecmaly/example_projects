<?php
namespace Mono\Web;

class CycleB {
    public ?CycleA $owner = null;                    // C1.b.type_ref → CycleA

    public function __construct(public readonly string $tag) {}

    public function bounceToAlpha(): string {
        return (new CycleA("bounce-from-{$this->tag}"))->describe();
    }
}
