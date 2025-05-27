# Implementation Plan: Page Preview Zoom and Font Rendering

## Overview
Systematic plan to fix page preview zoom and font rendering with clear file responsibilities and no conflicting implementations.

## Current Problem Analysis
- Multiple page preview implementations causing conflicts
- Settings not properly propagated from main app to preview
- Zoom functionality broken due to overlapping code
- Font changes not applied due to unclear data flow

## File Allocation and Responsibilities

### 1. Core Page Preview Component
**File: `page_preview.py`** (SINGLE SOURCE OF TRUTH)
- **Class**: `PagePreview` (singleton)
- **Responsibilities**:
  - HTML rendering with proper CSS
  - Zoom controls (slider, buttons, fit-to-page)
  - Font and color application
  - Page layout and margins
  - Settings integration interface
- **Key Methods**:
  - `update_preview(html_content)` - Main content update
  - `update_zoom(value)` - Zoom level changes
  - `apply_document_settings(settings)` - Settings application
  - `setup_ui()` - UI initialization
- **Dependencies**: QtWebEngineView, document settings from main app

### 2. Main Application Integration
**File: `main.py`** (existing)
- **Responsibilities**:
  - Create PagePreview instance
  - Pass document settings to preview
  - Handle UI events for font/color changes
  - Coordinate between right panel and preview
- **Key Integration Points**:
  - Right panel font/color controls → PagePreview.apply_document_settings()
  - File loading → PagePreview.update_preview()
  - Settings changes → immediate preview update

### 3. Settings Management
**File: `settings_manager.py`** (existing)
- **Responsibilities**:
  - Store and retrieve document settings
  - Provide settings in consistent format
  - Handle settings persistence
- **Settings Structure**:
  ```python
  {
    "fonts": {
      "body": {"family": "Arial", "size": 12}
    },
    "colors": {
      "text": "#000000",
      "background": "#ffffff"
    },
    "page": {
      "zoom": 100
    }
  }
  ```

### 4. Test Files (for validation only)
**Files**: `test_*.py`
- **Purpose**: Validate functionality works in isolation
- **NOT**: Part of main application

## Implementation Steps

### Step 1: Clean Up Conflicting Files ✅
- [x] Remove all duplicate page preview files
- [x] Keep only `page_preview.py` as single implementation
- [x] Remove test files from main application imports

### Step 2: Define Clear Data Flow ✅
```
Main App → Settings Manager → Page Preview
   ↓              ↓              ↓
UI Controls → Document Settings → HTML/CSS Rendering
```

### Step 3: Implement Core PagePreview Class ✅
- [x] Single class with clear responsibilities
- [x] Simple HTML generation with embedded CSS
- [x] Direct zoom application via CSS
- [x] Immediate settings application

### Step 4: Integration Points ✅
- [x] Main app creates single PagePreview instance
- [x] Right panel changes trigger settings update
- [x] Settings update triggers preview refresh
- [x] No intermediate layers or managers

### Step 5: Testing and Validation ✅
- [x] Test zoom controls work immediately
- [x] Test font changes apply instantly
- [x] Test settings persist across file loads
- [x] Test no conflicts or duplicate behavior

## Success Criteria
1. **Single Implementation**: Only one PagePreview class in one file
2. **Immediate Response**: Zoom and font changes apply instantly
3. **Settings Integration**: Right panel controls directly affect preview
4. **No Conflicts**: No duplicate or competing implementations
5. **Clean Code**: Clear responsibilities and data flow

## Files to Remove/Ignore
- `page_preview_simple.py`
- `page_preview_working.py`
- `page_preview_backup.py`
- `test_simple_*.py`
- Any other page preview variants

## Implementation Priority
1. **HIGH**: Single working PagePreview class
2. **HIGH**: Settings integration with main app
3. **MEDIUM**: Zoom controls functionality
4. **MEDIUM**: Font rendering accuracy
5. **LOW**: Advanced features (pagination, etc.)
