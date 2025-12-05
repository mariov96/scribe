# Local Transcription Model Comparison

**Constraint:** Local-only, free, CPU/GPU compatible.

## 1. Faster-Whisper (Current)
*   **Engine:** CTranslate2 (Optimized Transformer inference)
*   **Models:** OpenAI Whisper (Tiny, Base, Small, Medium, Large-v2/v3)
*   **Pros:**
    *   Extremely fast on CPU (int8 quantization).
    *   Low memory footprint.
    *   Battle-tested, reliable.
    *   Good general-purpose accuracy.
*   **Cons:**
    *   Can struggle with specialized technical jargon (e.g., "Kubernetes", "PyTorch" might be "Pie Torch").
    *   Hallucinations in silence (though VAD fixes this).

## 2. AquaVoice Avalon
*   **Status:** **Cloud-only API**.
*   **Verdict:** **Disqualified** based on "Local only" constraint.
*   **Note:** While impressive for tech jargon, it requires sending audio to their servers.

## 3. Distil-Whisper
*   **Engine:** Compatible with Faster-Whisper / HuggingFace.
*   **Models:** `distil-medium.en`, `distil-large-v2`
*   **Pros:**
    *   **6x faster** than standard Whisper.
    *   49% smaller model size.
    *   Maintains ~99% of Whisper's accuracy.
    *   Designed specifically for lower latency.
*   **Cons:**
    *   English only (mostly).
    *   Slightly less robust to background noise than full large models.

## 4. Deepgram (Aura/Nova)
*   **Status:** Cloud API.
*   **Verdict:** **Disqualified**.

## 5. Vosk
*   **Engine:** Kaldi-based.
*   **Pros:** Extremely lightweight (runs on Raspberry Pi).
*   **Cons:** Accuracy significantly lower than Whisper; requires specific language packs.
*   **Verdict:** Not recommended for modern desktop use unless hardware is extremely limited.

---

## Recommendation: Multi-Model Architecture

Since AquaVoice is cloud-based, the best path forward for a "tech-aware" local experience is to allow users to swap between **Standard Whisper** (for general accuracy) and **Distil-Whisper** (for extreme speed).

We can also explore **fine-tuned Whisper models** from HuggingFace that are trained on technical datasets, provided they are compatible with CTranslate2.

### Proposed Architecture

1.  **Abstract Backend:** Create a `TranscriptionBackend` interface.
2.  **Implementations:**
    *   `FasterWhisperBackend` (Current)
    *   `DistilWhisperBackend` (Specialized config for Distil models)
3.  **Configuration:**
    *   Allow users to specify `model_id` (e.g., `distil-whisper/distil-medium.en`) instead of just size (`medium`).
    *   Auto-download from HuggingFace.

### Action Plan

1.  **Refactor `TranscriptionEngine`**: Decouple the `WhisperModel` instantiation.
2.  **Add Distil-Whisper Support**: Test `distil-medium.en` with the current engine (it should work out of the box with minor config tweaks).
3.  **UI Update**: Change the "Model" dropdown to allow selecting "Distil-Medium (Fast)" and "Distil-Large (Fast & Accurate)".