# Flight Tracker Frontend - Unified CSS Architecture

## Overview
The Flight Tracker frontend has been refactored to use a single, comprehensive CSS file (`index.css`) with CSS custom properties (variables) for consistent theming and styling throughout the application.

## 🎨 Architecture Benefits

### Before (Multiple CSS Files)
- `App.css` - App-specific styles
- `Settings.css` - Settings component styles  
- `Tracker.css` - Tracker page styles
- `Display.css` - Display component styles
- Inconsistent color schemes and spacing
- Difficult to maintain and update themes

### After (Unified CSS)
- Single `index.css` file with all styles
- CSS custom properties for theming
- Consistent design system
- Easy theme switching (light/dark/auto)
- Maintainable and scalable architecture

## 🏗️ CSS Structure

### 1. CSS Custom Properties (Variables)
All design tokens are defined as CSS variables in `:root`:

```css
:root {
  /* Theme Colors */
  --primary-color: #007bff;
  --success-color: #28a745;
  --danger-color: #dc3545;
  
  /* Spacing System */
  --spacing-xs: 5px;
  --spacing-sm: 10px;
  --spacing-md: 20px;
  --spacing-lg: 30px;
  --spacing-xl: 40px;
  
  /* Typography */
  --font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  
  /* Layout */
  --max-width: 1200px;
  --border-radius: 8px;
}
```

### 2. Theme Support
Built-in support for light, dark, and auto (system preference) themes:

```css
/* Light theme */
:root[data-theme="light"] {
  --bg-primary: #ffffff;
  --text-primary: #333333;
}

/* Dark theme */
:root[data-theme="dark"] {
  --bg-primary: #1a1a1a;
  --text-primary: #ffffff;
}

/* Auto theme (follows system) */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) {
    --bg-primary: #1a1a1a;
    --text-primary: #ffffff;
  }
}
```

### 3. Component Classes
Organized by component type with consistent naming:

```css
/* Navigation */
.navbar { /* styles */ }
.nav-container { /* styles */ }
.nav-link { /* styles */ }

/* Forms */
.form-group { /* styles */ }
.btn-primary { /* styles */ }
.btn-success { /* styles */ }

/* Cards */
.card { /* styles */ }
.flight-card { /* styles */ }
```

### 4. Utility Classes
Common utility classes for quick styling:

```css
.text-center { text-align: center; }
.mb-3 { margin-bottom: var(--spacing-md); }
.d-flex { display: flex; }
.w-100 { width: 100%; }
```

## 🛠️ Vite Configuration

Enhanced Vite config for CSS optimization and theme variables:

```typescript
export default defineConfig({
  plugins: [react()],
  css: {
    postcss: {
      plugins: [],
    },
  },
  define: {
    __THEME_COLORS__: {
      primary: '#007bff',
      success: '#28a745',
      warning: '#ffc107',
      danger: '#dc3545',
      info: '#17a2b8',
    },
  },
  build: {
    cssCodeSplit: false, // Bundle all CSS into one file
  },
})
```

## 🎯 Usage Guide

### Using CSS Variables in Components
```tsx
// Direct CSS variable usage
<div style={{ color: 'var(--primary-color)' }}>
  Primary colored text
</div>

// With the theme utility
import { theme } from '../theme';

<div style={{ color: theme.colors.primary }}>
  Primary colored text
</div>
```

### Using Predefined Classes
```tsx
// Button classes
<button className="btn btn-primary">Save</button>
<button className="btn btn-success">Start</button>
<button className="btn btn-danger">Stop</button>

// Layout classes
<div className="container">
  <div className="card card-secondary">
    <div className="d-flex justify-between align-center">
      Content
    </div>
  </div>
</div>

// Utility classes
<h1 className="text-center mb-4">Title</h1>
<div className="mt-3 p-2">Content</div>
```

### Theme Switching
```tsx
import { setTheme, getTheme } from '../theme';

// Get current theme
const currentTheme = getTheme(); // 'light' | 'dark' | 'auto'

// Set theme
setTheme('dark');
setTheme('light');
setTheme('auto'); // Follows system preference
```

## 🎨 Design System

### Color Palette
- **Primary**: `#007bff` (Blue) - Main actions, links
- **Success**: `#28a745` (Green) - Success states, positive actions
- **Warning**: `#ffc107` (Yellow) - Warnings, cautions
- **Danger**: `#dc3545` (Red) - Errors, destructive actions
- **Info**: `#17a2b8` (Cyan) - Information, neutral states

### Spacing Scale
- **XS**: `5px` - Very tight spacing
- **SM**: `10px` - Small spacing
- **MD**: `20px` - Medium spacing (default)
- **LG**: `30px` - Large spacing
- **XL**: `40px` - Extra large spacing

### Typography Scale
- **SM**: `14px` - Small text, labels
- **Base**: `16px` - Body text
- **LG**: `18px` - Subheadings
- **XL**: `24px` - Headings
- **XXL**: `32px` - Large headings

### Border Radius
- **SM**: `4px` - Buttons, inputs
- **MD**: `8px` - Cards, containers
- **LG**: `12px` - Large containers

## 📱 Responsive Design

Built-in responsive breakpoints:

```css
@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
  }
  
  .flights-list {
    grid-template-columns: 1fr;
  }
}
```

## 🚀 Performance Benefits

1. **Reduced Bundle Size**: Single CSS file instead of multiple
2. **Better Caching**: One CSS file to cache
3. **Faster Loading**: Fewer HTTP requests
4. **Runtime Theming**: CSS variables enable instant theme switching
5. **Better Tree Shaking**: Unused styles are easier to identify

## 🔧 Maintenance

### Adding New Components
1. Add component styles to `index.css` under appropriate section
2. Use existing CSS variables for consistency
3. Follow the established naming convention
4. Add responsive styles if needed

### Adding New Colors
1. Add the color variable to `:root`
2. Add theme-specific variants if needed
3. Update the TypeScript theme types
4. Document the color usage

### Customizing Themes
1. Modify CSS variables in `:root` sections
2. Add new theme data attributes if needed
3. Update the theme switcher options
4. Test in both light and dark modes

## 📁 File Structure

```
src/
├── index.css          # Unified styles with CSS variables
├── theme.ts           # Theme utilities and TypeScript types
├── main.tsx           # App entry point with theme initialization
├── App.tsx            # Main app component
└── components/
    ├── ThemeSwitch.tsx # Theme switching component
    ├── Settings.tsx    # Settings page
    └── ...
```

## 🎭 Theme Components

### ThemeSwitch Component
A ready-to-use theme switcher:

```tsx
import { ThemeSwitch } from './components/ThemeSwitch';

// Add to navigation or settings
<ThemeSwitch />
```

Features:
- Auto-detects system preference
- Saves user preference to localStorage
- Instant theme switching
- Accessible select dropdown

## 🔮 Future Enhancements

1. **Custom Theme Builder**: Allow users to create custom color schemes
2. **CSS-in-JS Integration**: Optional styled-components support
3. **Animation System**: Consistent animations using CSS variables
4. **Component Library**: Extract common components to reusable library
5. **Design Tokens**: Export design tokens for other applications

---

**Migration Complete**: ✅ All CSS files consolidated
**Theme System**: ✅ Light/Dark/Auto themes working
**Performance**: ✅ Improved bundle size and loading
**Maintainability**: ✅ Single source of truth for styles

*Last updated: July 27, 2025*
