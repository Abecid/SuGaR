#!/usr/bin/env python3
import os
import argparse
import subprocess
from pathlib import Path

def run(cmd, cwd=None):
    print(f"\n$ {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd)
    if res.returncode != 0:
        raise SystemExit(f"[ERROR] Command failed: {cmd}")

def main():
    parser = argparse.ArgumentParser(description="Setup the SuGaR environment")
    parser.add_argument('--no_nvdiffrast', action='store_true', help='Skip installation of Nvdiffrast')
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    os.chdir(repo_root)

    # 0) Create env from environment.yml
    print("[INFO] Creating conda env 'sugar' from environment.yml ...")
    run("conda env create -f environment.yml")

    # Helper: run inside 'sugar' with bash -l to load conda env properly
    def in_env(cmd, cwd=None):
        run(f"""conda run -n sugar bash -lc '{cmd}'""", cwd=cwd)

    print("\n--- [STEP 1/3] Toolchain inside the env (GCC-11 + CUDA 11.8) ---")
    # 1) Correct compiler (GCC-11)
    run('conda run -n sugar conda install -y -c conda-forge gxx_linux-64=11.2.0')

    # 2) Correct CUDA toolkit + NVCC 11.8 (avoid system CUDA 12.x)
    run('conda run -n sugar conda install -y -c "nvidia/label/cuda-11.8.0" cuda-toolkit=11.8.0 cuda-nvcc=11.8.89')

    # Common exports for building extensions (kept minimal + explicit)
    exports = r'''
export CUDA_HOME="$CONDA_PREFIX";
export PATH="$CUDA_HOME/bin:$PATH";
export CC="$(which x86_64-conda-linux-gnu-gcc || which gcc)";
export CXX="$(which x86_64-conda-linux-gnu-g++ || which g++)";
export NVCC_APPEND_FLAGS="--compiler-bindir=$CXX";
'''

    print("\n[INFO] Sanity check: nvcc / torch CUDA versions (inside env)")
    in_env(exports + "which nvcc && nvcc -V || true")
    in_env('python - <<PY\nimport torch, os\nprint(\"torch:\", torch.__version__)\nprint(\"torch.version.cuda:\", torch.version.cuda)\nprint(\"CUDA_HOME:\", os.environ.get(\"CUDA_HOME\"))\nPY')

    print("\n--- [STEP 2/3] Build CUDA extensions ---")

    # 3D Gaussian Splatting rasterizer
    print("[INFO] Installing diff-gaussian-rasterization (editable)...")
    dgr_path = repo_root / "gaussian_splatting" / "submodules" / "diff-gaussian-rasterization"
    in_env(exports + "pip install -e .", cwd=str(dgr_path))

    # simple-knn
    print("[INFO] Installing simple-knn (editable)...")
    sknn_path = repo_root / "gaussian_splatting" / "submodules" / "simple-knn"
    in_env(exports + "pip install -e .", cwd=str(sknn_path))

    # Nvdiffrast (optional)
    if args.no_nvdiffrast:
        print("[INFO] Skipping nvdiffrast.")
    else:
        print("[INFO] Installing nvdiffrast...")
        nvd_path = repo_root / "nvdiffrast"
        if not nvd_path.exists():
            run("git clone --depth=1 https://github.com/NVlabs/nvdiffrast nvdiffrast")
        in_env(exports + "pip install .", cwd=str(nvd_path))
        print("[INFO] nvdiffrast installed. (First use will JIT a bit.)")

    print("\n--- [STEP 3/3] Final verification ---")
    in_env(exports + "python - <<PY\n"
          "import torch, os\n"
          "print('CUDA available:', torch.cuda.is_available())\n"
          "print('Device count:', torch.cuda.device_count())\n"
          "print('torch.version.cuda:', torch.version.cuda)\n"
          "print('CUDA_HOME:', os.environ.get('CUDA_HOME'))\n"
          "PY")

    print("\n[INFO] SuGaR installation complete. You're good to go.")

if __name__ == "__main__":
    main()
