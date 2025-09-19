import os
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup the environment')
    
    parser.add_argument('--no_nvdiffrast', action='store_true', help='Skip installation of Nvdiffrast')
    args = parser.parse_args()
    
    # Create a new conda environment
    print("[INFO] Creating the conda environment for SuGaR...")
    os.system("conda env create -f environment.yml")
    print("[INFO] Conda environment created.")

    run_in_sugar = "conda run -n sugar "

    print("\n--- [STEP 2/4] Installing compilers and CUDA toolkit... ---")
    
    # Install C++ compiler (g++)
    os.system(f'{run_in_sugar} conda install -y -c conda-forge gxx_linux-64=11.2.0')
    
    # Install CUDA compiler (nvcc)
    os.system(f'{run_in_sugar} conda install -y -c "nvidia/label/cuda-11.8.0" cuda-compiler')
    
    # Force-install the FULL CUDA toolkit with headers/libs from the NVIDIA channel
    os.system(f'{run_in_sugar} conda install -y "nvidia/label/cuda-11.8.0::cudatoolkit"')

    pip_build_editable = "bash -c 'CUDA_HOME=$CONDA_PREFIX pip install -e .'"
    pip_build_standard = "bash -c 'CUDA_HOME=$CONDA_PREFIX pip install .'"
    
    # Install 3D Gaussian Splatting rasterizer
    print("[INFO] Installing the 3D Gaussian Splatting rasterizer...")
    os.chdir("gaussian_splatting/submodules/diff-gaussian-rasterization/")
    os.system(f"{run_in_sugar} {pip_build_editable}")
    print("[INFO] 3D Gaussian Splatting rasterizer installed.")
    
    # Install simple-knn
    print("[INFO] Installing simple-knn...")
    os.chdir("../simple-knn/")
    os.system(f"{run_in_sugar} {pip_build_editable}")
    print("[INFO] simple-knn installed.")
    os.chdir("../../../")
    
    # Install Nvdiffrast
    if args.no_nvdiffrast:
        print("[INFO] Skipping installation of Nvdiffrast.")
    else:
        print("[INFO] Installing Nvdiffrast...")
        os.system("git clone https://github.com/NVlabs/nvdiffrast")
        os.chdir("nvdiffrast")
        os.system(f"{run_in_sugar} {pip_build_standard}")
        print("[INFO] Nvdiffrast installed.")
        print("[INFO] Please note that Nvdiffrast will take a few seconds or minutes to build the first time it is used.")
        os.chdir("../")

    print("[INFO] SuGaR installation complete.")
