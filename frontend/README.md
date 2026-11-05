# Sannetic Explorer Frontend

A modern SvelteKit frontend for the Sannetic Explorer solar system simulation project.

## Features

- **SvelteKit** - Modern full-stack web framework
- **TypeScript** - Type-safe development
- **TailwindCSS** - Utility-first CSS framework
- **daisyUI** - Beautiful component library
- **Threlte** - Three.js integration for 3D graphics
- **Vite** - Fast build tool with hot module replacement

## Project Structure

```
frontend/
├── src/
│   ├── lib/           # Shared utilities and components
│   │   ├── components/ # Reusable Svelte components
│   │   ├── api.ts     # API functions and types
│   │   └── utils/     # Utility functions
│   ├── routes/        # SvelteKit routes
│   └── app.css        # Global styles with Tailwind
├── static/            # Static assets
├── package.json       # Dependencies and scripts
├── svelte.config.js   # SvelteKit configuration
├── vite.config.ts     # Vite configuration with aliases
├── tailwind.config.js # Tailwind CSS configuration
└── tsconfig.json      # TypeScript configuration
```

## Environment Configuration

Create a `.env` file in the frontend directory with:

```bash
# API Configuration
PUBLIC_API_URL=http://localhost:8000
```

Use `http://localhost:8000` when the API is running on the host. The Docker stack publishes the API on **http://localhost:13800** and the UI on **http://localhost:13300** (`make up`). `npm run dev:front` still uses port 3000.

**Note**: All environment variables prefixed with `PUBLIC_` are exposed to the client and can be accessed via `import.meta.env.PUBLIC_*`.

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- FastAPI backend running (default: http://localhost:8000)

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables (see above)

4. Start the development server:
   ```bash
   npm run dev:front
   ```

The app will be available at `http://localhost:3000` with:
- Beautiful daisyUI components
- Interactive 3D scene at `/3d`
- Theme switching capabilities
- Responsive design
- TypeScript support throughout
- Real-time data from the FastAPI backend

### Available Scripts

- `npm run dev:front` - Start development server on port 3000
- `npm run dev` - Start development server on default port
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run check` - Type-check the project
- `npm run lint` - Lint the code
- `npm run format` - Format the code

## Configuration

### Vite Aliases

The project is configured with the following path aliases:

- `$lib/*` → `src/lib/*`

### TailwindCSS + daisyUI

The project uses TailwindCSS with daisyUI for beautiful, accessible components. Available themes:

- light
- dark  
- cyberpunk
- synthwave

### Threlte (Three.js)

The project includes Threlte for 3D graphics. See `src/lib/components/SolarSystemCanvas.svelte` for the main 3D scene.

### API Integration

The frontend integrates with the FastAPI backend through:

- `src/lib/api.ts` - API functions and TypeScript interfaces
- Automatic data loading in page load functions
- Real-time celestial body data display
- Error handling for API failures

## Development

### Adding New Components

1. Create components in `src/lib/components/`
2. Import using the `$lib` alias:
   ```typescript
   import MyComponent from '$lib/components/MyComponent.svelte';
   ```

### Adding New Routes

1. Create new `.svelte` files in `src/routes/`
2. SvelteKit will automatically create routes based on the file structure

### Styling

- Use TailwindCSS utility classes for styling
- Use daisyUI components for consistent design
- Add custom styles in `src/app.css`

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Integration with Backend

This frontend is designed to work with the Sannetic Explorer backend API. The backend provides:

- Celestial body data via `/bodies` endpoint
- Orbital calculations
- Real-time spacecraft tracking
- Historical exploration data

The frontend automatically fetches and displays this data in the 3D visualization.

## Contributing

1. Follow the existing code style
2. Use TypeScript for type safety
3. Add proper error handling
4. Test your changes thoroughly 