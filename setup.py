from setuptools import setup

setup(
    name='GammaLab',
    version='0.0.1',
    description='Toolkit for soundcard gamma ray spectroscopy',
    author='F.I. Pelupessy',
    url='https://github.com/ipelupessy/gammalab',
    license='GPL',
    packages=['gammalab'],
    package_data={},
    install_requires=['numpy','pyaudio'],
    python_requires='>=2.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GPL',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: High Energy Physics',
    ],
    long_description=open('README.rst').read(),
)
