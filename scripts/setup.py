"""Setup script for ML Competition Framework."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README (at project root; fallback when only scripts/ is present, e.g. Kaggle)
readme_path = Path(__file__).resolve().parent.parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else "ML Competition Framework."

setup(
    name="kaggle-ml-comp-scripts",
    version="0.1.0",
    author="ML Competition Framework Contributors",
    description="Unified ML competition framework for vision and tabular tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="."),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "scipy>=1.10.0",
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "timm>=0.9.0",
        "albumentations>=1.3.0",
        "Pillow>=10.0.0",
        "pyyaml>=6.0",
        "tqdm>=4.65.0",
        "psutil>=5.8.0",
        "lightgbm>=4.0.0",
        "xgboost>=2.0.0",
        "h5py>=3.6.0",
    ],
    extras_require={
        "vision": [
            "opencv-python>=4.5.0",
            "transformers>=4.30.0",
        ],
        "tabular": [
            "catboost>=1.0.0",
            "biopython>=1.81.0",
            "obonet>=1.3.0",
            "networkx>=3.0",
        ],
        "notebook": [
            "ipywidgets>=7.6.0",
            "jupyter>=1.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
