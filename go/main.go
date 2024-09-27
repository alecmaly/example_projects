package main

import (
    "fmt"
    "go_example/package1"
    "go_example/package2"
    "sync"
    "time"
    "crypto/rand"  // Added standard library import
    "math/big"     // Added standard library import
)

var globalVar = "I'm global in main"

func main() {
    localVar := "I'm local to main"
    fmt.Println(globalVar)
    fmt.Println(localVar)
    fmt.Println("Imported constant:", package2.Package2Constant)

    baseObj := package1.NewBaseStruct()
    derivedObj := package1.NewDerivedStruct()

    baseObj.BaseMethod()
    derivedObj.BaseMethod()
    derivedObj.DerivedMethod()

    package2.Function1()
    recursiveFunction(5)

    fmt.Println("Package1 var:", package1.Package1Var)
    fmt.Println("Package2 var:", package2.Package2Var)

    // Demonstrate goroutines and channels
    ch := make(chan int)
    go producer(ch)
    consumer(ch)

    // Demonstrate defer
    deferExample()

    // Demonstrate interfaces
    var shape package1.Shape = package1.NewCircle(5)
    fmt.Printf("Circle area: %.2f\n", shape.Area())

    // Demonstrate error handling
    result, err := package2.DivideNumbers(10, 0)
    if err != nil {
        fmt.Println("Error:", err)
    } else {
        fmt.Println("Result:", result)
    }

    // Using a standard library function
    randomNum, _ := rand.Int(rand.Reader, big.NewInt(100))
    fmt.Printf("Random number: %d\n", randomNum)
}

func recursiveFunction(n int) {
    if n <= 0 {
        return
    }
    fmt.Printf("Recursion level: %d\n", n)
    recursiveFunction(n - 1)
}

func producer(ch chan<- int) {
    for i := 0; i < 5; i++ {
        ch <- i
        time.Sleep(time.Millisecond * 100)
    }
    close(ch)
}

func consumer(ch <-chan int) {
    for num := range ch {
        fmt.Println("Received:", num)
    }
}

func deferExample() {
    defer fmt.Println("This will be printed last")
    fmt.Println("This will be printed first")
}