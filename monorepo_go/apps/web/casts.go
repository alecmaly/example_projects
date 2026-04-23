package main

import (
	"fmt"
	"strconv"
)

// 1. Numeric type conversion — T(x) syntax.
func numericConversions() {
	var i int = 300
	var b byte = byte(i)   // truncating
	var f float64 = float64(i)
	fmt.Printf("num: i=%d b=%d f=%g\n", i, b, f)
}

// 2. String <-> numeric via strconv.
func strconvDemo() {
	n, _ := strconv.Atoi("42")
	s := strconv.FormatFloat(3.14, 'f', 2, 64)
	fmt.Printf("strconv: n=%d s=%s\n", n, s)
}

// 3. Type assertion — interface{} → concrete type.
func typeAssertion(x any) {
	if s, ok := x.(string); ok {
		fmt.Printf("is string: %q\n", s)
	}
	if n, ok := x.(int); ok {
		fmt.Printf("is int: %d\n", n)
	}
}

// 4. Type switch.
func typeSwitch(x any) string {
	switch v := x.(type) {
	case string: return "s=" + v
	case int:    return fmt.Sprintf("i=%d", v)
	case nil:    return "nil"
	default:     return fmt.Sprintf("other %T", v)
	}
}

// 5. Interface satisfaction — implicit, via method set.
type Stringer2 interface{ String() string }
type Money struct{ cents int }
func (m Money) String() string { return fmt.Sprintf("$%.2f", float64(m.cents)/100) }

// 6. Slice → array conversion (Go 1.20+).
func sliceToArray() {
	s := []int{1, 2, 3, 4}
	a := [4]int(s)     // panics if len != 4
	fmt.Println(a)
}

// 7. Byte slice <-> string.
func bytesString() {
	s := "hi"
	b := []byte(s)
	fmt.Println(b, string(b))
}

func runCastsDemoGo() {
	numericConversions()
	strconvDemo()
	typeAssertion("hello"); typeAssertion(42); typeAssertion(3.14)
	fmt.Println(typeSwitch("x"), typeSwitch(7), typeSwitch(nil))
	var s Stringer2 = Money{1299}
	fmt.Println(s.String())
	sliceToArray()
	bytesString()
}
