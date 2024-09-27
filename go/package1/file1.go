package package1

import "fmt"

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