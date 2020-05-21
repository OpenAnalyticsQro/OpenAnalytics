# install- pip install -e .
# it can never hurt to re-install. Just run pip install -e . again.
import setuptools

setuptools.setup(
    name="OpenAnalytics",
    version="0.0.1",
    author="OpenAnalytics Dev",
    author_email="openanalytics.qro@gmail.com",
    description="OpenAnalytics",
    long_description="OpenAnalytics",
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=[],    # add all requierements txt
    python_requires='>=3.6',
)
