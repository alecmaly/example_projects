package main

import (
	"fmt"

	"mono/shared"
)

func main() {
	fmt.Println(shared.FormatUser(shared.User{ID: 99, Name: "cli-user"}))
}
