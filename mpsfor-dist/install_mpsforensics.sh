#!/bin/bash

# MPS build script for Ubuntu (with a non-working
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

set -e

# create the setup script if its isn't already present
if [ "$HOME" != / -a ! -f ./MPSforensicsSetup.sh ] ; then
  cat >./MPSforensicsSetup.sh <<-EOM
	MPSFOR="\$HOME/mpsforensics"

	cd
	[ -d \$MPSFOR ] || git clone https://cameronjack@bitbucket.org/gdu_jcsmr/mpsforensics.git

	cd  \$MPSFOR
	. install_user.sh
EOM
  chmod a+x MPSforensicsSetup.sh
fi

if [ -f /etc/mpsforensics.log ] ; then
  echo "MPSforensics admin. install was started, but it did not finish."
  read -p "Do you want to resume the admin. install [Y/n]? " ans
  if [ ans == Y ] ; then
    # make sure we can write to the log file
    sudo touch /etc/mpsforensics.log
    sudo chown $USER /etc/mpsforensics.log
    sudo chmod u+w /etc/mpsforensics.log
    echo resuming ...
  else
    echo "Please email the /etc/mpsforensics.log file to the system developers."
    exit 1
  fi
fi

if [ ! -f /etc/mpsforensics-done.log ] ; then
  # Admin. install not yet complete; start/resume admin. install

  echo; date

  set -x

  cd	# go to $HOME directory

  if python -mplatform | grep -qi ubuntu
  then
      # required on Ubuntu 14.04.14 LTS or 16.04 LTS
  #    sudo apt-get update -y
      sudo apt-get install -y git
      sudo apt-get install -y firefox
      sudo apt-get install -y python-tk
      sudo apt-get install -y gcc
      sudo apt-get install -y g++
      sudo apt-get install -y gfortran
      sudo apt-get install -y build-essential linux-headers-`uname -r` dkms
      sudo apt-get install -y cmake
      sudo apt-get install -y zlib1g-dev
      sudo add-apt-repository -y ppa:openjdk-r/ppa
      sudo apt-get install -y openjdk-8-jdk
      sudo apt-get install -y samtools
      sudo apt-get install -y bwa
      sudo apt-get install -y vcftools
      sudo apt-get install -y bedtools
      sudo apt-get install -y curl
      sudo apt-get install -y mongodb
      sudo apt-get install -y libgsl2
      sudo apt-get install -y gsl-bin
      # we need Chrome to fully support meteor
#      if [ ! -f "$HOME/google-chrome-stable_current_amd64.deb" ] ; then 
#        cd "$HOME"
#        wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb  
#        sudo dpkg -i google-chrome-stable_current_amd64.deb
#        sudo apt-get install -y -f
#      fi
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
  sudo mv /etc/mpsforensics.log /etc/mpsforensics-done.log
fi | tee -a /etc/mpsforensics.log

[ $HOME != / ] && {
  . ./MPSforensicsSetup.sh | tee ~/.mpsforensics.log 
  mv ~/.mpsforensics.log ~/mpsforensics/.mpsforensics.log
}

read -p "Done! Press ENTER/RETURN when you are ready." ans
