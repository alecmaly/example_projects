package package1

import "fmt"

type ID string

var (
	// Simnet is a simulated network for very simple testing of individual binaries.
	// It is a single binary with mocked clients (no networking).
	Simnet ID = "simnet" // Single binary with mocked clients (no network)

	// Devnet is the most basic single-machine deployment of the Omni cross chain protocol.
	// It uses docker compose to setup a network with multi containers.
	// E.g. 2 geth nodes, 4 halo validators, a relayer, and 2 anvil rollups.
	Devnet ID = "devnet"
)

var Package1Var = "I'm a package-level variable in package1"

type BaseStruct struct {
	baseVar string
}

func NewBaseStruct() *BaseStruct {
	return &BaseStruct{baseVar: "I'm a base struct variable"}
}

func (s *BaseStruct) BaseMethod() {
	fmt.Println("This is BaseMethod from BaseStruct")
	fmt.Println("Base var:", s.baseVar)
	Package1Var = "sdfd"
}

type DerivedStruct struct {
	BaseStruct
	derivedVar string
}

func NewDerivedStruct() *DerivedStruct {
	return &DerivedStruct{
		BaseStruct: BaseStruct{baseVar: "I'm a base struct variable"},
		derivedVar: "I'm a derived struct variable",
	}
}

func (s *DerivedStruct) BaseMethod() {
	s.BaseStruct.BaseMethod()
	fmt.Println("This is an overridden method in DerivedStruct")
}

func (s *DerivedStruct) DerivedMethod() {
	fmt.Println("This is DerivedMethod from DerivedStruct")
	fmt.Println("Derived var:", s.derivedVar)
	s.BaseMethod()
}
