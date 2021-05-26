#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from distutils.core import Command
from setuptools import setup, find_packages
from packaging import version
import torch
from torch.utils.cpp_extension import BuildExtension, CUDAExtension
import os.path
import os

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()

with open(os.path.join('msd_pytorch', 'VERSION')) as version_file:
    version = version_file.read().strip()

requirements = [
    # Add your project's requirements here, e.g.,
    "tifffile",
    "imageio"
]

setup_requirements = [
    'pytest-runner'
]

test_requirements = [
    'pytest'
]

dev_requirements = [
    'autopep8',
    'rope',
    'jedi',
    'flake8',
    'importmagic',
    'autopep8',
    'black',
    'yapf',
    'snakeviz',
    # Documentation
    'sphinx',
    'sphinx_rtd_theme',
    'recommonmark',
    # Other
    'watchdog',
    'coverage',
    'pytest',
    'pytest-runner'
]


class EmitNinjaCommand(Command):
    """A custom command to emit Ninja build files."""

    user_options = []
    description = 'emit ninja build file'

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        """Run command."""
        try:
            from torch.utils.cpp_extension import _write_ninja_file_and_build
            emit_ninja = _write_ninja_file_and_build
        except ImportError:
            from torch.utils.cpp_extension import _write_ninja_file_and_build_library
            emit_ninja = _write_ninja_file_and_build_library

        for e in self.distribution.ext_modules:
            output_dir = f"./ninja_{e.name}"
            os.makedirs(output_dir, exist_ok=True)

            nvcc_flags = e.extra_compile_args['nvcc']
            # Using these flags, ninja can detect changes in included header files.
            # This makes incremental builds substantially faster.
            nvcc_flags = nvcc_flags + ["-MMD", "-MF", "$out.d"]

            emit_ninja(
                name=e.name,
                sources=e.sources,
                extra_cflags=None,       # TODO:
                extra_cuda_cflags=nvcc_flags,
                extra_ldflags=e.extra_link_args,
                extra_include_paths=e.include_dirs,
                build_directory=output_dir,
                verbose=True,
                with_cuda=None,     # auto-detects CUDA
            )



def __nvcc_args():
    return []
    gxx = os.environ.get('GXX')
    recent_torch_version = version.parse("1.7") <= version.parse(torch.__version__)
    # Old versions of pytorch did not add the -ccbin command-line option.
    if gxx is not None and not recent_torch_version:
        print("AAH: Added ccbin command-line argument")
        return ['-ccbin', gxx]
    else:
        return []


setup(
    author="Allard Hendriksen",
    author_email='allard.hendriksen@cwi.nl',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="An implementation of Mixed-Scale Dense networks in PyTorch. ",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='msd_pytorch',
    name='msd_pytorch',
    packages=find_packages(include=['msd_pytorch']),
    setup_requires=setup_requirements,
    test_suite='msd_pytorch.tests',
    tests_require=test_requirements,
    extras_require={'dev': dev_requirements},
    url='https://github.com/ahendriksen/msd_pytorch',
    version=version,
    zip_safe=False,
    ext_modules=[
        CUDAExtension(
            name='msd_custom_convolutions',
            sources=[
                'msd_pytorch/msd_custom_convolutions.cpp',
                'msd_pytorch/msd_custom_convolutions/torch_cuda_dispatch.cu',
                # 2D kernels:
                'msd_pytorch/msd_custom_convolutions/conv2d_backward_k.cu',
                'msd_pytorch/msd_custom_convolutions/conv2d_backward_bias.cu',
                'msd_pytorch/msd_custom_convolutions/conv2d_backward_x.cu',
                'msd_pytorch/msd_custom_convolutions/conv2d_forward.cu',
                # 3D kernels:
                'msd_pytorch/msd_custom_convolutions/conv3d_backward_bias.cu',
                'msd_pytorch/msd_custom_convolutions/conv3d_backward_k.cu',
                'msd_pytorch/msd_custom_convolutions/conv3d_backward_x.cu',
                'msd_pytorch/msd_custom_convolutions/conv3d_forward.cu',
            ],
            extra_compile_args={
                'cxx': [],
                'nvcc': __nvcc_args(),
            },
        ),
    ],
    cmdclass={
        'build_ext': BuildExtension,
        'emit_ninja': EmitNinjaCommand,
    },
)
