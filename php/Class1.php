<?php
class Class1 {
    private $privateVar;
    public static $staticVar = "I'm a static variable in Class1";
    
    public function __construct() {
        $this->privateVar = "I'm private";
    }
    
    public function method1() {
        echo "This is method1 from Class1\n";
        $this->privateMethod();
    }
    
    private function privateMethod() {
        echo "This is a private method in Class1\n";
        echo "Private var: " . $this->privateVar . "\n";
        echo "Static var: " . self::$staticVar . "\n";
    }
}