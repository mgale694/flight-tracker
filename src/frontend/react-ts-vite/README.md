# Flight Tracker - React Web Dashboard

React + TypeScript + Vite web application for the Flight Tracker system.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📦 Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint for code quality

## 🔧 Configuration

### Environment Variables

Create a `.env` file for custom backend URL:

```
VITE_API_BASE_URL=http://your-backend-url:8000
```

### Backend Connection

The app automatically detects the backend URL:

1. Environment variable `VITE_API_BASE_URL`
2. Current hostname with port 8000 (for network access)
3. Fallback to `http://localhost:8000`

## 🏗️ Tech Stack

- **React 18** - UI library with hooks and functional components
- **TypeScript** - Type safety and better developer experience
- **Vite** - Fast build tool and development server
- **CSS Custom Properties** - Theme system and design tokens
- **ESLint** - Code quality and consistency

## 📱 Features

- **Responsive Design** - Works on desktop, tablet, and mobile
- **Dark/Light Theme** - System preference detection with manual toggle
- **Real-time Updates** - 5-second polling for live flight data
- **Offline Handling** - Graceful degradation when backend unavailable
- **TypeScript** - Full type safety across components and API

## 🔗 Related Documentation

- [Frontend Guide](../README.md) - Complete frontend documentation
- [Backend API](../../backend/README.md) - Backend service documentation
- [Project Documentation](../../../docs/README.md) - Full project guides

---

For detailed information about the Flight Tracker system, see the [main documentation](../../../README.md).
languageOptions: {
parserOptions: {
project: ['./tsconfig.node.json', './tsconfig.app.json'],
tsconfigRootDir: import.meta.dirname,
},
// other options...
},
},
])

````

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
````
