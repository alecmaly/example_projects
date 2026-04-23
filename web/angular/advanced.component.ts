import {
    Component,
    Input,
    Output,
    EventEmitter,
    OnInit,
    OnDestroy,
    ViewChild,
    ElementRef,
    ChangeDetectionStrategy,
    Directive,
    HostListener,
    HostBinding,
    Pipe,
    PipeTransform,
    Injectable,
} from '@angular/core';
import { Subscription } from 'rxjs';
import { CounterService } from './counter.service';

// --- Custom pipe.
@Pipe({ name: 'capitalize' })
export class CapitalizePipe implements PipeTransform {
    transform(value: string): string {
        return value ? value.charAt(0).toUpperCase() + value.slice(1) : '';
    }
}

// --- Attribute directive with host bindings/listeners.
@Directive({ selector: '[appHighlight]' })
export class HighlightDirective {
    @HostBinding('style.background')   background = 'yellow';
    @HostListener('mouseenter') onEnter() { this.background = 'orange'; }
    @HostListener('mouseleave') onLeave() { this.background = 'yellow'; }
}

// --- Child-scoped service (not providedIn root).
@Injectable()
export class LocalLogger {
    log(msg: string): void { console.log('[local]', msg); }
}

// --- Advanced component exercising DI, @Input/@Output, ViewChild,
//     OnPush change detection, lifecycle hooks, template refs, RxJS
//     subscription management.
@Component({
    selector: 'app-advanced-counter',
    changeDetection: ChangeDetectionStrategy.OnPush,
    providers: [LocalLogger],
    template: `
        <div #root>
            <button (click)="onInc()" appHighlight>+1 ({{ doubled }})</button>
            <button (click)="onReset()">reset</button>
            <input [(ngModel)]="label" />
            <span>{{ label | capitalize }}</span>
            <ng-container *ngIf="count > 5; else small">big</ng-container>
            <ng-template #small>small</ng-template>
        </div>
    `,
})
export class AdvancedCounterComponent implements OnInit, OnDestroy {
    @Input() initial = 0;
    @Output() changed = new EventEmitter<number>();
    @ViewChild('root', { static: true }) rootEl!: ElementRef<HTMLDivElement>;

    count = 0;
    doubled = 0;
    label = 'counter';

    private sub = new Subscription();

    constructor(
        private readonly counter: CounterService,
        private readonly logger: LocalLogger,
    ) {}

    ngOnInit(): void {
        this.sub.add(this.counter.count$.subscribe(n => {
            this.count = n;
            this.changed.emit(n);
        }));
        this.sub.add(this.counter.doubled$.subscribe(n => (this.doubled = n)));
        this.logger.log(`init initial=${this.initial}`);
    }

    ngOnDestroy(): void { this.sub.unsubscribe(); }

    onInc():   void { this.counter.increment(); }
    onReset(): void { this.counter.reset(); }
}
