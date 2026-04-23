// ASP.NET Core + EF Core framework idioms: controller attributes, route
// templates, action filters, DI via ctor, DbContext + DbSet<>, LINQ query.
//
// Using directives mirror real projects; they don't need to resolve for
// static analysis of attribute + routing shapes.
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace Mono.Web.AspNet;

public class UserEntity
{
    public int Id { get; set; }
    [Required]
    [StringLength(128)]
    public string Email { get; set; } = string.Empty;
    public string? Name { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }
    public DbSet<UserEntity> Users => Set<UserEntity>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<UserEntity>()
            .HasIndex(u => u.Email)
            .IsUnique();
    }
}

public record CreateUserRequest([Required] string Email, string? Name);

[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class UsersController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly ILogger<UsersController> _log;

    public UsersController(AppDbContext db, ILogger<UsersController> log)
    {
        _db = db;
        _log = log;
    }

    [HttpGet("{id:int}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<UserEntity>> Get(int id)
    {
        var user = await _db.Users.FirstOrDefaultAsync(u => u.Id == id);
        return user is null ? NotFound() : Ok(user);
    }

    [HttpGet]
    [AllowAnonymous]
    public async Task<ActionResult<IEnumerable<UserEntity>>> List(
        [FromQuery] int limit = 10,
        [FromQuery] string? search = null)
    {
        var q = _db.Users.AsQueryable();
        if (!string.IsNullOrEmpty(search))
            q = q.Where(u => u.Email.Contains(search));
        var users = await q.Take(limit).ToListAsync();
        return Ok(users);
    }

    [HttpPost]
    [Authorize(Roles = "admin")]
    public async Task<ActionResult<UserEntity>> Create([FromBody] CreateUserRequest req)
    {
        var user = new UserEntity { Email = req.Email, Name = req.Name };
        _db.Users.Add(user);
        await _db.SaveChangesAsync();
        _log.LogInformation("created user {Id}", user.Id);
        return CreatedAtAction(nameof(Get), new { id = user.Id }, user);
    }

    [HttpDelete("{id:int}")]
    [Authorize(Policy = "CanDeleteUser")]
    public async Task<IActionResult> Delete(int id)
    {
        var user = await _db.Users.FindAsync(id);
        if (user is null) return NotFound();
        _db.Users.Remove(user);
        await _db.SaveChangesAsync();
        return NoContent();
    }
}
