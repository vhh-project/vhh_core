# vhh_core
VHH DL Framework Core Module

## Package Description

PDF format: [vhh_core_pdf](https://github.com/dahe-cvl/vhh_core/blob/master/ApiSphinxDocumentation/build/latex/vhhcorepackageautomaticvideoanalysisframeworkvhh_core.pdf)
    
HTML format (only usable if repository is available in local storage): [vhh_core_html](https://github.com/dahe-cvl/vhh_core/blob/master/ApiSphinxDocumentation/build/html/index.html)
    
requirements:

    1) install vhh related modules into virtual environment
    
    # make virtual environment
    mkdir PATH_to/vhh_core_venv
    python3 -m venv PATH_to/vhh_core_venv
    source PATH_to/vhh_core_venv/bin/activate
    
    # clone all repositories
    cd PATH_to/vhh_pkgs
    git clone https://github.com/dahe-cvl/vhh_sbd.git
    
    # install each repo
    cd vhh_sbd
    python setup.py install
    
    # check if repos are installed successfully
    pip list 
    

    2) set environment variables
 
    exports CUDA_VISIBLE_DEVICES=0
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-10.1/lib64/
    export CUDA_HOME=/usr/local/cuda-10.1
    export PATH=$PATH:/usr/local/cuda-10.1/bin


## Quick Setup

**Requirements:**

   * Ubuntu 18.04 LTS
   * python version 3.6.x

**Create a virtual environment:**

   * create a folder to a specified path (e.g. /xxx/vhh_core/)
   * python3 -m venv /xxx/vhh_core/

**Activate the environment:**

   * source /xxx/vhh_core/bin/activate

**Checkout vhh_core repository to a specified folder:**

   * git clone https://github.com/dahe-cvl/vhh_core

**Install dependencies**

    * cd /xxx/vhh_core/
    * pip install -r requirements.txt

**Setup environment variables:**

   * source /data/dhelm/python_virtenv/vhh_core_env/bin/activate
   * export CUDA_VISIBLE_DEVICES=1
   * export PYTHONPATH=$PYTHONPATH:/XXX/vhh_core/:/XXX/vhh_core/Develop/:/XXX/vhh_core/Demo/

**Run demo script**

   * change to root directory of the repository
   * python Demo/run_automatic_annotation_process.py

## Docker Setup instructions

NOT AVAILABLE YET