package scopes_ns

type Widget struct {                          // S14.Widget.def
	Label string
}

func NewWidget(label string) *Widget {
	return &Widget{Label: label}
}
