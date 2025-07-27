# Flight Tracker Documentation

Comprehensive guides and documentation for the Flight Tracker project.

## 📚 Available Guides

### 🚀 Setup & Installation

- **[Quick Start Guide](../README.md#quick-start)** - Get up and running quickly
- **[Startup Scripts Guide](STARTUP_SCRIPTS.md)** - Automated startup and development scripts
- **[Raspberry Pi Setup](../src/raspi/README.md)** - Hardware installation and configuration

### 🔧 Development

- **[API Polling Guide](POLLING_GUIDE.md)** - Best practices for API integration
- **[CSS Architecture](CSS_ARCHITECTURE.md)** - Frontend styling system and theme management
- **[Refactoring Notes](REFACTORING_COMPLETE.md)** - Major code changes and architecture decisions

### 🏗️ Architecture

- **[Project Structure](../src/README.md)** - Source code organization
- **[Backend API](../src/backend/README.md)** - FastAPI service documentation
- **[Frontend Dashboard](../src/frontend/README.md)** - React application guide
- **[Hardware Interface](../src/raspi/README.md)** - Raspberry Pi implementation

### 🛠️ Configuration

- **Backend Configuration**: `src/backend/config.toml`
- **Raspberry Pi Configuration**: `src/raspi/config.toml`
- **Frontend Environment**: Environment variables and build settings

### 🔍 API Reference

#### Backend Endpoints

```
GET  /flights          # Current tracked flights
GET  /config           # Configuration settings
POST /config           # Update configuration
GET  /logs             # Activity logs
DELETE /logs           # Clear logs
GET  /health           # System health
```

#### Frontend Components

- **Display Page**: Real-time flight tracking interface
- **Settings Page**: Configuration management
- **Activities Page**: System logs and monitoring

### 🐛 Troubleshooting

#### Common Issues

1. **Backend Connection**: Check if backend is running on correct port
2. **No Flights Detected**: Verify location and search radius settings
3. **Display Issues**: Check hardware connections and driver configuration
4. **API Errors**: Ensure internet connection and FlightRadar24 access

#### Debug Commands

```bash
# Backend debugging
python src/backend/main.py --host 127.0.0.1 --port 8000

# Frontend development
cd src/frontend/react && npm run dev

# Raspberry Pi testing
cd src/raspi && python tracker.py --debug
```

### 📊 Performance Tips

#### Backend Optimization

- Monitor API rate limits
- Configure appropriate polling intervals
- Use efficient data structures for flight storage

#### Frontend Performance

- Enable production builds for deployment
- Use React DevTools for component profiling
- Optimize polling frequencies based on usage

#### Hardware Optimization

- Use appropriate update intervals for e-ink displays
- Monitor CPU and memory usage on Raspberry Pi
- Configure logging levels appropriately

### 🔐 Security Considerations

#### Network Security

- Use HTTPS in production deployments
- Configure CORS appropriately for your domain
- Consider API authentication for public deployments

#### Hardware Security

- Change default Raspberry Pi passwords
- Use SSH keys for remote access
- Keep system packages updated

### 📈 Monitoring & Maintenance

#### Log Management

- Backend logs: In-memory with API access
- Frontend logs: Browser console and localStorage
- Raspberry Pi logs: File-based with rotation

#### Health Checks

- `/health` endpoint for backend monitoring
- Connection status indicators in frontend
- Hardware status monitoring on Raspberry Pi

### 🤝 Contributing

#### Development Workflow

1. Fork the repository
2. Create feature branch from main
3. Make changes with appropriate tests
4. Update documentation as needed
5. Submit pull request with clear description

#### Code Standards

- **Backend**: PEP 8 Python style guide
- **Frontend**: ESLint configuration with React rules
- **Documentation**: Clear, concise markdown with examples

#### Testing Guidelines

- Test API endpoints with curl or Postman
- Verify frontend functionality across browsers
- Test hardware integration on actual Raspberry Pi

---

## 📞 Support

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for questions and community support
- **Documentation**: Submit PRs for documentation improvements

---

_Last updated: ${new Date().toISOString().split('T')[0]}_
