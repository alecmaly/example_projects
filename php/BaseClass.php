<?php

class BaseClass {
    protected $baseVar;
    public static $staticVar = "I'm a static variable in BaseClass";
    
    public function __construct() {
        $this->baseVar = "I'm a base class variable";
    }
    
    public function baseMethod() {
        echo "This is a method from BaseClass\n";
        echo "Base var: " . $this->baseVar . "\n";
    }

    // Demonstrate a trait
    use LoggableTrait;
}

trait LoggableTrait {
    public function log($message) {
        echo "Logging: " . $message . "\n";
    }
}