# CI/CD Pipeline Troubleshooting Guide

## Overview
This document provides troubleshooting information for the GitHub Actions CI/CD pipeline.

## Recent Fixes (2024)

### GitHub Actions Version Compatibility
**Issue**: CI pipeline failing with "Missing download info for actions/upload-artifact@v3" error.

**Solution**: Updated all GitHub Actions to latest stable versions:
- `actions/setup-python@v4` → `v5`
- `actions/upload-artifact@v3` → `v4`
- `codecov/codecov-action@v3` → `v4`

### Codecov Integration
**Issue**: Codecov v4 requires authentication token.

**Solution**: 
- Added `token: ${{ secrets.CODECOV_TOKEN }}` to codecov step
- Set `fail_ci_if_error: false` to prevent codecov failures from blocking CI
- Requires `CODECOV_TOKEN` secret to be configured in GitHub repository settings

## Pipeline Structure

### Test Job
- **Purpose**: Run unit tests, integration tests, linting, and coverage analysis
- **Matrix**: Python 3.9 and 3.11
- **Key Steps**:
  1. Checkout code
  2. Set up Python environment
  3. Install dependencies with `pip install .[dev]`
  4. Run flake8 linting
  5. Execute unit tests with pytest and coverage
  6. Run integration tests (allowed to fail)
  7. Upload coverage to Codecov
  8. Upload coverage reports as artifacts

### Benchmark Job
- **Purpose**: Run performance benchmark tests
- **Dependencies**: Only runs if test job passes
- **Matrix**: Python 3.9 and 3.11
- **Key Steps**:
  1. Checkout code
  2. Set up Python environment
  3. Install dependencies
  4. Run benchmark tests with detailed output
  5. Upload benchmark results as artifacts

## Common Issues and Solutions

### 1. Action Version Incompatibility
**Symptoms**: "Missing download info" errors, deprecated action warnings

**Solution**: Regularly update GitHub Actions to latest stable versions. Check [GitHub Actions Marketplace](https://github.com/marketplace/actions/) for latest versions.

### 2. Codecov Upload Failures
**Symptoms**: Codecov step failing, coverage not appearing on dashboard

**Solutions**:
- Ensure `CODECOV_TOKEN` is set in repository secrets
- Check coverage.xml file is generated correctly
- Use `fail_ci_if_error: false` to prevent blocking CI

### 3. Test Failures in CI but Passing Locally
**Symptoms**: Tests pass on local machine but fail in CI

**Common Causes & Solutions**:
- **Missing dependencies**: Ensure all dependencies are in `pyproject.toml`
- **Environment differences**: Use `python -m` prefix for commands
- **External service dependencies**: Use mocking for external APIs in unit tests
- **Timing issues**: Add appropriate timeouts and retries for async operations

### 4. Benchmark Test Instability
**Symptoms**: Benchmark tests producing inconsistent results or failing

**Solutions**:
- Use `continue-on-error: true` for benchmark jobs
- Consider running benchmarks on dedicated stable hardware
- Implement retry mechanisms for flaky performance tests
- Use relative performance metrics rather than absolute values

## Monitoring and Maintenance

### Regular Maintenance Tasks
1. **Monthly**: Update GitHub Actions to latest versions
2. **Quarterly**: Review and update Python versions in matrix
3. **As needed**: Update dependencies in `pyproject.toml`

### Performance Monitoring
- Monitor benchmark results trends over time
- Set up alerts for significant performance regressions
- Archive benchmark results for historical analysis

## Debugging Commands

### Local Testing
```bash
# Run the same commands as CI locally
python -m pip install --upgrade pip
pip install .[dev]

# Linting
python -m flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics

# Unit tests with coverage
python -m pytest tests/fetcher/test_fetcher_mock.py tests/utils/ -m "not benchmark" --cov=src --cov-report=xml --cov-report=html --cov-report=term-missing

# Integration tests
python -m pytest -m "integration" --tb=short

# Benchmark tests
python -m pytest -m "benchmark" --tb=long -v
```

### GitHub Actions Debugging
- Use `actions/upload-artifact@v4` to upload logs and debug files
- Add debug steps with environment variable dumps
- Use `continue-on-error: true` for non-critical steps
- Enable debug logging with `ACTIONS_STEP_DEBUG: true`

## Security Considerations

### Secrets Management
- Store sensitive tokens (CODECOV_TOKEN) in GitHub repository secrets
- Never commit API keys or tokens to version control
- Use `secrets.` prefix to access repository secrets in workflows

### Dependency Security
- Regularly update dependencies to patch security vulnerabilities
- Use `pip-audit` or similar tools to scan for known vulnerabilities
- Pin dependency versions in production deployments

## Contact and Support

For CI/CD pipeline issues:
1. Check this troubleshooting guide
2. Review recent workflow runs in GitHub Actions tab
3. Check dependency updates and compatibility
4. Consider creating an issue in the repository for persistent problems

---

**Last Updated**: December 2024  
**Pipeline Version**: GitHub Actions with Python 3.9/3.11 matrix
