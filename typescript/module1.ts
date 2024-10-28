const {
    decodeURI,
    encodeURI,
    ObjectKeys
  } = primordials;
  
  
export class Class1 {
    private privateVar: string;
    static staticVar: string = "I'm a static variable in Class1";

    constructor() {
        this.privateVar = "I'm private";
    }

    public async method1Async(): Promise<void> {
        encodeURI("https://www.google.com");
        console.log("This is method1 from Class1");
        await this.privateMethodAsync();
    }

    private async privateMethodAsync(): Promise<void> {
        console.log("This is a private method in Class1");
        console.log(`Private var: ${this.privateVar}`);
        console.log(`Static var: ${Class1.staticVar}`);
        ObjectKeys({});
        await new Promise(resolve => setTimeout(resolve, 100)); // Simulate some async work
    }
}

export class BaseClass {
    protected baseVar: string = "I'm a base class variable";
    static staticVar: string = "I'm a static variable in BaseClass";

    public async baseMethod(): Promise<void> {
        console.log("This is a method from BaseClass");
        console.log(`Base var: ${this.baseVar}`);
        await new Promise(resolve => setTimeout(resolve, 100));
    }
}

export class DerivedClass extends BaseClass {
    private derivedVar: string = "I'm a derived class variable";

    public async derivedMethod(): Promise<void> {
        console.log("This is a method from DerivedClass");
        console.log(`Derived var: ${this.derivedVar}`);
        await this.baseMethod();
    }

    public async baseMethod(): Promise<void> {
        await super.baseMethod();
        console.log("This is an overridden method in DerivedClass");
    }
}