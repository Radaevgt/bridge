# Tailwind CSS Bridge Design System Skill

> Trigger: styling, UI components, layout, responsive design, colors

## Color Tokens — USE EXACTLY THESE

| Token            | Value    | Tailwind Class        | Usage                          |
|------------------|----------|-----------------------|--------------------------------|
| Primary          | #1A56DB  | `text-primary`, `bg-primary` | Buttons, links, active states |
| Primary light    | #EBF2FF  | `bg-primary-light`    | Card backgrounds, badges       |
| Primary dark     | #1E3A5F  | `text-primary-dark`   | Headings, important text       |
| White            | #FFFFFF  | `bg-white`            | Page bg, cards                 |
| Gray-50          | #F9FAFB  | `bg-gray-50`          | Subtle section backgrounds     |
| Text primary     | #111827  | `text-text-primary`   | Body text                      |
| Text secondary   | #6B7280  | `text-text-secondary` | Labels, hints, meta            |
| Border           | #E5E7EB  | `border-border`       | Dividers, card borders         |
| Error            | #EF4444  | `text-error`          | Validation errors              |
| Success          | #10B981  | `text-success`        | Available badge, success       |

## Component Patterns

### Card
```jsx
<div className="bg-white border border-border rounded-lg p-5 hover:shadow-md transition-shadow">
  <h3 className="text-lg font-semibold text-primary-dark">Title</h3>
  <p className="text-sm text-text-secondary mt-1">Description</p>
</div>
```

### Button (Primary)
```jsx
<button className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50">
  Action
</button>
```

### Button (Secondary)
```jsx
<button className="border border-primary text-primary px-4 py-2 rounded-lg hover:bg-primary-light transition-colors">
  Secondary
</button>
```

### Badge (Available)
```jsx
<span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-success">
  Available
</span>
```

### Badge (Busy)
```jsx
<span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-700">
  Busy
</span>
```

### Input Field
```jsx
<input
  type="text"
  className="w-full border border-border rounded-lg px-4 py-2 text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
  placeholder="Search..."
/>
```

### Validation Error
```jsx
{errors.field && (
  <p className="text-error text-sm mt-1">{errors.field.message}</p>
)}
```

### Loading Skeleton
```jsx
<div className="animate-pulse">
  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
  <div className="h-4 bg-gray-200 rounded w-1/2" />
</div>
```

### Empty State
```jsx
<div className="text-center py-12">
  <p className="text-text-secondary text-lg mb-4">No results found</p>
  <button className="bg-primary text-white px-4 py-2 rounded-lg">
    Try a different search
  </button>
</div>
```

## Rules — ABSOLUTE
- **NO custom CSS files** — Tailwind classes only
- **NO inline styles** — no `style={{}}` ever
- **NO arbitrary values** unless truly needed — prefer design tokens
- Use `rounded-lg` for cards/buttons, `rounded-full` for badges/avatars
- Responsive: `sm:`, `md:`, `lg:` breakpoints when needed
- Spacing: `p-4`/`p-5`/`p-6` for cards, `gap-4` for flex/grid layouts
