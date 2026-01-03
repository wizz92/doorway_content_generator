# Coding Standards & Architecture Guidelines

## General Principles

### 1. Code Quality
- **DRY (Don't Repeat Yourself)**: Extract common logic into reusable functions/utilities
- **KISS (Keep It Simple, Stupid)**: Prefer simple, readable solutions over clever ones
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **Fail Fast**: Validate inputs early, throw meaningful errors immediately

### 2. Naming Conventions

**Backend (Python):**
- Classes: `PascalCase` (e.g., `UserRepository`, `JobService`)
- Functions/Variables: `snake_case` (e.g., `get_user_by_id`, `max_keywords`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_ATTEMPTS`)
- Private: Prefix with `_` (e.g., `_internal_method`)
- Type hints: Always use type hints for function parameters and return values

**Frontend (TypeScript/React):**
- Components: `PascalCase` (e.g., `JobCard`, `LoginForm`)
- Functions/Variables: `camelCase` (e.g., `fetchJobs`, `isLoading`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)
- Interfaces/Types: `PascalCase` with descriptive names (e.g., `JobStatus`, `ApiResponse`)
- Hooks: Prefix with `use` (e.g., `useJobs`, `useAuth`)

### 3. File Organization

**Backend Structure:**
```
app/
  api/          # API routes and endpoints
  models/       # Database models (SQLAlchemy)
  schemas/      # Pydantic schemas for validation
  services/     # Business logic
  repositories/ # Data access layer
  middleware/   # Request/response middleware
  exceptions/   # Custom exceptions and handlers
  utils/        # Utility functions
```

**Frontend Structure:**
```
src/
  components/   # Reusable UI components (grouped by feature)
  pages/        # Page-level components
  services/     # API clients and external services
  hooks/        # Custom React hooks
  context/      # React context providers
  types/        # TypeScript type definitions
  utils/        # Utility functions
  theme/        # Theme configuration
```

### 4. Backend Standards (Python/FastAPI)

**Imports:**
- Group imports: stdlib, third-party, local (separated by blank line)
- Use absolute imports: `from app.services.job_service import JobService`
- Avoid wildcard imports (`from module import *`)

**Functions:**
- Maximum 50 lines per function
- Single responsibility per function
- Use async/await for I/O operations
- Always include docstrings for public functions
- Type hints required for all function signatures

**Error Handling:**
- Use custom exception classes inheriting from base exceptions
- Return appropriate HTTP status codes (400, 401, 403, 404, 500)
- Log errors with context (user_id, job_id, etc.)
- Never expose internal errors to clients

**Database:**
- Use repositories for all database access (no direct ORM in routes)
- Transactions for multi-step operations
- Use connection pooling
- Index frequently queried columns

**API Design:**
- RESTful endpoints: `/api/v1/resource/{id}`
- Use Pydantic schemas for request/response validation
- Version APIs: `/api/v1/`, `/api/v2/`
- Return consistent response format: `{data, error, message}`

**Example:**
```python
from typing import Optional
from fastapi import HTTPException, status
from app.schemas.job_schemas import JobCreate, JobResponse
from app.services.job_service import JobService

async def create_job(
    job_data: JobCreate,
    user_id: int,
    job_service: JobService = Depends()
) -> JobResponse:
    """Create a new job for the authenticated user."""
    try:
        job = await job_service.create_job(job_data, user_id)
        return JobResponse.from_orm(job)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

### 5. Frontend Standards (TypeScript/React)

**Components:**
- Functional components only (no class components)
- Maximum 200 lines per component
- Extract complex logic into custom hooks
- Use TypeScript interfaces for props
- Memoize expensive computations with `useMemo`
- Use `React.memo` for components that re-render frequently

**State Management:**
- Local state: `useState` for component-specific state
- Shared state: React Context for app-wide state
- Server state: Custom hooks with polling/caching
- Avoid prop drilling beyond 2-3 levels

**API Calls:**
- Centralize API calls in service files
- Use async/await, never mix with `.then()`
- Handle loading and error states
- Implement retry logic for failed requests
- Use proper TypeScript types for responses

**Styling:**
- Use theme provider for consistent styling
- Prefer CSS modules or styled-components over inline styles
- Responsive design: mobile-first approach
- Accessibility: semantic HTML, ARIA labels, keyboard navigation

**Example:**
```typescript
interface JobCardProps {
  job: Job;
  onStatusChange: (jobId: string, status: JobStatus) => void;
}

export const JobCard: React.FC<JobCardProps> = React.memo(({ job, onStatusChange }) => {
  const [isLoading, setIsLoading] = useState(false);
  
  const handleStatusUpdate = async (newStatus: JobStatus) => {
    setIsLoading(true);
    try {
      await updateJobStatus(job.id, newStatus);
      onStatusChange(job.id, newStatus);
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="job-card" role="article">
      {/* Component JSX */}
    </div>
  );
});
```

### 6. Security

**Backend:**
- Validate all inputs using Pydantic schemas
- Sanitize user inputs before database queries
- Use parameterized queries (SQLAlchemy handles this)
- Implement rate limiting for API endpoints
- Store secrets in environment variables, never in code
- Use HTTPS in production
- Implement proper authentication/authorization

**Frontend:**
- Never store sensitive data in localStorage
- Sanitize user inputs before rendering
- Validate forms on both client and server
- Use HTTPS for all API calls
- Implement CSRF protection
- Set secure cookie flags

### 7. Testing

**Backend:**
- Unit tests for services and utilities
- Integration tests for API endpoints
- Test coverage minimum: 80%
- Use pytest fixtures for test data
- Mock external dependencies (APIs, databases)

**Frontend:**
- Unit tests for utilities and hooks
- Component tests with React Testing Library
- Integration tests for critical user flows
- Test accessibility with jest-axe

### 8. Performance

**Backend:**
- Use async/await for I/O operations
- Implement database query optimization
- Use connection pooling
- Cache frequently accessed data
- Implement pagination for large datasets

**Frontend:**
- Code splitting with React.lazy()
- Lazy load images and heavy components
- Debounce/throttle user input handlers
- Optimize bundle size (tree shaking)
- Use React.memo and useMemo appropriately

### 9. Documentation

**Code Comments:**
- Explain "why", not "what" (code should be self-documenting)
- Docstrings for all public functions/classes
- Type hints serve as inline documentation

**API Documentation:**
- FastAPI auto-generates OpenAPI docs
- Add descriptions to all endpoints
- Document request/response schemas

**README:**
- Setup instructions
- Environment variables
- Running tests
- Deployment guide

### 10. Git & Version Control

- Meaningful commit messages: `feat: add job status polling`
- Branch naming: `feature/job-upload`, `fix/auth-bug`, `refactor/api-routes`
- Small, focused commits
- Review code before merging
- Use `.gitignore` for sensitive files and build artifacts

### 11. Code Review Checklist

- [ ] Code follows naming conventions
- [ ] Type hints/types are present and correct
- [ ] Error handling is implemented
- [ ] No hardcoded values (use config/constants)
- [ ] Tests are written and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Accessibility requirements met

---

**Remember:** Code is read more often than written. Prioritize clarity and maintainability over cleverness.

