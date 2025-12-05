"""Test faster-whisper model loading WITH Qt initialized"""
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("Testing faster-whisper model loading WITH Qt")
logger.info("=" * 80)

try:
    logger.info("\n1. Initializing Qt...")
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    
    # Enable high-DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Test")
    logger.info("✅ Qt initialized")
    
    logger.info("\n2. Importing faster_whisper...")
    from faster_whisper import WhisperModel
    logger.info("✅ Import successful")
    
    logger.info("\n3. Attempting to load model...")
    logger.info("Model: tiny")
    logger.info("Device: cpu")
    logger.info("Compute Type: int8")
    logger.info("Download Root: models")
    
    model = WhisperModel(
        "tiny",
        device="cpu",
        compute_type="int8",
        download_root="models",
        num_workers=1,
        cpu_threads=1
    )
    
    logger.info("✅ Model loaded successfully!")
    logger.info(f"Model type: {type(model)}")
    
except Exception as e:
    logger.error(f"❌ Error: {e}", exc_info=True)
    sys.exit(1)

logger.info("\n" + "=" * 80)
logger.info("Test completed successfully")
logger.info("=" * 80)
