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
# placed under ~/mpsforensics, which simplifies both
# installation and data security concerns.

# Supported platforms: Ubuntu 14.04.4 LTS, 16.04 LTS

cd ~

if python -mplatform | grep -qi ubuntu
then
    # required on Ubuntu 14.04.14 LTS or 16.04 LTS
    add-apt-repository -y ppa:openjdk-r/ppa
    apt-get update -y
    apt-get install -y gcc
    apt-get install -y g++
    apt-get install -y gfortran
    apt-get install -y build-essential linux-headers-`uname -r` dkms
    apt-get install -y cmake
    apt-get install -y openjdk-8-jdk
    apt-get install -y samtools
    apt-get install -y bwa
    apt-get install -y python-tk
    apt-get install -y vcftools
    apt-get install -y bedtools
    apt-get install -y curl
    apt-get install -y mongodb
    apt-get install -y libgsl2
    apt-get install -y gsl-bin
    apt-get install -y firefox
    apt-get install -y git
    # we need Chrome to fully support meteor
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb  
    sudo dpkg -i google-chrome-stable_current_amd64.deb
    sudo apt-get install -y -f

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
if [ ! -d "~/mpsforensics" ] ; then
  git clone https://cameronjack@bitbucket.org/gdu_jcsmr/mpsforensics.git
  cd mpsforensics
  mkdir results
fi

cd ~/mpsforensics

if [ ! -d "~/mpsforensics/human" ] ; then
  # Pull down BWA indexed human reference
  wget https://cloudstor.aarnet.edu.au/plus/index.php/s/nLGwa9lBuiQCARc/download
  mv download hg19.tgz
  tar -xzf hg19.tgz
  rm hg19.tgz
  # wget https://www.dropbox.com/s/p47hqi8zde3qmqn/hg19.tgz
fi

if [ ! -d "~/lobstr_ref" ] ; then
  # Pull down LobSTR prebuilt
  wget https://cloudstor.aarnet.edu.au/plus/index.php/s/NsZYhN2m7WS2RoA/download
  mv download lobstr_ref.tgz
  tar -xzf lobstr_ref.tgz
  rm lobstr_ref.tgz
  # wget https://www.dropbox.com/s/2asy40bx9agfjhk/lobstr.tgz
fi

if [ ! -d "~/.meteor" ] ; then
  # Pull down prebuilt meteor
  wget https://cloudstor.aarnet.edu.au/plus/index.php/s/cF63EohzFRcjD22
  mv download meteor.tgz
  tar -xzf meteor.tgz
  rm meteor.tgz
  mv meteor ~/.meteor
  cp ~/mpsforensics/meteor /usr/local/bin/meteor
fi

# Pull down mpsforensics_bin supporting binaries
if [ ! -d "~/mpsforensics/mpsforensics_bin" ] ; then
  wget https://cloudstor.aarnet.edu.au/plus/index.php/s/SI91o90UGCkkGFN/download
  mv download mpsforensics_bin.tgz
  tar -xzf mpsforensics_bin.tgz
  rm mpsforensics_bin.tgz
fi

# install binaries as needed: FASTQC, Trimmomatic, LobSTR, STRaitRazor, Freebayes
cd ~/mpsforensics/mpsforensics_bin

# FASTQC
unzip fastqc_v0.11.5.zip
cd FastQC
chmod +x fastqc
ln ~/mpsforensics/mpsforensics_bin/FastQC/fastqc /usr/local/bin/fastqc
cd ..

# Trimmomatic
unzip Trimmomatic-0.36.zip
cd Trimmomatic-0.36
ln ~/mpsforensics/mpsforensics_bin/Trimmomatic-0.36/trimmomatic-0.36.jar /usr/share/java/trimmomatic-0.36.jar
cd ..

# Freebayes
tar -xzf freebayes-v1.0.2.tar.gz
cd freebayes-v1.0.2
make
make install
cd ..

# LobSTR v4
tar -xzf lobSTR-bin-Linux-x86_64-4.0.0.tar.gz
ln ~/mpsforensics/mpsforensics_bin/lobSTR-bin-Linux-x86_64-4.0.0/bin/allelotype /usr/local/bin/allelotype
ln ~/mpsforensics/mpsforensics_bin/lobSTR-bin-Linux-x86_64-4.0.0/bin/lobSTR /usr/local/bin/lobSTR

# STRait Razor v2.5
unzip STRaitRazorv2.zip
mv STRaitRazorv2.5/Newest_STRait_Razor/ ~/mpsforensics/STRaitRazorv2.5
cd ~/mpsforensics/STRaitRazor
chmod +x ppss
tar -xzf tre-0.8.0.tar.gz
cd tre-0.8.0
./configure --prefix=/usr/local
make
make install
cd ~/mpsforensics/mpsforensics_bin

# IGV
tar -xzf IGV_2.3.67.tgz
mv IGV_2.3.67 ~/mpsforensics/IGV_2.3.67

### End of mpsforensics installer script ###



