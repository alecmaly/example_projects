package main

// Advanced-feature coverage ported from the flat go/. Covers:
// goroutine + channel producer/consumer, defer, embedded struct with
// method override, recursive fn, crypto/rand stdlib access, select.

import (
	"crypto/rand"
	"fmt"
	"math/big"
	"time"
)

// --- Embedded struct with method override — the Go analog of inheritance.
type AnimalBase struct {
	name string
}

func (a AnimalBase) Speak() string { return a.name + " makes a sound" }

type DogA struct {
	AnimalBase            // embedded — its Speak is reachable via `.Speak()`
	breed      string
}

// Override: the embedded Speak is shadowed by this method.
func (d DogA) Speak() string {
	return d.AnimalBase.Speak() + " (woof, " + d.breed + ")"
}

// --- Goroutine + channel producer/consumer pattern.
func producerAdv(ch chan<- int) {
	defer close(ch)
	for i := 0; i < 5; i++ {
		ch <- i
		time.Sleep(time.Millisecond * 2)
	}
}

func consumerAdv(ch <-chan int) {
	for n := range ch {
		fmt.Println("received:", n)
	}
}

// --- Recursive function with defer.
func recursiveAdv(n int) {
	if n <= 0 {
		return
	}
	defer fmt.Printf("unwind %d\n", n)
	fmt.Printf("recurse %d\n", n)
	recursiveAdv(n - 1)
}

// --- Select over multiple channels with timeout.
func selectWithTimeout() {
	ch := make(chan string, 1)
	go func() {
		time.Sleep(5 * time.Millisecond)
		ch <- "msg"
	}()
	select {
	case m := <-ch:
		fmt.Println("got:", m)
	case <-time.After(50 * time.Millisecond):
		fmt.Println("timed out")
	}
}

func runAdvancedDemo() {
	// Embedded struct.
	d := DogA{AnimalBase: AnimalBase{name: "Rex"}, breed: "collie"}
	fmt.Println(d.Speak())

	// Producer/consumer.
	ch := make(chan int)
	go producerAdv(ch)
	consumerAdv(ch)

	// Recursion with defer.
	recursiveAdv(3)

	// select / timeout.
	selectWithTimeout()

	// Stdlib use.
	r, _ := rand.Int(rand.Reader, big.NewInt(100))
	fmt.Println("random:", r)
}

// --- Generic function (type parameters).
func MapG[T, U any](xs []T, f func(T) U) []U {
	out := make([]U, 0, len(xs))
	for _, x := range xs {
		out = append(out, f(x))
	}
	return out
}

// --- Constraint interface with type-set / approximation elements.
type OrderedG interface {
	~int | ~int64 | ~float64 | ~string
}

func MaxG[T OrderedG](a, b T) T {
	if a > b {
		return a
	}
	return b
}

// --- Generic type with methods.
type StackG[T any] struct {
	items []T
}

func (s *StackG[T]) Push(v T) {
	s.items = append(s.items, v)
}

func (s *StackG[T]) Pop() (T, bool) {
	var zero T
	if len(s.items) == 0 {
		return zero, false
	}
	v := s.items[len(s.items)-1]
	s.items = s.items[:len(s.items)-1]
	return v, true
}

func (s *StackG[T]) Len() int {
	return len(s.items)
}

// --- Demo that touches each generic above.
func runGenericsDemo() {
	doubled := MapG([]int{1, 2, 3}, func(i int) int { return i * 2 })
	fmt.Println("MapG:", doubled)

	fmt.Println("MaxG:", MaxG("apple", "banana"))

	var stk StackG[string]
	stk.Push("a")
	stk.Push("b")
	if v, ok := stk.Pop(); ok {
		fmt.Println("popped:", v, "remaining:", stk.Len())
	}
}
