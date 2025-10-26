import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional


def run_command(command: str, cwd: Optional[Path] = None) -> None:
    """Run a shell command and exit if it fails."""
    print(f"[CMD] {command}")
    try:
        subprocess.run(
            command,
            shell=True,
            check=True,
            executable="/bin/bash",
            cwd=str(cwd) if cwd is not None else None,
        )
    except subprocess.CalledProcessError as exc:
        print(
            f"Error: Command '{command}' failed with exit code {exc.returncode}",
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Setup the environment for SuGaR")
    parser.add_argument(
        "--no_nvdiffrast",
        action="store_true",
        help="Skip installation of Nvdiffrast",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent

    print("--- [STEP 1/3] Creating the complete conda environment... ---")
    environment_file = project_root / "environment.yml"
    run_command(f"conda env create -f '{environment_file}'", cwd=project_root)
    print("--- Conda environment created successfully. ---")

    run_in_sugar = "conda run -n sugar"
    pip_build_editable = "bash -c 'CUDA_HOME=$CONDA_PREFIX pip install -e .'"
    pip_build_standard = "bash -c 'CUDA_HOME=$CONDA_PREFIX pip install .'"

    print("\n--- [STEP 2/3] Building C++/CUDA extensions... ---")

    print("Building 3D Gaussian Splatting rasterizer...")
    rasterizer_dir = project_root / "gaussian_splatting/submodules/diff-gaussian-rasterization"
    run_command(f"{run_in_sugar} {pip_build_editable}", cwd=rasterizer_dir)
    print("3D Gaussian Splatting rasterizer installed.")

    print("Building simple-knn...")
    simple_knn_dir = project_root / "gaussian_splatting/submodules/simple-knn"
    run_command(f"{run_in_sugar} {pip_build_editable}", cwd=simple_knn_dir)
    print("simple-knn installed.")

    if args.no_nvdiffrast:
        print("Skipping Nvdiffrast installation.")
    else:
        print("Building Nvdiffrast...")
        nvdiffrast_dir = project_root / "nvdiffrast"
        if not nvdiffrast_dir.exists():
            run_command(
                "git clone https://github.com/NVlabs/nvdiffrast",
                cwd=project_root,
            )
        run_command(f"{run_in_sugar} {pip_build_standard}", cwd=nvdiffrast_dir)
        print("Nvdiffrast installed.")

    print("\n--- [STEP 3/3] SuGaR installation complete. ---")
    print("\nTo activate the environment, run: conda activate sugar")


if __name__ == "__main__":
    main()
