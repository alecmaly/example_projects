package main

import (
	"context"
	"encoding/json"
	"fmt"
	"time"
)

// Struct tags — encoding hints on fields.
type UserF struct {
	ID       int    `json:"id"`
	Name     string `json:"name"`
	Password string `json:"-"`
	Email    string `json:"email,omitempty"`
}

// Embedded interface composition.
type FReader interface {
	Read() string
}
type FWriter interface {
	Write(s string)
}
type FReadWriter interface {
	FReader
	FWriter
}

type InMemoryF struct {
	buf string
}

func (m *InMemoryF) Read() string   { return m.buf }
func (m *InMemoryF) Write(s string) { m.buf = s }

func describeF(x any) string {
	switch v := x.(type) {
	case nil:
		return "nil"
	case int:
		return fmt.Sprintf("int=%d", v)
	case string:
		return fmt.Sprintf("string len=%d", len(v))
	case []byte:
		return fmt.Sprintf("bytes len=%d", len(v))
	case fmt.Stringer:
		return fmt.Sprintf("stringer: %s", v.String())
	default:
		return fmt.Sprintf("other %T", v)
	}
}

func doWorkF(ctx context.Context, label string) error {
	select {
	case <-time.After(50 * time.Millisecond):
		fmt.Println("work done:", label)
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

func runFeatureDemo() {
	u := UserF{ID: 1, Name: "alice", Password: "secret", Email: ""}
	b, _ := json.Marshal(u)
	fmt.Println("json:", string(b))

	var rw FReadWriter = &InMemoryF{}
	rw.Write("hello")
	fmt.Println("read:", rw.Read())

	for _, v := range []any{nil, 42, "hi", []byte{1, 2, 3}, time.Now()} {
		fmt.Println(describeF(v))
	}

	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Millisecond)
	defer cancel()
	if err := doWorkF(ctx, "ctx-demo"); err != nil {
		fmt.Println("doWork error:", err)
	}
}
