FROM registry.centos.org/centos:8


# pipeline deps
RUN yum -y install git python3 python3-flask python3-requests
# pipeline plugins deps
RUN yum -y install python2 python2-lxml
# pipeline tests
RUN yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
RUN yum -y install make python3-pylint diffutils
# tclib deps
RUN yum -y install python3-yaml
# bugzilla plugin deps
RUN yum -y install python3-bugzilla

# fetch other libraries and tools
WORKDIR /root
RUN git clone https://github.com/rhinstaller/tclib.git

# set up git
RUN git config --global user.email "nobody@example.com"
RUN git config --global user.name "Nobody"
