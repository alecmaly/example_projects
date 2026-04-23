package shared

import "fmt"

type User struct {
	ID   int
	Name string
}

type Role string

const (
	Admin Role = "admin"
	User_ Role = "user"   // trailing underscore to avoid colliding with type
	Guest Role = "guest"
)

var DefaultRole = User_

func FormatUser(u User) string {
	return fmt.Sprintf("%d:%s", u.ID, u.Name)
}
