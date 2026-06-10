## Exploration: Project Structure Architecture Review

### Current State

The project is in **greenfield / pre-development phase** — no production code exists. The entire artifact set consists of:

- **Planning docs** (11 files): PRD, vision, architecture, bounded contexts, domain model, event storming, API standards, database strategy/standards, coding standards, development principles, ADR template
- **Module specs** (5 files): Users, Customers, Sales/Invoice, Inventory, Accounting — **all are empty**
- **Root files**: `AGENTS.md` (AI assistant rules), `erp.md` (user stories + high-level arch), `helpers.md` (trivial template)
- **SDD artifacts**: `openspec/config.yaml` (init completed), `.atl/skill-registry` files
- **Tech stack**: FastAPI + PostgreSQL + SQLAlchemy + Flyway backend, React + TypeScript + Vite frontend

The documentation is aspirational and establishes useful direction, but contains inconsistencies, gaps, and placeholder content that must be resolved before coding begins.

### Affected Areas

- `AGENTS.md` — Defines project rules for AI assistants; source of bounded context list
- `erp.md` — Contains conflicting module breakdown and business rules that should be in specs
- `docs/architecture.md` — States stack but contradicts itself and `coding-standards.md` on architecture style
- `docs/bounded-context.md` — Only covers 3 of 6–7 listed contexts
- `docs/domain-model.md` — Several entities are headings with no content
- `docs/event-storming.md` — Skeletal — only event names, no commands/aggregates/boundaries
- `docs/api-standards.md` — Empty (frontmatter only)
- `docs/database-standards.md` — Empty (frontmatter only)
- `docs/coding-standards.md` — Declares "Clean Architecture + DDD + Vertical Slice" simultaneously, which is contradictory
- `docs/development-principles.md` — Strong principles but not referenced/enforced elsewhere
- `docs/adr-template.md` — Template exists but zero ADRs written
- `docs/modules/users/user-spec-v1.md` — Empty file
- `docs/modules/customers/customer-spec-v1.md` — Empty file
- `docs/modules/sales/invoice-spec-v1.md` — Empty file
- `docs/modules/inventory/inventory-spec-v1.md` — Empty file
- `docs/modules/accounting/accounting-spec-v1.md` — Empty file
- `openspec/config.yaml` — All testing infrastructure marked unavailable

### Improvement Opportunities

1. **Resolve Architecture Contradiction (Clean/Hexagonal vs Vertical Slice)**
   - **Impact**: High — foundational decisions affect every line of code written
   - **Effort**: Low
   - **Suggestion**: `coding-standards.md` declares Clean Architecture + DDD + Vertical Slice Architecture simultaneously. Clean Arch and Hexagonal Arch are compatible (both enforce dependency inversion and domain isolation). Vertical Slice is *incompatible* with layer-first architectures — it organizes by feature, collapsing the layered split. Choose: **Hexagonal Architecture with DDD** (as stated in `AGENTS.md` and `development-principles.md`). Drop Vertical Slice from `coding-standards.md`. Hexagonal gives clear ports/adapters separation, which maps cleanly to the bounded context design.

2. **Reconcile Bounded Context Definitions — There Are Three Different Versions**
   - **Impact**: High — if contexts aren't aligned, module boundaries and team ownership will conflict
   - **Effort**: Low
   - **Suggestion**: `AGENTS.md` lists 6 contexts (Sales, Inventory, Accounting, Banking, HR, Purchasing). `erp.md` lists 7 (IAM, CRM, Inventory, Sales, Purchasing, Accounting, Reports). `bounded-context.md` only defines 3 (CRM, Sales, Accounting). Create **one canonical list** in `bounded-context.md` that reconciles all sources. Recommended canonical set: **IAM** (Users/Roles), **CRM** (Customers/Contacts), **Sales** (Quotes/Orders/Invoices), **Inventory** (Products/Stock/Warehouses), **Purchasing** (Vendors/Purchase Orders), **Accounting** (Journal/Ledger/AR/AP), **Banking** (Transactions/Reconciliation), **HR** (Employees/Payroll). Update `AGENTS.md` to reference `bounded-context.md` as the single source of truth.

3. **Fill All Empty Module Specs — Largest Risk to Development**
   - **Impact**: Critical — without specs, development has no requirements to validate against
   - **Effort**: High
   - **Suggestion**: All 5 module specs are empty files. Before writing any code, at minimum the **Customer** and **Invoice** specs need to be written (they're the core transaction flow). Leverage the scenarios already sketched in `erp.md` (the "Spec-Driven Development" section has customer endpoints) and the business rules (invoice uniqueness, immutability after posting, automatic accounting entry). Use the SDD pipeline: write specs per bounded context as delta specs under `openspec/specs/`, then code. The `erp.md` "Spec-Driven Development" section at the bottom is a good starting prototype — formalize it into proper specs.

4. **Define Cross-Cutting Concerns That Are Currently Missing**
   - **Impact**: High — these affect every module and are harder to retrofit
   - **Effort**: Medium
   - **Suggestion**: The following concerns have zero documentation:
     - **Error handling strategy**: Standardized error response format, exception hierarchy, validation error format
     - **Logging / Observability**: Structured logging format, correlation IDs, metric collection, distributed tracing
     - **Security beyond Auth0**: CORS policy, rate limiting, input sanitization, audit logging for sensitive operations
     - **Transaction management**: Unit of Work pattern scope, when to use DB transactions vs eventual consistency across contexts
     - **Concurrency**: Optimistic locking strategy for entities (e.g., invoices must not have double-posting), version columns
     - **Compliance**: Tax regulations (FEL for Guatemala mentioned in `erp.md`), data retention, GDPR if applicable
     - **Multi-tenancy**: `vision.md` says "multi-tenant ready" but no document defines how (schema-per-tenant? column-based? separate DB?)
     - Address these in **new docs** or **ADRs** before implementation begins.

5. **Set Up Testing and CI Infrastructure Before Coding**
   - **Impact**: Medium — not critical for first module but will cause pain if deferred
   - **Effort**: Medium
   - **Suggestion**: `openspec/config.yaml` shows all testing infrastructure unavailable. Define:
     - Test runner: pytest with async support (`pytest-asyncio`)
     - Test layers: unit (domain logic, no DB), integration (repository against test DB), e2e (API contracts)
     - CI: GitHub Actions workflow file (`.github/workflows/ci.yml`) with lint (ruff), type-check (mypy/pyright), test, and coverage steps
     - Docker Compose for local dev with PostgreSQL test database
     - Database test strategy: Flyway migrations run on test DB, `pytest` with `--reuse-db` for speed
     - This should be one of the first "implementation" tasks, even before business logic

### Recommendation

**The project is NOT ready to start coding business logic yet.** The foundation documents have too many contradictions and gaps. Proceed in this order:

1. **Immediate (before any code)**: Canonicalize bounded contexts, resolve architecture contradiction, and write the Customer + Invoice module specs (these are the first modules to build).
2. **Next (first implementation sprint)**: Set up project scaffolding — FastAPI project structure with Hexagonal layout per bounded context, Flyway migration setup, Docker Compose, CI pipeline, test infrastructure, and the cross-cutting concern foundations (error handling, logging, security middleware).
3. **Then**: Begin implementing the first bounded context (Customers/CRM) with full testing.

### Risks

- **Architecture confusion risk**: Developers reading `coding-standards.md` will be uncertain whether to organize code by layers (Clean/Hexagonal) or by features (Vertical Slice). This produces inconsistent code from day one.
- **Empty specs risk**: Starting to code without filled specs means the acceptance criteria are undefined. Code written without spec validation will be informally verified at best, producing unpredictable quality.
- **Missing cross-cutting concerns risk**: Auth, error handling, logging, and transaction management will be bolted on inconsistently per module if not defined upfront, creating technical debt from the first PR.
- **Boundary misalignment risk**: Building a module that turns out to be in the wrong bounded context (e.g., Customer entity needed by both CRM and Sales) will cause wasteful refactoring. The context map needs to be explicit about shared kernels and upstream/downstream relationships.

### Ready for Proposal

Yes — the exploration provides enough insight to create a structured proposal for improvements. The first proposal should focus on reconciling the architecture foundation and filling critical spec gaps before any code is written.
