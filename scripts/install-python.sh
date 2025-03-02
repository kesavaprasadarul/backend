# update the package manager
apt-get update

# install git, C/C++ compiler and a text editor (I prefer vim)
apt install -y git software-properties-common curl build-essential vim

# add package source for python distributions
add-apt-repository ppa:deadsnakes/ppa

# install specific version of python with venv and distutils
apt install -y python3.11 python3.11-tk python3.11-distutils python3.11-venv postgresql-client

# get pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.11 get-pip.py