export const MODULE2_CONSTANT = "I'm a constant in module2";
export const exportedVar = "I'm an exported variable in module2";

export async function function1(): Promise<void> {
    console.log("This is function1 from module2");
    console.log(`Accessing module constant: ${MODULE2_CONSTANT}`);
    await internalFunction();
}

async function internalFunction(): Promise<void> {
    const localVar: string = "I'm local to internalFunction";
    console.log("This is an internal function in module2");
    console.log(`Local var: ${localVar}`);
    console.log(`Exported var: ${exportedVar}`);
    await new Promise(resolve => setTimeout(resolve, 100)); // Simulate some async work
}