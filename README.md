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
    * pip install torch==1.5.0+cu101 torchvision==0.6.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html

**Setup environment variables:**

   * source /data/dhelm/python_virtenv/vhh_core_env/bin/activate
   * export CUDA_VISIBLE_DEVICES=0
   * export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-10.1/lib64/
   * export CUDA_HOME=/usr/local/cuda-10.1
   * export PATH=$PATH:/usr/local/cuda-10.1/bin
   * export PYTHONPATH=$PYTHONPATH:/XXX/vhh_core/:/XXX/vhh_core/Develop/:/XXX/vhh_core/Demo/
   * export PYTHONPATH=$PYTHONPATH:/home/dhelm/VHH_Releases/vhh_core/vhh_core/:/home/dhelm/VHH_Releases/vhh_core/vhh_core/Develop/:/home/dhelm/VHH_Releases/vhh_core/vhh_core/Demo/
   
**Install opencv with nonfree libs**
   
   * You have to install opencv from source (because of nonfree methods such as SIFT,SURF,...)
   * refer to opencv installation guide: https://linuxize.com/post/how-to-install-opencv-on-ubuntu-18-04/
   * USE cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/home/dhelm/thirdpartylibs/opencv/install_opencv -D PYTHON_DEFAULT_EXECUTABLE=/home/dhelm/virtual_env/test_opencv_venv/bin/python -D PYTHON_INCLUDE_DIRS=/home/dhelm/virtual_env/test_opencv_venv/include -D PYTHON_PACKAGES_PATH=/home/dhelm/virtual_env/test_opencv_venv/lib/python3.6/site-packages -D PYTHON_EXECUTABLE=/home/dhelm/virtual_env/test_opencv_venv/bin/python -D PYTHON_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython3.6m.so.1 -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON -D OPENCV_GENERATE_PKGCONFIG=ON -D OPENCV_EXTRA_MODULES_PATH=/home/dhelm/thirdpartylibs/opencv/opencv_contrib/modules -D OPENCV_ENABLE_NONFREE=ON -D BUILD_PYTHON_SUPPORT=ON -D BUILD_EXAMPLES=ON  .. 

**Run demo script**

   * change to root directory of the repository
   * python Demo/run_automatic_annotation_process.py

## Docker Setup instructions

NOT AVAILABLE YET