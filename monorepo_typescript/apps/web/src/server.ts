// Backend framework idioms: Express-style middleware chain, NestJS-style
// decorator-driven controller, Zod schema validation, Prisma-style ORM.
//
// Imports mirror real projects; they are not expected to resolve for
// static analysis of decorator + routing shapes.
import express, { NextFunction, Request, Response, Router } from "express";
import { z } from "zod";
import { Body, Controller, Get, Post, Param, Query, UseGuards } from "@nestjs/common";
import { PrismaClient } from "@prisma/client";

// --- Zod schema ---
const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().max(128).optional(),
});
type CreateUserDto = z.infer<typeof CreateUserSchema>;

// --- Prisma client (singleton) ---
const prisma = new PrismaClient();

// --- middleware: logging ---
function withLogging(req: Request, res: Response, next: NextFunction): void {
  const start = Date.now();
  res.on("finish", () => {
    console.log(`${req.method} ${req.url} ${res.statusCode} ${Date.now() - start}ms`);
  });
  next();
}

// --- middleware: auth ---
function requireAuth(req: Request, res: Response, next: NextFunction): void {
  const token = req.headers.authorization;
  if (!token) {
    res.status(401).json({ error: "unauthorized" });
    return;
  }
  (req as Request & { userId: number }).userId = 1;
  next();
}

// --- Express-style router ---
export const usersRouter: Router = express.Router();

usersRouter.get("/:id", async (req: Request, res: Response) => {
  const id = Number(req.params.id);
  const user = await prisma.user.findUnique({ where: { id } });
  if (!user) return res.status(404).json({ error: "not found" });
  res.json(user);
});

usersRouter.get("/", async (req: Request, res: Response) => {
  const limit = Math.min(Number(req.query.limit ?? 10), 100);
  const search = typeof req.query.search === "string" ? req.query.search : undefined;
  const users = await prisma.user.findMany({
    where: search ? { email: { contains: search } } : undefined,
    take: limit,
  });
  res.json(users);
});

usersRouter.post("/", requireAuth, async (req: Request, res: Response) => {
  const parsed = CreateUserSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ errors: parsed.error.issues });
  const user = await prisma.user.create({ data: parsed.data });
  res.status(201).json(user);
});

// --- Express app wiring ---
export function buildApp() {
  const app = express();
  app.use(express.json());
  app.use(withLogging);
  app.use("/api/users", usersRouter);
  app.get("/health", (_req, res) => res.send("ok"));
  return app;
}

// --- NestJS-style (decorator-driven) alternative ---
class AuthGuard {
  canActivate(req: Request): boolean {
    return Boolean(req.headers.authorization);
  }
}

@Controller("api/users")
export class UsersController {
  constructor(private readonly db: PrismaClient = prisma) {}

  @Get(":id")
  async get(@Param("id") id: string) {
    const user = await this.db.user.findUnique({ where: { id: Number(id) } });
    if (!user) throw new Error("not found");
    return user;
  }

  @Get()
  async list(@Query("limit") limit = "10") {
    return this.db.user.findMany({ take: Math.min(Number(limit), 100) });
  }

  @Post()
  @UseGuards(AuthGuard)
  async create(@Body() dto: CreateUserDto) {
    return this.db.user.create({ data: dto });
  }
}
