import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="livia-ui",
    version="0.1.dev8",
    author="Fernando Campos Tato, Miguel Reboiro-Jato, Daniel Glez-Peña, Florentino Fdez-Riverola, Rubén Domínguez Carbajales, Hugo López-Fdez, Alba Nogueira-Rodríguez",
    author_email="fctato@esei.uvigo.es, mrjato@uvigo.es, dgpena@uvigo.es, riverola@uvigo.es, RUBEN.DOMINGUEZ.CARBAJALES@sergas.es, hlfernandez@uvigo.es, alnogueira@uvigo.es",
    description="User interfaces for the LIVIA framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://dev.sing-group.org/gitlab/polydeep/livia-ui",
    packages=setuptools.find_packages(),
    install_requires=[
        "livia-core==0.1.dev33",
        "pyqt5==5.14.2"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Scientific/Engineering :: Medical Science Apps."
    ],
    python_requires='>=3.7',
)
