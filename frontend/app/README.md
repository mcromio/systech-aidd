# LLM Dashboard Frontend

Dashboard for monitoring LLM assistant conversations and statistics.

Built with Next.js 15, React 19, TypeScript, and Tailwind CSS.

## Tech Stack

- **Framework:** Next.js 15 with App Router
- **Language:** TypeScript 5 (strict mode)
- **Styling:** Tailwind CSS 3
- **Components:** Radix UI primitives
- **Charts:** Recharts
- **Package Manager:** pnpm
- **Quality Tools:** ESLint, Prettier, TypeScript

## Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── page.tsx            # Home page (redirects to /dashboard)
│   ├── layout.tsx          # Root layout
│   ├── globals.css         # Global styles
│   └── dashboard/          # Dashboard route
│       └── page.tsx        # Dashboard page
├── components/
│   ├── ui/                 # shadcn/ui components
│   ├── layout/             # Layout components (Header, Footer)
│   └── dashboard/          # Dashboard-specific components
├── lib/
│   ├── api.ts              # API client
│   ├── types.ts            # TypeScript types
│   └── utils.ts            # Utility functions
├── hooks/                  # Custom React hooks
│   └── use-stats.ts        # Hook for fetching statistics
└── styles/
    └── globals.css         # Global styles + Tailwind
```

## Getting Started

### Prerequisites

- Node.js 18+ (or installed via nvm)
- pnpm 10+

### Installation

```bash
# Install dependencies
pnpm install

# Create .env.local (copy from .env.example)
cp .env.example .env.local
```

### Environment Variables

```env
# Mock API URL (local development)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Production API URL
# NEXT_PUBLIC_API_URL=https://api.example.com
```

## Development

### Start Dev Server

```bash
# Using pnpm directly
pnpm dev

# Using Makefile (from project root)
make fe-dev
```

The app will be available at [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
pnpm build
pnpm start
```

## Code Quality

### Linting

```bash
pnpm lint
```

Checks code style using ESLint with Next.js and TypeScript rules.

### Formatting

```bash
pnpm format
```

Formats code using Prettier with configured rules.

### Type Checking

```bash
pnpm type-check
```

Checks TypeScript types without emitting code.

### Full Quality Check

```bash
# Using Makefile
make fe-quality
```

## Makefile Commands

From project root:

```bash
# Installation
make fe-install          # Install dependencies

# Development
make fe-dev             # Start dev server
make fe-build           # Build for production
make fe-start           # Run production server

# Code Quality
make fe-lint            # Run ESLint
make fe-format          # Format code with Prettier
make fe-type-check      # Check TypeScript types
make fe-quality         # Run all quality checks
```

## API Integration

### Mock API

The dashboard connects to Mock Stats API (FE-S1):

- **Base URL:** `http://localhost:8000`
- **Endpoints:**
  - `GET /health` - Health check
  - `GET /api/v1/stats?period=day|week|month` - Get statistics

### Real API

When ready, update `NEXT_PUBLIC_API_URL` in `.env.local` to connect to production API.

## Architecture

### Component Structure

All components follow TypeScript best practices:

- **Type Safety:** Full type hints for all props
- **Client Components:** Use `"use client"` for interactive components
- **Server Components:** Used for static content and data fetching
- **Naming:** PascalCase for components, camelCase for functions

### Data Flow

1. Dashboard page uses `useStats` hook
2. Hook fetches data from API client
3. API client makes requests to Mock API
4. Data flows down to child components
5. Components render UI with Tailwind classes

### Styling Strategy

- **Tailwind CSS:** Utility-first approach
- **Responsive:** Mobile-first design with md/lg breakpoints
- **Colors:** Gray palette for neutral look
- **Spacing:** Consistent spacing using Tailwind scale

## Code Conventions

### Imports Order

```typescript
// 1. React/Next.js
import { useState } from "react";
import Link from "next/link";

// 2. External libraries
import { LineChart } from "recharts";

// 3. Internal components
import { Header } from "@/components/layout/header";

// 4. Internal utilities
import { apiClient } from "@/lib/api";

// 5. Types
import type { StatsResponse } from "@/lib/types";
```

### Component Template

```typescript
"use client";

import type { SomeType } from "@/lib/types";

interface ComponentProps {
  data: SomeType;
}

export function Component({ data }: ComponentProps): React.ReactNode {
  return <div>{/* JSX */}</div>;
}
```

### File Naming

- **Components:** `kebab-case.tsx` (e.g., `stats-cards.tsx`)
- **Files:** `kebab-case.ts` (e.g., `use-stats.ts`)
- **Directories:** `kebab-case` (e.g., `components/`)
- **Types/Interfaces:** `PascalCase` (e.g., `StatsResponse`)

## Performance

- **Code Splitting:** Automatic via Next.js
- **Image Optimization:** Via Next.js Image component
- **Font Optimization:** Via Next.js Font module
- **Bundle Size:** Minimal (only what's used)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Port 3000 Already in Use

```bash
# Kill the process on port 3000
lsof -ti:3000 | xargs kill -9

# Then restart
pnpm dev
```

### API Connection Error

1. Ensure Mock API is running: `make api-run`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS is enabled on API

### TypeScript Errors

```bash
# Clear cache and rebuild
rm -rf .next
pnpm type-check
pnpm dev
```

## Next Steps

- [FE-S3: Implement Dashboard](../doc/frontend-roadmap.md#fe-s3-dashboard-со-статистикой)
- [API Usage Guide](../doc/api-usage.md)
- [Dashboard Requirements](../doc/dashboard-requirements.md)

## Documentation

- [Frontend Vision](../doc/frontend-vision.md) - Technical vision and principles
- [ADR-001: Next.js Choice](../doc/adr/001-nextjs-choice.md)
- [ADR-002: shadcn/ui Choice](../doc/adr/002-shadcn-ui-choice.md)
- [ADR-003: pnpm Choice](../doc/adr/003-pnpm-choice.md)

## License

Part of LLM Assistant project.
