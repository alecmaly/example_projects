import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

// Angular service with DI scope + RxJS stream.
@Injectable({ providedIn: 'root' })
export class CounterService {
    private readonly _count$ = new BehaviorSubject<number>(0);
    readonly count$: Observable<number> = this._count$.asObservable();
    readonly doubled$: Observable<number> = this.count$.pipe(map(n => n * 2));

    increment(): void { this._count$.next(this._count$.value + 1); }
    reset(): void     { this._count$.next(0); }
}
