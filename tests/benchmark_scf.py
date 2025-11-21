import os
import time
import logging
import google.generativeai as genai
from google.generativeai.types import content_types
from dotenv import load_dotenv

# --- Configuration ---
# Ensure your GEMINI_API_KEY is set as an environment variable
try:
    api_key = "AIzaSyA1AIFI8UdabZVxCF0RayOqncpafQ4L6L8"
    if not api_key:
        raise ValueError("API key is missing.")
        
    genai.configure(api_key=api_key)
    MODEL_ID = "gemini-1.5-pro-latest" # Use a model that supports caching
    model = genai.GenerativeModel(model_name=MODEL_ID)
except Exception as e:
    print(f"ERROR: Could not configure Gemini client. Details: {e}")
    exit()

# --- Mock Data ---
# Simulate a large, static document (e.g., a project's entire codebase context)
# This needs to be large to show the benefit. We'll repeat a block of text.
CODEBASE_CONTEXT_BLOCK = """
# Scribe Application - Modern voice automation platform.
#
# Architecture:
#     - Plugin-first: All features are plugins
#     - Analytics-first: Track value from day 1
#     - Clean separation: Core, plugins, UI, analytics
#
# Flow:
#     User presses hotkey -> AudioRecorder captures -> TranscriptionEngine transcribes
#     -> Text goes to plugins for processing -> Analytics tracks everything -> Output to user
#
# Threading Architecture:
#     1. Main/GUI Thread (Qt event loop)
#     2. Keyboard Library Thread (global hotkey listener)
#     3. Audio Thread (PortAudio callback)
#     4. Worker Threads (transcription, etc.)
"""
# Repeat the block to create a large context (~5000 tokens)
LARGE_CONTEXT = CODEBASE_CONTEXT_BLOCK * 25

# --- Helper Functions ---
def count_tokens(text):
    """Counts tokens for a given text."""
    return model.count_tokens(contents=text).total_tokens

def generate_without_cache(context: str, user_prompt: str):
    """Simulates a standard RAG query where the full context is sent every time."""
    full_prompt = f"CONTEXT:\n{context}\n\nQUESTION:\n{user_prompt}"
    response = model.generate_content(contents=full_prompt)
    return response.usage_metadata.prompt_token_count

def run_benchmark():
    """Runs and prints the before/after benchmark for SCF caching."""
    print("="*50)
    print("Running Session Continuity Framework (SCF) Benchmark")
    print("="*50)

    # --- SCENARIO 1: WITHOUT CACHING (Standard RAG) ---
    print("\n--- 1. Simulating Development Session WITHOUT Caching ---")
    total_tokens_without_cache = 0
    
    # Query 1
    print("Query 1: Summarize the architecture...")
    tokens_used = generate_without_cache(LARGE_CONTEXT, "Summarize the core architecture.")
    total_tokens_without_cache += tokens_used
    print(f"   Tokens Billed (Full Price): {tokens_used}")

    # Query 2
    print("Query 2: Explain the threading model...")
    tokens_used = generate_without_cache(LARGE_CONTEXT, "What are the main threads in the application?")
    total_tokens_without_cache += tokens_used
    print(f"   Tokens Billed (Full Price): {tokens_used}")

    # Query 3
    print("Query 3: Ask about the data flow...")
    tokens_used = generate_without_cache(LARGE_CONTEXT, "Describe the data flow from hotkey press to output.")
    total_tokens_without_cache += tokens_used
    print(f"   Tokens Billed (Full Price): {tokens_used}")

    print(f"\n>>> Total Tokens Billed (Without Cache): {total_tokens_without_cache}")

    # --- SCENARIO 2: WITH CACHING (SCF) ---
    print("\n--- 2. Simulating Development Session WITH SCF Caching ---")
    total_tokens_with_cache = 0
    
    # Step 1: Create the cache (one-time cost)
    print("Creating the cache (one-time operation)...")
    try:
        cache = genai.caching.CachedContent.create(
            model=MODEL_ID,
            contents=[content_types.to_content(LARGE_CONTEXT)],
            ttl="600s" # 10-minute TTL for the test
        )
        cache_creation_cost = cache.usage_metadata.total_token_count
        total_tokens_with_cache += cache_creation_cost
        print(f"   Cache created. ID: {cache.name}")
        print(f"   Tokens Billed for Creation (Full Price): {cache_creation_cost}")
    except Exception as e:
        print(f"   ERROR: Failed to create cache. {e}")
        return

    # Step 2: Use the cache for queries
    def generate_with_cache(cache_name, user_prompt):
        response = model.generate_content(
            contents=user_prompt,
            cached_content=cache_name
        )
        # IMPORTANT: We only pay for the NEW prompt tokens, not the cached ones.
        return response.usage_metadata.prompt_token_count, response.usage_metadata.cached_content_token_count

    # Query 1
    print("Query 1: Summarize the architecture...")
    new_tokens, cached_tokens = generate_with_cache(cache.name, "Summarize the core architecture.")
    total_tokens_with_cache += new_tokens
    print(f"   Cached Tokens (Discounted): {cached_tokens}")
    print(f"   New Tokens Billed (Full Price): {new_tokens}")

    # Query 2
    print("Query 2: Explain the threading model...")
    new_tokens, cached_tokens = generate_with_cache(cache.name, "What are the main threads in the application?")
    total_tokens_with_cache += new_tokens
    print(f"   Cached Tokens (Discounted): {cached_tokens}")
    print(f"   New Tokens Billed (Full Price): {new_tokens}")

    # Query 3
    print("Query 3: Ask about the data flow...")
    new_tokens, cached_tokens = generate_with_cache(cache.name, "Describe the data flow from hotkey press to output.")
    total_tokens_with_cache += new_tokens
    print(f"   Cached Tokens (Discounted): {cached_tokens}")
    print(f"   New Tokens Billed (Full Price): {new_tokens}")

    print(f"\n>>> Total Tokens Billed (With Cache): {total_tokens_with_cache}")

    # Step 3: Clean up
    print("\nDeleting the cache to stop storage costs...")
    genai.caching.CachedContent.delete(name=cache.name)
    print("   Cache deleted.")

    # --- FINAL RESULTS ---
    print("\n" + "="*50)
    print("Benchmark Results")
    print("="*50)
    print(f"Total Tokens WITHOUT Caching: {total_tokens_without_cache}")
    print(f"Total Tokens WITH Caching:    {total_tokens_with_cache}")
    
    cost_saving_percentage = ((total_tokens_without_cache - total_tokens_with_cache) / total_tokens_without_cache) * 100
    print(f"\n>>> Cost Saving: {cost_saving_percentage:.2f}%")
    print("\nThis demonstrates that for a session with multiple queries against the same large context,")
    print("the one-time cost of creating the cache is quickly offset, leading to significant savings.")

if __name__ == "__main__":
    run_benchmark()