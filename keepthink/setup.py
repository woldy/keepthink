import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="keepthink",
    version="0.0.1",
    author="woldy",
    author_email="king@woldy.net",
    description="A framework for structured multi-step AI reasoning and task decomposition.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/woldy/keepthink",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.6",
    install_requires=[
        "openai>=0.27.0",  # 请根据实际需求调整版本
        "tqdm",            # 进度条（如果你的框架用到了）
        "requests",        # 网络请求（如果你的框架用到了）
    ],
    extras_require={
        "dev": ["pytest", "black", "flake8"],  # 仅供开发者使用的依赖
    },
    license="MIT",
    keywords="AI, OpenAI, task decomposition, LLM, automation",
    project_urls={
        "Documentation": "https://github.com/woldy/keepthink",
        "Source": "https://github.com/woldy/keepthink",
        "Bug Tracker": "https://github.com/woldy/keepthink/issues",
    },
)

