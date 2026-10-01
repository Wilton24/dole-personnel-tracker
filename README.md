# DOLE Personnel Tracker

Tracks Safety Officer / First Aider personnel and their assignment to projects,
enforcing that a person can't be on two Ongoing projects at once — unless an
admin overrides it (with a logged reason).

## Stack
- Frontend: React + TypeScript (Vite)
- Backend: FastAPI
- Database: PostgreSQL
- Fully dockerized

## Run it

```bash
cp .env.example .env
docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend API docs (Swagger): http://localhost:8000/docs
- Postgres: localhost:5432 (user: dole_user / pass: dole_pass / db: dole_tracker)

On first boot, the backend seeds:
- Roles: "Safety Officer", "First Aider"
- Admin user: username `admin`, password `admin123`

**Change the admin password before using this for anything real.** There's
no "change password" endpoint yet — for now you'd update it directly in the
database or via a one-off script using `hash_password()` from `app/security.py`.

## How the engagement rule works

- `personnel.status` isn't stored — it's computed live: a person is "Engaged"
  if they have an assignment on a project whose status is "Ongoing", otherwise
  "Available".
- Assigning an "Available" person to a project works normally.
- Assigning an "Engaged" person:
  - as a non-admin → rejected (409)
  - as an admin → allowed, but requires an `override_reason`, and the
    assignment is flagged `is_override = true` with `override_by` set to the
    admin's user id. This is visible in the project's assignment table.
- Marking a project "Completed" frees up everyone assigned to it (since status
  is computed from *Ongoing* projects only — no extra step needed).

## What's not built yet (left as next steps)
- Password change / user management UI (only the seeded admin exists)
- Alembic migrations (currently just `Base.metadata.create_all()` on startup —
  fine for a fresh dev DB, but you'll want Alembic once this is in real use
  and the schema needs to evolve without wiping data)
- Editing/removing roles from the UI (the API supports adding roles as admin;
  no delete endpoint yet)
- Tests
- Production-hardened CORS / secrets (currently permissive for local dev)

## Project structure

```
backend/
  app/
    main.py          FastAPI app, CORS, startup seeding
    models.py         SQLAlchemy models (Role, Personnel, Project, Assignment, User)
    schemas.py         Pydantic request/response models
    security.py        password hashing + JWT
    deps.py             auth dependencies (get_current_user, require_admin)
    utils.py            computed personnel status logic
    seed.py              default roles + admin user
    routers/
      auth.py, roles.py, personnel.py, projects.py, assignments.py
frontend/
  src/
    api.ts             axios client with JWT interceptor
    types.ts            shared TS types
    pages/               Login, Personnel, Projects, ProjectDetail
    components/           Navbar, StatusBadge
docker-compose.yml
```
