# Markdown to PDF Converter Test Report

Generated: 2025-05-26 13:53:30

## Summary

- Total Tests: 15
- Passed: 12
- Failed: 3
- Pass Rate: 80.00%
- Total Execution Time: 150.59 seconds

## Results by Category

### Other

- Tests: 1
- Passed: 0
- Pass Rate: 0.00%

| Test | Status | Time (s) | Message |
|------|--------|----------|--------|
| UnitTests | ❌ FAIL | 60.06 | Unit tests failed to run: Process timed out after 60 seconds |

### ContentProcessor

- Tests: 6
- Passed: 6
- Pass Rate: 100.00%

| Test | Status | Time (s) | Message |
|------|--------|----------|--------|
| mermaid | ✅ PASS | 1.77 | Test passed |
| math | ✅ PASS | 1.70 | Test passed |
| image | ✅ PASS | 1.59 | Test passed |
| code | ✅ PASS | 1.65 | Test passed |
| media | ✅ PASS | 1.69 | Test passed |
| visualization | ✅ PASS | 1.59 | Test passed |

### MDZ

- Tests: 3
- Passed: 2
- Pass Rate: 66.67%

| Test | Status | Time (s) | Message |
|------|--------|----------|--------|
| Basic | ✅ PASS | 2.97 | Test passed |
| Export | ✅ PASS | 0.09 | Test passed |
| Comprehensive | ❌ FAIL | 60.19 | Test timed out after 60 seconds |

### Export

- Tests: 4
- Passed: 4
- Pass Rate: 100.00%

| Test | Status | Time (s) | Message |
|------|--------|----------|--------|
| PDF | ✅ PASS | 6.66 | Test passed |
| HTML | ✅ PASS | 5.65 | Test passed |
| DOCX | ✅ PASS | 2.49 | Test passed |
| EPUB | ✅ PASS | 2.46 | Test passed |

### ZoomFix

- Tests: 1
- Passed: 0
- Pass Rate: 0.00%

| Test | Status | Time (s) | Message |
|------|--------|----------|--------|
| Automated | ❌ FAIL | 0.06 | Test failed with return code 2 |

## Failed Tests

### UnitTests

- Message: Unit tests failed to run: Process timed out after 60 seconds
- Execution Time: 60.06 seconds

#### Details

```

```

### MDZ.Comprehensive

- Message: Test timed out after 60 seconds
- Execution Time: 60.19 seconds

#### Details

```
STDOUT:


STDERR:
Process timed out after 60 seconds
```

### ZoomFix.Automated

- Message: Test failed with return code 2
- Execution Time: 0.06 seconds

#### Details

```
STDOUT:


STDERR:
C:\Users\joshd\anaconda3\envs\py3\python.exe: can't open file 'C:\\Projects\\markdown2pdf\\test_zoom_fix_automated.py': [Errno 2] No such file or directory

```

