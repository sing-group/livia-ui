import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="livia-ui",
    version="0.1.dev62",
    author="Fernando Campos Tato, Miguel Reboiro-Jato, Daniel Glez-Peña, Florentino Fdez-Riverola, Rubén Domínguez Carbajales, Hugo López-Fdez, Alba Nogueira-Rodríguez",
    author_email="fctato@esei.uvigo.es, mrjato@uvigo.es, dgpena@uvigo.es, riverola@uvigo.es, RUBEN.DOMINGUEZ.CARBAJALES@sergas.es, hlfernandez@uvigo.es, alnogueira@uvigo.es",
    description="User interfaces for the LIVIA framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://dev.sing-group.org/gitlab/polydeep/livia-ui",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "livia-core==0.1.dev79",
        "PySide2==5.15.2"
    ],
    extras_require={
        'dev': [
            'pyroma==3.2',
            'mypy==0.931',
            'twine==3.8.0',
            'packaging==21.3'
        ]
    },
    dependency_links=[
        "https://maven.sing-group.org/repository/python-snapshots/simple/livia-core/"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Scientific/Engineering :: Medical Science Apps."
    ],
    python_requires='>=3.7',
)
