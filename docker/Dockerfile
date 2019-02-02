# Runtime for https://github.com/icemoon1987/stock_features

FROM centos

LABEL maintainer "icemoon1987 <panwenhai1987@163.com>"

RUN mkdir /tmp/software

# Install pip
RUN curl https://bootstrap.pypa.io/get-pip.py -o /tmp/software/get-pip.py
RUN python /tmp/software/get-pip.py

# Install python packages
RUN pip install progressbar2
RUN pip install pandas
RUN pip install tushare
RUN pip install bs4

# Clean up
RUN rm -rf /tmp/software

