package main

// Labeled scope test cases for Go — monorepo edition.
// Ported from go/scopes.go. Cross-package refs target the sibling
// workspace modules `mono/shared` / `mono/utils` / `mono/scopes_ns`.

import (
	"fmt"

	sharedAlias "mono/shared"                     // S09.def — package alias
	nsw "mono/scopes_ns"                           // S14.import
)

// --------------------------------------------------------------------- S04 def / S05 write target
var moduleVar = "mod-initial"                      // S04.def

func sS01Local() {
	localA := "S01.local"                          // S01.def
	fmt.Println(localA)                            // S01.read
}

func sS02ClosureRead() {
	outerA := "S02.outer"                          // S02.outer.def
	inner := func() { fmt.Println(outerA) }        // S02.inner.read
	inner()
}

func sS03ClosureWrite() int {
	counter := 0                                    // S03.outer.def
	bump := func() { counter++ }                    // S03.inner.write
	bump(); bump()
	return counter                                  // S03.outer.read
}

func sS05SameModuleWrite() {
	moduleVar = "rotated"                           // S05.write
	fmt.Println(moduleVar)                          // S05.read
}

func sS06CrossRead() string {
	return string(sharedAlias.DefaultRole)          // S06.read via alias
}

func sS07CrossWrite() {
	sharedAlias.DefaultRole = "S07"                 // S07.write via alias (alias kept for S09 too)
}

func sS08Shadowing() {
	moduleVar := "shadowed"                         // S08.shadow.def
	fmt.Println(moduleVar)                          // S08.shadow.read
}

// Struct embedding stands in for S13 inherited field.
type ScopeBase struct {
	X int                                           // S11.instance.def + S13.base.def
}

func (b ScopeBase) ReadInstance(x int) int {
	return x + b.X                                  // S11.param.read + S11.instance.read
}

type ScopeDerived struct {
	ScopeBase                                       // embedded
	Y int
}

func sS13() int {
	d := ScopeDerived{ScopeBase: ScopeBase{X: 7}, Y: 1}
	return d.X                                      // S13.derived.read
}

func sS14Qualified() string {
	return nsw.NewWidget("hi").Label                // S14.read
}

func runScopeDemo() {
	sS01Local()
	sS02ClosureRead()
	fmt.Println(sS03ClosureWrite())
	sS05SameModuleWrite()
	fmt.Println(sS06CrossRead())
	sS07CrossWrite()
	sS08Shadowing()
	fmt.Println(ScopeBase{X: 10}.ReadInstance(100))
	fmt.Println(sS13())
	fmt.Println(sS14Qualified())
}
