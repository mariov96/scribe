# User Acceptance Test (UAT): Model Selection & Performance

**Objective:** To verify the new model selection UI, confirm the performance improvements, and ensure the application is stable.

---

### Test Case 1: Verify New Model Selection UI

**Steps:**
1.  Start Scribe.
2.  Navigate to the **Settings** page.
3.  Locate the **Whisper Model** section.

**Expected Result:**
*   You should see a matrix of selectable radio buttons for different models, categorized into "Standard Whisper Models" and "Distil-Whisper (High Performance)".
*   The dropdown menu for model selection should be gone.
*   The currently active model should be selected (e.g., "Base").

---

### Test Case 2: Verify Model Switching Logic

**Steps:**
1.  In the **Whisper Model** section, click on a model that is **not** currently active (e.g., "Small").
2.  Observe the UI.

**Expected Result:**
*   The info panel below the selection should update to show details for the "Small" model.
*   **Crucially, the application should NOT immediately start downloading or switching.**
*   An "Apply Model" button should appear. If the model is not downloaded, a "Download Model" button should appear instead.

---

### Test Case 3: Verify Model Download and Application

**Steps:**
1.  Select a model you have not used before, like **"Distil-Medium"**.
2.  A "Download Distil-Medium" button should appear. Click it.
3.  Observe the UI and logs.

**Expected Result:**
*   A progress bar should appear, and the button text should indicate downloading.
*   The application should remain responsive during the download.
*   Once the download is complete, the "Apply Model" button should appear, and the model should be applied automatically.
*   A success notification should appear confirming the model has been switched.
*   The "Distil-Medium" radio button should now be the active selection, and the info panel should show "✅ Currently Active".

---

### Test Case 4: Verify Performance and Stability

**Steps:**
1.  Ensure a fast model like **"Distil-Medium"** is active.
2.  Press the hotkey, speak a sentence for 3-5 seconds, and release.
3.  Observe the time it takes for the transcription to appear.
4.  Repeat the process several times.

**Expected Result:**
*   The application should transcribe your speech without crashing.
*   The `ValueError` from previous logs should not appear.
*   The transcription should feel responsive, with minimal delay after you stop speaking.
*   The logs should be clean of "Unknown property transition" spam.