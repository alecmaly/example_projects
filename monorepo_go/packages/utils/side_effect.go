package utils

import "fmt"

// init() runs when the package is imported — even via blank import.
// Exercises the `import _ "mono/utils"` side-effect pattern.
func init() {
	fmt.Println("[utils] init() registered")
}
