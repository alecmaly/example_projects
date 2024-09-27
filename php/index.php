<?php
require_once 'BaseClass.php';
require_once 'DerivedClass.php';
require_once 'functions.php';

$globalVar = "I'm global in index";

function main() {
    $localVar = "I'm local to main";
    global $globalVar;
    echo $globalVar . "\n";
    echo $localVar . "\n";
    echo "Imported constant: " . FUNCTIONS_CONSTANT . "\n";
    
    $baseObj = new BaseClass();
    $derivedObj = new DerivedClass();
    
    $baseObj->baseMethod();
    $derivedObj->baseMethod();
    $derivedObj->derivedMethod();
    
    function1();
    recursiveFunction(5);
    
    // Accessing class-level variables
    echo "BaseClass static var: " . BaseClass::$staticVar . "\n";
    echo "Functions global: " . $GLOBALS['functionsGlobal'] . "\n";

    // Demonstrate anonymous functions and closures
    $multiplier = function($x) use ($localVar) {
        return $x * strlen($localVar);
    };
    echo "Result of multiplier: " . $multiplier(5) . "\n";

    // Demonstrate error handling
    try {
        $result = divideNumbers(10, 0);
    } catch (Exception $e) {
        echo "Caught exception: " . $e->getMessage() . "\n";
    }

    // Demonstrate generators
    foreach (fibonacciGenerator(10) as $number) {
        echo "Fibonacci number: $number\n";
    }

    // Using a standard library function
    $hashed_string = password_hash("password123", PASSWORD_DEFAULT);
    echo "Hashed string: " . $hashed_string . "\n";
}

function recursiveFunction($n) {
    if ($n <= 0) {
        return;
    }
    echo "Recursion level: $n\n";
    recursiveFunction($n - 1);
}

main();