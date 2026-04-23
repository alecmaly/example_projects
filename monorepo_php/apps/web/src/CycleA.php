<?php
namespace Mono\Web;

class CycleA {
    public ?CycleB $child = null;                    // C1.a.type_ref → CycleB

    public function __construct(public readonly string $name) {}
    public function describe(): string { return "CycleA({$this->name})"; }
    public function spawnBravo(): CycleB { return new CycleB("{$this->name}/b"); }

    public static function kickOff(): string {
        $a = new self("root");
        $b = $a->spawnBravo();
        return $b->bounceToAlpha();
    }
}
