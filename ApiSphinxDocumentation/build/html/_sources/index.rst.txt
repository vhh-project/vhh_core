.. vhh_core documentation master file, created by
   sphinx-quickstart on Wed May  6 18:41:33 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Introduction
============

Detecting cinematographic techniques such as Shot Boundary Detection (SBD), Shot Type Classification (STC) and Camera
Movements Classification (CMC) is a fundamental task for automatic film archival. Therefore, a software framework is
developed to process historical films related to the time of the liberation phase of Nazi concentration camps during
the Second World War [`Visual History of the Holocaust`_ (VHH)]. This framework is able to detect and classify SBDs
(`vhh_sbd`_), STCs (`vhh_stc`_) and CMCs (`vhh_cmc`_) by using deep learning-based as well as optical flow-based
approaches [XX][XX][XX]. This documentation is separated into the following sections: In Section *System Overview* and
*Process Pipeline* an overview of the code structure as well as the automatic annotation process pipeline is demonstrated.
Furthermore, the package structure and the setup and usage description is visualized in Section *Package Structure* and
*Setup Instructions*. Finally, this documentation closes with an API description of all classes, modules and their
members in Section *API Description*.

System Overview
===============

The software architecture is visualized in the below figure. The `vhh_core`_ is divided in multiple classes. The core
class is called *MainController* and administers the external plugin modules for automatic shot analysis in historical
films: `vhh_sbd`_ (SBD), `vhh_stc`_ (STC) and `vhh_cmc`_ (CMC). Moreover, central functionality such as the communication
with the VHH-MMSI system is handled in this class. The class *VhhRestApi* includes methods to communicate with the
VHH-MMSI database via RestAPI endpoints. A various number of parameters defined and set in the *config_core.yaml*
file is managed by the class *Configuration*. Furthermore, each shot analysis plugin can be configured with separate
configuration files stored in the *./config* folder in this repositories.

.. only:: latex

   .. figure:: ../figures/software_architecture_core.pdf
      :align: center

.. only:: html

   .. figure:: ../figures/software_architecture_core.png
      :align: center

Process Pipeline
================

.. only:: latex

   .. figure:: ../figures/process_pipeline_core.pdf
      :align: center

.. only:: html

   .. figure:: ../figures/process_pipeline_core.png
      :align: center

Package Overview
================

The following list gives an overview of the folder structure of this python repository:

*name of repository*: vhh_core

   * **ApiSphinxDocumentation/**: includes all files to generate the documentation as well as the created documentations (html, pdf). The results are stored in the build folder (e.g. xx/build/latex/vhh_core.pdf)
   * **config/**: This folder includes the required configuration file. For each plugin (sbd, stc, cmc, ...) there is one subdirectory holding the corresponding configuration file.
   * **Demo/**: This folder includes a all scripts to run this application. Furthermore, scripts to setup the folder structure (video and results storage) as well as to setup the environment for running this application.
   * **Develop/**: This folder includes additional scripts used during developing phase of this application. (e.g. the document_builder script to generate the package documentation).
   * **README.md**: This file gives a brief description of this repository (e.g. link to this documentation)
   * **requirements.txt**: this file holds all python dependencies and is needed to install the package in your own virtual environment
   * **setup.py**: this script is needed to install the stc package in your own virtual environment

Setup  instructions
===================

This package includes a setup.py script and a requirements.txt file which are needed to install this package for custom applications.
The following instructions have to be done to used this library in your own application:

**Requirements:**

   * Ubuntu 18.04 LTS
   * CUDA 10.1 + cuDNN
   * python version 3.6.x

**Create a virtual environment:**

   * create a folder to a specified path (e.g. /xxx/vhh_core/)
   * python3 -m venv /xxx/vhh_core/

**Activate the environment:**

   * source /xxx/vhh_core/bin/activate

**Checkout vhh_core repository to a specified folder:**

   * git clone https://github.com/dahe-cvl/vhh_core

**Install the stc package and all dependencies:**

   * change to the root directory of the repository (includes setup.py)
   * python setup.py install

.. note::

  You can check the success of the installation by using the commend *pip list*. This command should give you a list with all installed python packages and it should include *vhh_core*

.. note::

   Currently there is an issue in the *setup.py* script. Therefore the pytorch libraries have to be installed manually by running the following command:
   *pip install torch==1.5.0+cu101 torchvision==0.6.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html*


Parameter Description
=====================

.. autoyaml:: ../config/CORE/config.yaml


API Description
===============

This section gives an overview of all classes and modules in *vhh_core* as well as a brief configuration parameter description.

.. toctree::
   :maxdepth: 4

   Configuration.rst
   Sbd.rst
   Stc.rst
   Video.rst
   VhhRestApi.rst
   MainController.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

References
==========
.. target-notes::

.. _`Visual History of the Holocaust`: https://www.vhh-project.eu/
.. _`vhh_core`: https://github.com/dahe-cvl/vhh_core
.. _`vhh_sbd`: https://github.com/dahe-cvl/vhh_sbd
.. _`vhh_stc`: https://github.com/dahe-cvl/vhh_stc
.. _`vhh_cmc`: https://github.com/dahe-cvl/vhh_cmc


