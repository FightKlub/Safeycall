# Contributing to SaferCall AI

First off, thank you for considering contributing to SaferCall AI! It's people like you that make SaferCall AI such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs if possible**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and explain the behavior you expected**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Follow the Python style guide (PEP 8)
* Include thoughtfully-worded, well-structured tests
* Document new code based on the Documentation Styleguide
* End all files with a newline

## Development Setup

### Prerequisites
```bash
Python 3.9+
FFmpeg
Git
Docker (optional)
```

### Setup Steps

1. **Fork and clone the repository**
```bash
git clone https://github.com/yourusername/safercall-ai.git
cd safercall-ai/backend
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Run tests**
```bash
pytest
```

6. **Run the application**
```bash
uvicorn main:app --reload
```

## Style Guidelines

### Python Style Guide

* Follow PEP 8
* Use type hints for all function parameters and return values
* Maximum line length: 100 characters
* Use docstrings for all public modules, functions, classes, and methods

Example:
```python
def detect_scam(text: str) -> bool:
    """
    Detect if text contains scam indicators.
    
    Args:
        text: The text to analyze
    
    Returns:
        bool: True if scam indicators are found
    """
    pass
```

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Example:
```
Add audio file validation

- Check file extension
- Validate file size
- Add error messages

Fixes #123
```

### Branch Naming

* `feature/description` - New features
* `bugfix/description` - Bug fixes
* `hotfix/description` - Urgent fixes
* `docs/description` - Documentation updates

## Testing Guidelines

### Writing Tests

* Write tests for all new features
* Ensure all tests pass before submitting PR
* Aim for 80%+ code coverage

Example:
```python
def test_detect_scam_positive():
    """Test scam detection with scam text"""
    text = "Send OTP and bank account details"
    assert detect_scam(text) is True
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_scam_detector.py

# Run specific test
pytest tests/test_scam_detector.py::test_detect_scam_positive
```

## Documentation Guidelines

* Update README.md with details of changes to the interface
* Update DOCUMENTATION.md for technical documentation
* Add inline comments for complex logic
* Update API documentation for endpoint changes

## Review Process

1. Automated tests must pass
2. Code review by at least one maintainer
3. Documentation must be updated
4. No merge conflicts

## Community

* Join our Discord server: [link]
* Follow us on Twitter: [@SaferCallAI]
* Email: support@safercall.ai

## Recognition

Contributors will be recognized in:
* CONTRIBUTORS.md file
* Release notes
* Project README

## Questions?

Feel free to contact the maintainers if you have any questions. We're here to help!

---

Thank you for contributing to SaferCall AI! 🎉
