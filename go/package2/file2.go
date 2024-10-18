package package2

import "fmt"

const Package2Constant = "I'm a constant in package2"

var Package2Var = "I'm a package-level variable in package2"

func Function1() {
	fmt.Println("This is Function1 from package2")
	fmt.Println("Accessing package constant:", Package2Constant)
	internalFunction()
}

func AnotherFunc(s string) (string, bool) {
	return s, true
}

func internalFunction() {
	localVar := "I'm local to internalFunction"
	fmt.Println("This is an internal function in package2")
	fmt.Println("Local var:", localVar)
	fmt.Println("Package var:", Package2Var)
}
