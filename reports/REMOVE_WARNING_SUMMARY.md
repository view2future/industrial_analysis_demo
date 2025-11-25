# Summary of Changes to Remove pkg_resources Deprecation Warning

## Problem
When starting the system, the following warning appears:
```
/Users/wangyu94/regional-industrial-dashboard/venv/lib/python3.12/site-packages/jieba/_compat.py:18: UserWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html. The pkg_resources package is slated for removal as early as 2025-11-30. Refrain from using this package or pin to Setuptools<81.
  import pkg_resources
```

## Solution Implemented

### 1. Updated requirements.txt
Added `setuptools<81.0.0` to pin to a version that doesn't show the deprecation warning.

### 2. Updated start.sh script
Added environment variable to suppress warnings:
```bash
export PYTHONWARNINGS="ignore::UserWarning"
```

Also updated all Python commands to include the environment variable:
- `pip install` commands
- `celery` worker start command
- `python3 app_enhanced.py` start command

### 3. Updated Python files
Added warning suppression code to the beginning of key Python files:
- `app_enhanced.py`
- `src/tasks/celery_app.py`
- `src/tasks/report_tasks.py`

Code added:
```python
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")
```

## Files Modified
1. `requirements.txt` - Added setuptools version pin
2. `start.sh` - Added environment variables to suppress warnings
3. `app_enhanced.py` - Added warning suppression code
4. `src/tasks/celery_app.py` - Added warning suppression code
5. `src/tasks/report_tasks.py` - Added warning suppression code

## Result
The deprecation warning no longer appears when starting the system, making the output cleaner and more user-friendly.