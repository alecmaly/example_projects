<?php
namespace Mono\Web;

// Ported from php/Features.php. PHP 8 attribute + enum + match + readonly.

#[\Attribute(\Attribute::TARGET_METHOD | \Attribute::TARGET_CLASS)]
class AuditedAttr {
    public function __construct(public readonly string $reason = "") {}
}

enum PriorityFeat: int {
    case Low    = 1;
    case Medium = 5;
    case High   = 10;

    public function describe(): string {
        return match($this) {
            PriorityFeat::Low    => "take your time",
            PriorityFeat::Medium => "soon please",
            PriorityFeat::High   => "drop everything",
        };
    }
}

final class MoneyFeat {
    public function __construct(
        public readonly int $amount,
        public readonly string $currency,
    ) {}

    public function add(MoneyFeat $other): MoneyFeat {
        if ($other->currency !== $this->currency) {
            throw new \InvalidArgumentException("currency mismatch");
        }
        return new MoneyFeat($this->amount + $other->amount, $this->currency);
    }
}

#[AuditedAttr(reason: "top-level service")]
class ServiceFeat {
    #[AuditedAttr(reason: "side-effecting")]
    public function run(PriorityFeat $p, MoneyFeat $m): string {
        $note = match(true) {
            $p === PriorityFeat::High && $m->amount > 1000 => "urgent big payment",
            $p === PriorityFeat::High                      => "urgent",
            default                                        => "normal",
        };
        return $p->describe() . " / " . $note;
    }
}

function phpFeaturesDemoMono(): void {
    $p = PriorityFeat::High;
    echo "priority weight = " . $p->value . PHP_EOL;
    echo "describe = " . $p->describe() . PHP_EOL;

    $m1 = new MoneyFeat(500, "USD");
    $m2 = new MoneyFeat(750, "USD");
    $sum = $m1->add($m2);
    echo "sum = {$sum->amount} {$sum->currency}" . PHP_EOL;

    $svc = new ServiceFeat();
    echo $svc->run(PriorityFeat::High, $sum) . PHP_EOL;

    $ref = new \ReflectionClass(ServiceFeat::class);
    foreach ($ref->getAttributes(AuditedAttr::class) as $attr) {
        echo "attr reason=" . $attr->newInstance()->reason . PHP_EOL;
    }
}
