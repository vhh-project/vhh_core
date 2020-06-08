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
