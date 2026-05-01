from setuptools import setup, find_packages

setup(
    name="comfyui-dep-resolver",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1",
        "rich>=13.0",
    ],
    entry_points={
        "console_scripts": [
            "comfyui-dep-resolver=comfyui_dep_resolver.cli:cli",
        ],
    },
    python_requires=">=3.9",
    author="darshd9941",
    description="npm install for ComfyUI workflows — resolve missing nodes, auto-install",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/darshd9941/comfyui-dep-resolver",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics",
    ],
)
