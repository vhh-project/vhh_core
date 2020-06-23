FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04

RUN apt-get update -y && \
    apt-get install -y git python3-pip python3-dev

COPY ./requirements.txt /requirements.txt

WORKDIR /

RUN pip3 install opencv-python
RUN pip3 install torch==1.5.0+cu101 torchvision==0.6.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html
RUN pip3 install -r requirements.txt

COPY . /

ENTRYPOINT [ "python3" ]

ENV PYTHONPATH "${PYTHONPATH}:/home/dhelm/VHH_Develop/pycharm_vhh_core/"

CMD [ "pip list" ]
CMD [ "Demo/run_automatic_annotation_process.py" ]


#ADD kerasTest2.py /home/dhelm/abgaben_cvsp/cvsp_1526648/Demo/demo_0.py   /
#RUN apt update && apt install python python-pip libyaml-dev -y
#RUN pip install tensorflow-gpu keras
#CMD [ "python", "/home/dhelm/abgaben_cvsp/cvsp_1526648/Demo/demo_0.py" ]





