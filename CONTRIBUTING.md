# Contributing to PhilEarthStats

Thank you for your interest in contributing to PhilEarthStats! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs 🐛

If you find a bug, please create an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected behavior vs actual behavior
- Screenshots if applicable
- Your environment (OS, Python version, Node version)

### Suggesting Features 💡

Feature requests are welcome! Please provide:
- Clear description of the feature
- Use cases and benefits
- Potential implementation approach (if you have ideas)

### Code Contributions 🔨

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style
   - Add comments for complex logic
   - Test your changes thoroughly

4. **Commit your changes**
   ```bash
   git commit -m "Add: description of your changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**

## Development Guidelines

### Python Backend

- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Handle errors gracefully
- Test API endpoints

### React Frontend

- Use functional components with hooks
- Follow existing component structure
- Use TailwindCSS for styling
- Keep components focused and reusable
- Handle loading and error states

### Code Style

**Python:**
```python
def fetch_earthquake_data(start_date, end_date):
    """
    Fetch earthquake data for the specified date range.
    
    Args:
        start_date: Start date for query
        end_date: End date for query
    
    Returns:
        dict: Earthquake data
    """
    # Implementation
```

**JavaScript/React:**
```javascript
const EarthquakeCard = ({ earthquake }) => {
  // Component implementation
  return (
    <div className="earthquake-card">
      {/* JSX */}
    </div>
  );
};
```

## Testing

### Backend Testing
```bash
cd backend
python -m pytest
```

### Frontend Testing
```bash
cd frontend
npm test
```

## Areas for Contribution

### High Priority
- [ ] Add more data sources (alternative earthquake APIs)
- [ ] Implement user preferences/settings
- [ ] Add email/SMS notifications for significant events
- [ ] Create mobile app version
- [ ] Add historical data analysis

### Medium Priority
- [ ] Improve error handling and retry logic
- [ ] Add more visualization options
- [ ] Implement data export (CSV, JSON)
- [ ] Add multi-language support
- [ ] Create API documentation website

### Nice to Have
- [ ] Dark mode support
- [ ] Customizable alert thresholds
- [ ] Social media sharing
- [ ] Earthquake prediction models (educational)
- [ ] 3D visualization of earthquake depths

## Questions?

Feel free to open an issue for any questions about contributing!

## License

By contributing to PhilEarthStats, you agree that your contributions will be licensed under the project's license.
