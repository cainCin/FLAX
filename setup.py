#!/usr/bin/env python
import os
import platform

from setuptools import find_packages, setup

platform_system = platform.system()

# LIB_REPORT_VERSION = os.getenv("LIB_REPORT_VERSION") or "v2.0.3-greport-extend"
LAYOUT_MODEL = os.getenv("LAYOUT_MODEL") or "jeff"
OCR_MODEL = os.getenv("OCR_MODEL") or "cannet"
TABLE_MODEL = os.getenv("TABLE_MODEL") or "tee"
KV_MODEL = os.getenv("KV_MODEL") or "graph"

LIB_LAYOUT_VERSION = os.getenv("LIB_LAYOUT_VERSION") or "prj_tohmatsu-dev"
LIB_OCR_VERSION = os.getenv("LIB_OCR_VERSION") or "prj_tohmatsu-dev"
LIB_TABLE_VERSION = os.getenv("LIB_TABLE_VERSION") or "v1.2.2"
LIB_KV_VERSION = os.getenv("LIB_KV_VERSION") or "prj_invoice_phase4"
LIB_RULEBASED_VERSION = os.getenv("LIB_RULEBASED_VERSION") or "prj_invoice_phase4"


pypi_packages = [
    "Pillow>=6,<7",
    "azure-storage-blob==2.0.1",
    "click==7.0",
    "distance==0.1.3",
    "jaconv==0.2.4",
    "jinja2>=2.10,<2.11",
    "opencv-contrib-python>=3.4.5.20,<4",
    "opencv-python>=3.4.5.20,<4",
    "pdf2image==1.5.4",
    "progress==1.5",
    "python-box==3.4.6",
    "python-dotenv<=0.10.3",
    "regex==2019.6.8",
    "rootpath==0.1.1",
    "torch==1.7.0",
    "torchaudio==0.7.0",
    "torchvision==0.8.1",
    "dynaconf==2.2.3",
    "fuzzywuzzy",
    "fuzzysearch==0.7.3",
]

cinnamon_libs = [
    f"cassia@git+ssh://git@github.com/Cinnamon/cassia.git@v1.1.2-alpha",
    f"niq@git+ssh://git@github.com/Cinnamon/niq@v1.2.1",
    f"lib-layout[{LAYOUT_MODEL}]@git+ssh://git@github.com/Cinnamon/lib-layout.git@{LIB_LAYOUT_VERSION}",
    f"lib-ocr[{OCR_MODEL}]@git+ssh://git@github.com/Cinnamon/lib-ocr.git@{LIB_OCR_VERSION}",
    f"lib-table[{TABLE_MODEL}]@git+ssh://git@github.com/Cinnamon/lib-table.git@{LIB_TABLE_VERSION}",
    f"lib-rulebased@git+ssh://git@github.com/Cinnamon/lib_rulebased.git@{LIB_RULEBASED_VERSION}",
    f"lib-kv@git+ssh://git@github.com/Cinnamon/lib-kv-graph@{LIB_KV_VERSION}",
]

setup(
    name="FLAX_AI",
    description="",
    version="0.0.1",
    packages=find_packages(exclude=["docs", "tests*"]),
    include_package_data=True,
    package_data={
        "prj_tohmatsu": ["utility/fonts/simsun.ttc"],
    },
    install_requires=pypi_packages + cinnamon_libs,
    extras_require={"dev": ["ipdb", "ipython", "jsonschema", "pytest", "dvc[s3]"]},
    python_requires=">=3.6",
)