#
# Copyright (C) 2023, Inria
# GRAPHDECO research group, https://team.inria.fr/graphdeco
# All rights reserved.
#
# This software is free for non-commercial, research and evaluation use 
# under the terms of the LICENSE.md file.
#
# For inquiries contact  george.drettakis@inria.fr
#

from setuptools import setup
import os
import shutil
import torch.utils.cpp_extension as torch_cpp_extension


def _has_nvcc(cuda_home: str) -> bool:
    """Return True when ``nvcc`` exists inside ``cuda_home``."""
    if not cuda_home:
        return False
    return os.path.exists(os.path.join(cuda_home, "bin", "nvcc"))


cuda_home = torch_cpp_extension.CUDA_HOME
if not _has_nvcc(cuda_home):
    nvcc_path = shutil.which("nvcc")
    if nvcc_path:
        cuda_home = os.path.dirname(os.path.dirname(nvcc_path))
        torch_cpp_extension.CUDA_HOME = cuda_home
        os.environ.setdefault("CUDA_HOME", cuda_home)

CUDAExtension = torch_cpp_extension.CUDAExtension
BuildExtension = torch_cpp_extension.BuildExtension
os.path.dirname(os.path.abspath(__file__))

setup(
    name="diff_gaussian_rasterization",
    packages=['diff_gaussian_rasterization'],
    ext_modules=[
        CUDAExtension(
            name="diff_gaussian_rasterization._C",
            sources=[
            "cuda_rasterizer/rasterizer_impl.cu",
            "cuda_rasterizer/forward.cu",
            "cuda_rasterizer/backward.cu",
            "rasterize_points.cu",
            "ext.cpp"],
            extra_compile_args={"nvcc": ["-I" + os.path.join(os.path.dirname(os.path.abspath(__file__)), "third_party/glm/")]})
        ],
    cmdclass={
        'build_ext': BuildExtension
    }
)
