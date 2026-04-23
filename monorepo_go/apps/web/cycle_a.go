package main

// C1.a — file-level cycle within the `main` package.
// Go forbids cycles at the PACKAGE level; within a single package,
// files can reference each other freely because they're compiled as
// one translation unit.

type Alpha struct {
	name  string
	child *Bravo                       // C1.a.type_ref → defined in cycle_b.go
}

func newAlpha(name string) *Alpha    { return &Alpha{name: name} }
func (a *Alpha) describe() string    { return "Alpha(" + a.name + ")" }

func (a *Alpha) spawnBravo() *Bravo {
	return newBravo(a.name + "/b")
}

func kickOffCycle() string {
	a := newAlpha("root")
	b := a.spawnBravo()
	return b.bounceToAlpha()
}
