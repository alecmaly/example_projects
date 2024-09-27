<?php
define('FUNCTIONS_CONSTANT', "I'm a constant in functions");
$functionsGlobal = "I'm global in functions";

function function1() {
    echo "This is function1 from functions.php\n";
    internalFunction();
}

function internalFunction() {
    $localVar = "I'm local to internalFunction";
    echo "This is an internal function in functions.php\n";
    echo "Local var: $localVar\n";
    global $functionsGlobal;
    echo "Accessing global: $functionsGlobal\n";
}