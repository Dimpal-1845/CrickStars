# Quick Test Execution Guide

## Step 1: Install Test Dependencies

```bash
# Windows PowerShell
pip install pytest pytest-asyncio httpx

# Or install from requirements
pip install -r requirements.txt
```

## Step 2: Run All Tests

```bash
# Run all tests with verbose output
pytest test_api.py -v

# Run and show print statements
pytest test_api.py -v -s

# Run with test times
pytest test_api.py -v --durations=10
```

## Step 3: Run Specific Test Groups

```bash
# Run only CRUD tests
pytest test_api.py::TestQuickMatchCRUD -v

# Run only inning tests
pytest test_api.py::TestInningManagement -v

# Run only validation tests
pytest test_api.py::TestDataValidation -v

# Run only error handling tests
pytest test_api.py::TestErrorHandling -v

# Run only main endpoints
pytest test_api.py::TestMainEndpoints -v
```

## Step 4: Run Individual Tests

```bash
# Test match creation
pytest test_api.py::TestQuickMatchCRUD::test_create_quick_match_success -v

# Test match retrieval
pytest test_api.py::TestQuickMatchCRUD::test_get_single_match_success -v

# Test inning start
pytest test_api.py::TestInningManagement::test_start_inning_success -v
```

## Expected Output

```
================================ test session starts =================================
collected 21 items

test_api.py::TestMainEndpoints::test_health_check PASSED                    [  4%]
test_api.py::TestMainEndpoints::test_index_page PASSED                      [  9%]
test_api.py::TestQuickMatchCRUD::test_create_quick_match_success PASSED    [ 14%]
test_api.py::TestQuickMatchCRUD::test_create_quick_match_missing_required_field PASSED [ 19%]
...

================================ 21 passed in 2.34s ==================================
```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'pytest'"
```bash
# Install pytest
pip install pytest
```

### Error: "ModuleNotFoundError: No module named 'sqlalchemy'"
```bash
# Install all dependencies
pip install -r requirements.txt
```

### Error: "Database locked"
```bash
# Delete test.db file and retry
del test.db
pytest test_api.py -v
```

### Error: "Port 8000 already in use"
```bash
# If API server is running, stop it first
# Then run tests
pytest test_api.py -v
```

## Live Test Dashboard

```bash
# Install pytest-html for HTML reports
pip install pytest-html

# Generate HTML report
pytest test_api.py -v --html=report.html

# Open report.html in browser
start report.html  # Windows
open report.html   # macOS
xdg-open report.html  # Linux
```

## Continuous Testing

```bash
# Auto-rerun tests when files change
pip install pytest-watch
ptw test_api.py
```

---

**Total Tests**: 21
**Estimated Time**: 2-3 seconds
**Coverage**: All endpoints + error handling + data validation
