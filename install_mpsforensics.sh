#!/bin/bash

# NGS build script for Ubuntu (with a non-working
# code branch for Fedora).

# All applications are owned by their respective
# authors and are subject to their own licenses.

# The MPS Forensics Pipeline project is copyright of
# the UC National Centre for Forensic Studies.

# All platform code was developed and is owned by the 
# ANU Bioinformatics Consultancy.

# Installer by Cameron Jack, ANU 2016.
# Must be run with root privileges, but all code is
# placed under $HOME/mpsforensics, which simplifies both
# installation and data security concerns.

# Supported platforms: Ubuntu 14.04.4 LTS, 16.04 LTS

set -x
set -e

cd "$HOME"

if python -mplatform | grep -qi ubuntu
then
    # required on Ubuntu 14.04.14 LTS or 16.04 LTS
    sudo add-apt-repository -y ppa:openjdk-r/ppa
#    sudo apt-get update -y
    sudo apt-get install -y gcc
    sudo apt-get install -y g++
    sudo apt-get install -y gfortran
    sudo apt-get install -y build-essential linux-headers-`uname -r` dkms
    sudo apt-get install -y cmake
    sudo apt-get install -y zlib1g-dev
    sudo apt-get install -y openjdk-8-jdk
    sudo apt-get install -y samtools
    sudo apt-get install -y bwa
    sudo apt-get install -y python-tk
    sudo apt-get install -y vcftools
    sudo apt-get install -y bedtools
    sudo apt-get install -y curl
    sudo apt-get install -y mongodb
    sudo apt-get install -y libgsl2
    sudo apt-get install -y gsl-bin
    sudo apt-get install -y firefox
    sudo apt-get install -y git
    # we need Chrome to fully support meteor
    if [ ! -f "$HOME/google-chrome-stable_current_amd64.deb" ] ; then 
      cd "$HOME"
      wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb  
      sudo dpkg -i google-chrome-stable_current_amd64.deb
      sudo apt-get install -y -f
    fi

else
    # required on Fedora - this is not up to date and needs more testing
    yum install -y dnf
    dnf install -y gcc
    dnf install -y gcc-c++
    dnf install -y gcc-gfortran
    dnf install -y java-1.8.0-openjdk
    dnf install -y kernel-devel-`uname -r`
    dnf install -y samtools
    dnf install -y bwa
    dnf install -y tkinter
    dnf install -y vcftools
    dnf install -y curl
    dnf install -y mongodb
    dnf install -y gsl-devel
    #dnf install -y firefox
fi

# Pull down application
if [ ! -d "$HOME/mpsforensics" ] ; then
  git clone https://cameronjack@bitbucket.org/gdu_jcsmr/mpsforensics.git
  cd mpsforensics
  mkdir results
fi

cd "$HOME/mpsforensics"

if [ ! -d "$HOME/mpsforensics/human" ] ; then
  # Pull down BWA indexed human reference
  wget https://cloudstor.aarnet.edu.au/plus/index.php/s/nLGwa9lBuiQCARc/download
  mv download hg19.tgz
  tar -xzf hg19.tgz
  rm hg19.tgz
  # wget https://www.dropbox.com/s/p47hqi8zde3qmqn/hg19.tgz
fi

if [ ! -d "$HOME/mpsforensics/lobstr_ref" ] ; then
  # Pull down LobSTR prebuilt
  wget https://cloudstor.aarnet.edu.au/plus/index.php/s/NsZYhN2m7WS2RoA/download
  mv download lobstr_ref.tgz
  tar -xzf lobstr_ref.tgz
  rm lobstr_ref.tgz
  # wget https://www.dropbox.com/s/2asy40bx9agfjhk/lobstr.tgz
fi

if [ ! -d "$HOME/.meteor" ] ; then
  # Pull down prebuilt meteor
  #wget https://cloudstor.aarnet.edu.au/plus/index.php/s/cF63EohzFRcjD22/download
  #mv download meteor.tgz
  #tar -xzf meteor.tgz
  #rm meteor.tgz
  #mv meteor "$HOME/.meteor"
  #cp "$HOME/mpsforensics/meteor" /usr/local/bin/meteor
  curl https://install.meteor.com/ | sh
fi
  cd "$HOME/mpsforensics/viewer"
if [ ! -d "$HOME/mpsforensics/viewer/.meteor" ]; then
  meteor create .
fi
./install_meteor.sh
cd "$HOME/mpsforensics"

# Pull down mpsforensics_bin supporting binaries
if [ ! -d "$HOME/mpsforensics/mpsforensics_bin" ] ; then
  wget https://cloudstor.aarnet.edu.au/plus/index.php/s/SI91o90UGCkkGFN/download
  mv download mpsforensics_bin.tgz
  tar -xzf mpsforensics_bin.tgz
  rm mpsforensics_bin.tgz
fi

# install binaries as needed: FASTQC, Trimmomatic, LobSTR, STRaitRazor, Freebayes
cd "$HOME/mpsforensics/mpsforensics_bin"

# FASTQC
unzip -o fastqc_v0.11.5.zip
cd FastQC
chmod +x fastqc
if [ ! -f "/usr/local/bin/fastqc" ]; then
  ln "$HOME/mpsforensics/mpsforensics_bin/FastQC/fastqc" /usr/local/bin/fastqc
fi
cd ..

# Trimmomatic
unzip -o Trimmomatic-0.36.zip
if [ ! -f "/usr/share/java/trimmomatic-0.36.jar" ]; then
  ln "$HOME/mpsforensics/mpsforensics_bin/Trimmomatic-0.36/trimmomatic-0.36.jar" /usr/share/java/trimmomatic-0.36.jar
fi

# Freebayes
if [ ! -f "/usr/local/bin/freebayes" ]; then
  tar -xzf freebayes-v1.0.2.tgz
  cd freebayes
  make clean
  make
  sudo make install
  cd ..
fi

# LobSTR v4
tar -xzf lobSTR-bin-Linux-x86_64-4.0.0.tar.gz
if [ -f "/usr/local/bin/allelotype" ]; then
  ln "$HOME/mpsforensics/mpsforensics_bin/lobSTR-bin-Linux-x86_64-4.0.0/bin/allelotype" /usr/local/bin/allelotype
fi
if [ -f "/usr/local/bin/lobSTR" ]; then
  ln "$HOME/mpsforensics/mpsforensics_bin/lobSTR-bin-Linux-x86_64-4.0.0/bin/lobSTR" /usr/local/bin/lobSTR
fi

# STRait Razor v2.5
unzip -o STRaitRazorv2.zip
if [ ! -d "$HOME/mpsforensics/STRaitRazorv2.5" ]; then
  mkdir "$HOME/mpsforensics/STRaitRazorv2.5"
fi
mv STRaitRazorv2.5/Newest_STRait_Razor/* "$HOME/mpsforensics/STRaitRazorv2.5/."
cd "$HOME/mpsforensics/STRaitRazorv2.5"
chmod +x ppss
tar -xzf tre-0.8.0.tar.gz
cd tre-0.8.0
./configure --prefix="$HOME/mpsforensics/"
make clean
make
make install
cd "$HOME/mpsforensics/mpsforensics_bin"

# IGV
if [ ! -d "$HOME/mpsforensics/IGV_2.3.67" ]; then
  tar -xzf IGV_2.3.67.tgz
  mv IGV_2.3.67 "$HOME/mpsforensics/IGV_2.3.67"
fi

# Picard tools
if [ ! -d "$HOME/mpsforensics/picard-tools-2.2.1" ]; then
  tar -xzf picard-tools-2.2.1.tgz
  mv picard-tools-2.2.1 "$HOME/mpsforensics/picard-tools-2.2.1"
fi

# set paths in application
cd "$HOME/mpsforensics"
./install.sh

# create application links
if [ ! -f "$HOME/Desktop/MPSforensics.sh" ]; then
  echo '#!/bin/bash' > "$HOME/Desktop/MPSforensics.sh"
  echo "python $HOME/mpsforensics/forensics.py" >> "$HOME/Desktop/MPSforensics.sh"
  chmod +x "$HOME/Desktop/MPSforensics.sh"
fi

if [ ! -L "$HOME/Desktop/MPS_results" ]; then
  ln -s "$HOME/mpsforensics/results" "$HOME/Desktop/MPS_results"
fi

cd "$HOME"

echo "Installation of MPS Forensics pipeline complete"

### End of mpsforensics installer script ###



