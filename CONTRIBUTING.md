# Contributing to RemoteReach

Thank you for your interest in contributing to RemoteReach! This document provides guidelines and information for contributors.

## How to Contribute

### Reporting Issues

1. **Check existing issues** first to avoid duplicates
2. **Use the issue template** when creating new issues
3. **Provide detailed information** including:
   - Operating system and version
   - Python version
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Screenshots if applicable

### Suggesting Features

1. **Check existing feature requests** to avoid duplicates
2. **Describe the feature** clearly and explain why it would be useful
3. **Consider the scope** - keep suggestions focused and feasible

### Code Contributions

#### Setting Up Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:   ```bash
   git clone https://github.com/your-username/remotereach.git
   cd remotereach
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

#### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes** following the coding standards below
3. **Test your changes** thoroughly
4. **Commit your changes** with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```

#### Coding Standards

- **Python Code Style**: Follow PEP 8 guidelines
- **Comments**: Write clear, helpful comments for complex logic
- **Error Handling**: Include proper error handling and user feedback
- **Security**: Be mindful of security implications, especially for network features
- **Performance**: Consider performance impact of changes

#### Testing

- Test on multiple platforms if possible (Windows, macOS, Linux)
- Test with different devices (phones, tablets, desktop browsers)
- Verify that existing functionality still works
- Test edge cases and error conditions

#### Submitting Pull Requests

1. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
2. **Create a pull request** on GitHub
3. **Fill out the PR template** with:
   - Clear description of changes
   - Screenshots/GIFs if UI changes are involved
   - Testing steps
   - Any breaking changes
4. **Respond to feedback** and make requested changes

## Development Guidelines

### Code Organization

- Keep the main `app.py` focused on Flask/SocketIO routing
- Create separate modules for complex functionality
- Use clear, descriptive variable and function names
- Follow the existing project structure

### Frontend Development

- Maintain responsive design principles
- Test on various screen sizes
- Keep the interface intuitive and accessible
- Follow existing CSS/JavaScript patterns

### Security Considerations

- Never expose sensitive system information
- Validate all user inputs
- Consider network security implications
- Document any security-related changes

## Questions?

If you have questions about contributing, feel free to:
- Open an issue for discussion
- Contact the maintainers
- Check existing documentation

Thank you for contributing to RemoteReach!
