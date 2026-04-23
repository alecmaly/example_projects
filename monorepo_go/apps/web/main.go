package main

import (
	"fmt"

	// Standard named import.
	"mono/shared"
	// Aliased import.
	u "mono/utils"
	// Blank import — triggers package init() for side effects.
	_ "mono/utils"
	// Dot import — brings every exported symbol from the package into
	// the current file's namespace. Rare and controversial, but valid.
	. "mono/shared"
)

func main() {
	user := User{ID: 1, Name: "alice"}                        // via dot-import
	fmt.Println(shared.FormatUser(user), shared.DefaultRole)  // via named import
	fmt.Println("tag:", u.Tag, "clamped:", u.Clamp(42, 0, 10))

	// Ported coverage from the flat go/ fixture.
	runFeatureDemo()
	runScopeDemo()
	importsDemo()
	runAdvancedDemo()
	runCastsDemoGo()

	// T1 transitive chain: VALUE_ALIAS flows through 3 packages.
	deep, _ := importChainDeep()
	fmt.Println("transitive:", deep)

	// Cycle: Alpha ↔ Bravo (same package, different files).
	fmt.Println("cycle:", kickOffCycle())
}

// Isolated accessor so casts.go doesn't need to import chain packages
// into its top-level import block.
func importChainDeep() (string, error) {
	// separate indirection to keep flat package-level imports tidy
	return chainDeepValue(), nil
}
