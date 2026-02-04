# Contributing to Paper-Verify

Thank you for your interest in contributing to Paper-Verify!

## Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/rakaarao17/paper-verify
   cd paper-verify
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

```bash
pytest tests/ -v
```

## Code Style

We use `ruff` for linting and `black` for formatting:

```bash
ruff check src/
black src/
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/ -v`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Reporting Issues

Please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
