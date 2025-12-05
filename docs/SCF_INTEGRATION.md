# Session Continuity Framework (SCF) Integration

**Objective:** Integrate the Gemini API Caching strategy (SCF) into the Scribe application to provide intelligent, cost-saving features for users leveraging cloud-based AI.

---

## 1. Core Module (`scf_cacher.py`)

*   **File:** `src/scribe/core/scf_cacher.py`
*   **Purpose:** Encapsulates all logic for creating, using, and deleting `CachedContent` on the Gemini API.
*   **Key Features:**
    *   Handles API key configuration.
    *   Provides a simple interface: `create_cache`, `generate_with_cache`, `delete_cache`.
    *   Includes validation to check for token counts and confirm cache usage.

## 2. Application Integration (`app.py`)

*   **File:** `src/scribe/app.py`
*   **Changes:**
    *   The `ScribeApp` class now initializes an `ScfCacher` instance if a `GEMINI_API_KEY` is found in the environment.
    *   If no key is found, the feature is gracefully disabled.
    *   The `shutdown` method should be updated to call `delete_cache` to ensure no lingering storage costs.

## 3. UI Implementation (`settings.py`)

*   **File:** `src/scribe/ui_fluent/pages/settings.py`
*   **Changes:**
    *   A new **"SCF Caching (Experimental)"** card has been added to the Settings page.
    *   **UI Components:**
        *   `LineEdit` for users to enter their Gemini API key.
        *   `Label` to display the current cache status (e.g., "Not Active", "Cache ID: ...").
        *   "Create Cache" and "Delete Cache" buttons to manage the lifecycle.
    *   **Logic:**
        *   The UI will need to be connected to the `ScfCacher` instance in the main app to trigger these actions.
        *   The API key should be securely stored in the application's configuration.

---

## Next Steps & Considerations

1.  **Connect UI to Logic:** Wire up the new buttons in `settings.py` to the corresponding methods in `scf_cacher.py` via the main `ScribeApp` instance.
2.  **State Management:** The UI needs to reflect the current state of the cache (e.g., disable "Delete" if no cache exists).
3.  **Content Strategy:** Decide *what* to cache. A good starting point would be to allow users to select a large document (e.g., a project's `README.md` or a technical manual) to serve as the context for a session.
4.  **Error Handling:** Provide clear feedback to the user if cache creation fails (e.g., API key is invalid, content is too small).