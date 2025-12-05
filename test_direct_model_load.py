"""Test direct faster-whisper model loading"""
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("Testing faster-whisper model loading")
logger.info("=" * 80)

try:
    logger.info("Importing faster_whisper...")
    from faster_whisper import WhisperModel
    logger.info("✅ Import successful")
    
    logger.info("\nAttempting to load model...")
    logger.info("Model: distil-medium.en")
    logger.info("Device: cpu")
    logger.info("Compute Type: int8")
    logger.info("Download Root: models")
    
    model = WhisperModel(
        "distil-medium.en",
        device="cpu",
        compute_type="int8",
        download_root="models",
        num_workers=4,
        cpu_threads=4
    )
    
    logger.info("✅ Model loaded successfully!")
    logger.info(f"Model type: {type(model)}")
    
except Exception as e:
    logger.error(f"❌ Error: {e}", exc_info=True)
    sys.exit(1)

logger.info("\n" + "=" * 80)
logger.info("Test completed successfully")
logger.info("=" * 80)
