package main

// C1.b — cycle partner for cycle_a.go.

type Bravo struct {
	tag   string
	owner *Alpha                          // C1.b.type_ref → cycle_a.go
}

func newBravo(tag string) *Bravo        { return &Bravo{tag: tag} }

func (b *Bravo) bounceToAlpha() string {
	return newAlpha("bounce-from-" + b.tag).describe()
}
