from setuptools import setup, find_packages

setup(
    name = "ccpoviz",
    version = "0.0.1",
    packages = find_packages(),
    scripts = ['scripts/ccpoviz'],

    install_requires = [
        'docutils>=0.3',
        'pystache>=0.5',
        ],

    package_data = {
        'ccpoviz': ['data/*.json', 'data/*.dat'],
    },

    # metadata for upload to PyPI
    author = "Tschijnmo TSCHAU",
    author_email = "tschijnmotschau@gmail.com",
    description = "Command-line batch molecular visualizer",
    license = "MIT",
    keywords = "visualization, chemistry",
    url = "http://tschijnmo.github.io/ccpoviz",

)
