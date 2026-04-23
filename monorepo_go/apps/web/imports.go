package main

import (
	// 1. Stdlib plain.
	"fmt"

	// 2. Multi-line group.
	"strconv"
	"strings"

	// 3. Renamed (aliased).
	unicodeutf8 "unicode/utf8"

	// 4. Blank — runs package init() for side effects.
	_ "mono/utils"

	// 5. Intra-monorepo.
	"mono/shared"

	// 6. Dot import (controversial but legal). Commented to avoid
	//    name pollution in this package; shape-visible.
	// . "mono/shared"
)

func importsDemo() {
	_ = unicodeutf8.RuneLen('a')
	fmt.Println(strings.ToUpper("hi"), strconv.Itoa(42))
	fmt.Println(shared.FormatUser(shared.User{ID: 1, Name: "i"}))
}
