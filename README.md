# vhh_core

This package represents the Automatic Video Analysis Framework (AVAF) for the H2020 project Visual History of the 
Holocaust. It includes various video analysis techniques (e.g. Shot Boundary Detection, Shot Type Classfication and 
Camera Movements Classification).

## Package Description

PDF format: [vhh_core_pdf](https://github.com/dahe-cvl/vhh_core/blob/master/ApiSphinxDocumentation/build/latex/vhhcorepackageautomaticvideoanalysisframeworkvhh_core.pdf)
    
HTML format (only usable if repository is available in local storage): [vhh_core_html](https://github.com/dahe-cvl/vhh_core/blob/master/ApiSphinxDocumentation/build/html/index.html)

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
   * export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-10.1/lib64/
   * export CUDA_HOME=/usr/local/cuda-10.1
   * export PATH=$PATH:/usr/local/cuda-10.1/bin
   * export PYTHONPATH=$PYTHONPATH:/XXX/vhh_core/:/XXX/vhh_core/Develop/:/XXX/vhh_core/Demo/

**Run demo script**

   * change to root directory of the repository
   * python Demo/run_automatic_annotation_process.py

## Docker Setup instructions

NOT AVAILABLE YET