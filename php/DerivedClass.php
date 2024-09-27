<?php
require_once 'BaseClass.php';

class DerivedClass extends BaseClass {
    private $derivedVar;
    
    public function __construct() {
        parent::__construct();
        $this->derivedVar = "I'm a derived class variable";
    }
    
    public function baseMethod() {
        parent::baseMethod();
        echo "This is an overridden method in DerivedClass\n";
    }
    
    public function derivedMethod() {
        echo "This is a method from DerivedClass\n";
        echo "Derived var: " . $this->derivedVar . "\n";
        $this->baseMethod();
        $this->log("DerivedClass method called"); // Using the trait method
    }

    // Demonstrate anonymous class
    public function getAnonymousClass() {
        return new class {
            public function anonymousMethod() {
                echo "This is a method from an anonymous class\n";
            }
        };
    }
}