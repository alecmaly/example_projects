import { BaseClass, DerivedClass } from './module1';
import { function1, MODULE2_CONSTANT, exportedVar } from './module2';

const globalVar: string = "I'm global in main";

async function main(): Promise<void> {
    const localVar: string = "I'm local to main";
    console.log(globalVar);
    console.log(localVar);
    console.log(`Imported constant: ${MODULE2_CONSTANT}`);

    const baseObj = new BaseClass();
    const derivedObj = new DerivedClass();

    await baseObj.baseMethod();
    await derivedObj.baseMethod();
    await derivedObj.derivedMethod();

    await function1();
    await recursiveFunctionAsync(5);

    // Accessing module-level variables
    console.log(`BaseClass static var: ${BaseClass.staticVar}`);
    console.log(`Module2 exported var: ${exportedVar}`);

    // Demonstrate function overloading
    console.log(add(5, 3));
    console.log(add("Hello", "World"));

    // Demonstrate generic constraints
    const numberProcessor = new NumberProcessor<number>();
    console.log(numberProcessor.process(10));

    // Demonstrate async iterator
    for await (const item of generateSequence()) {
        console.log(`Generated: ${item}`);
    }
}

async function recursiveFunctionAsync(n: number): Promise<void> {
    if (n <= 0) return;
    console.log(`Recursion level: ${n}`);
    await new Promise(resolve => setTimeout(resolve, 100));
    await recursiveFunctionAsync(n - 1);
}

// Function overloading
function add(a: number, b: number): number;
function add(a: string, b: string): string;
function add(a: any, b: any): any {
    return a + b;
}

// Generic class with constraint
class NumberProcessor<T extends number | bigint> {
    process(input: T): T {
        return input;
    }
}

// Async iterator
async function* generateSequence(): AsyncIterableIterator<number> {
    for (let i = 0; i < 5; i++) {
        await new Promise(resolve => setTimeout(resolve, 100));
        yield i;
    }
}

main().catch(console.error);