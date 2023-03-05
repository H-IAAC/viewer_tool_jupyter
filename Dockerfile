# VERSION: 0.1.0
# DESCRIPTION: Basic extensible Jupyter Notebook/Lab Container
# BUILD: docker build --rm -t docker-jupyter-extensible .

FROM jupyter/minimal-notebook 








# install other dependencies
# 
# For quick experimentation, you can also install Python packages with
# pip by including the package references in requirements.txt.
# However, the recommended way to add packages is in the section above.
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt



