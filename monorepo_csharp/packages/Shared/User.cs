namespace Mono.Shared;

public record User(int Id, string Name);

public enum Role { Admin, User, Guest }

public static class Defaults
{
    public const Role DEFAULT_ROLE = Role.User;
}
