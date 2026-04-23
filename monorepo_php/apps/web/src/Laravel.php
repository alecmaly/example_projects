<?php
// Laravel framework idioms: Eloquent model, Request form-request,
// controller extending Controller, route-level attributes (PHP 8),
// middleware, facades, service provider.
//
// Not expected to resolve the vendor classes — this fixture is for
// static-analysis of Laravel-shaped code.
namespace Mono\Web\Laravel;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Routing\Controller;
use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\ServiceProvider;

// --- Eloquent model ---
class LaravelUser extends Model
{
    protected $table = "users";
    protected $fillable = ["email", "name", "organization_id"];
    protected $hidden  = ["password"];
    protected $casts = [
        "email_verified_at" => "datetime",
        "settings"          => "array",
    ];

    public function posts(): HasMany {
        return $this->hasMany(LaravelPost::class, "author_id");
    }

    public function organization(): BelongsTo {
        return $this->belongsTo(LaravelOrganization::class);
    }

    public function scopeActive($q) {
        return $q->whereNull("archived_at");
    }
}

class LaravelPost extends Model {}
class LaravelOrganization extends Model {}

// --- FormRequest for validation ---
class CreateUserRequest extends FormRequest
{
    public function authorize(): bool { return $this->user() !== null; }

    public function rules(): array
    {
        return [
            "email" => ["required", "email", "unique:users,email"],
            "name"  => ["nullable", "string", "max:128"],
        ];
    }
}

// --- Controller ---
class LaravelUserController extends Controller
{
    public function __construct()
    {
        $this->middleware("auth");
        $this->middleware("throttle:60,1")->only(["store"]);
    }

    public function index(Request $request): JsonResponse
    {
        $limit = (int) $request->query("limit", 10);
        $users = LaravelUser::active()
            ->orderByDesc("created_at")
            ->limit($limit)
            ->get();
        return response()->json($users);
    }

    public function show(int $id): JsonResponse
    {
        $user = LaravelUser::findOrFail($id);
        return response()->json($user);
    }

    public function store(CreateUserRequest $req): JsonResponse
    {
        $user = DB::transaction(function () use ($req) {
            return LaravelUser::create($req->validated());
        });
        return response()->json($user, 201);
    }

    public function destroy(int $id): JsonResponse
    {
        $user = LaravelUser::findOrFail($id);
        $user->delete();
        return response()->json(null, 204);
    }
}

// --- Routes (normally in routes/api.php) ---
Route::prefix("api")->middleware(["api"])->group(function () {
    Route::get   ("/users",      [LaravelUserController::class, "index"]);
    Route::get   ("/users/{id}", [LaravelUserController::class, "show"])->whereNumber("id");
    Route::post  ("/users",      [LaravelUserController::class, "store"]);
    Route::delete("/users/{id}", [LaravelUserController::class, "destroy"]);
});

// --- Service provider (container registration) ---
class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->singleton(LaravelUserController::class, function ($app) {
            return new LaravelUserController();
        });
    }

    public function boot(): void
    {
        // bootstrap logic
    }
}
