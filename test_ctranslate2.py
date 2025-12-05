import ctranslate2
print(f"ctranslate2: {ctranslate2.__version__}")
print(f"CUDA device count: {ctranslate2.get_cuda_device_count()}")
