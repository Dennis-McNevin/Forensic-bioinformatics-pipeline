
set -ex

MPSFOR="$HOME/mpsforensics"

cd

# Pull down application
[ -d "$MPSFOR" ] || git clone https://cameronjack@bitbucket.org/gdu_jcsmr/mpsforensics.git

cd "$MPSFOR"
mkdir -p results bin lib

# Pull down BWA indexed human reference
if [ ! -d human ] ; then
  [ -d human_tmp ] || mkdir human_tmp
  cd human_tmp
  wget -c https://cloudstor.aarnet.edu.au/plus/index.php/s/nLGwa9lBuiQCARc/download
  mv download ../hg19.tgz
  cd $MPSFOR
  rmdir human_tmp
  tar -xzf hg19.tgz
  rm hg19.tgz
  # wget https://www.dropbox.com/s/p47hqi8zde3qmqn/hg19.tgz
fi

cd $MPSFOR

if [ ! -d "$MPSFOR/lobstr_ref" ] ; then
  # Pull down LobSTR prebuilt
  [ -d lobstr_tmp ] || mkdir lobstr_tmp
  cd lobstr_tmp
  wget -c https://cloudstor.aarnet.edu.au/plus/index.php/s/NsZYhN2m7WS2RoA/download
  mv download ../lobstr_ref.tgz
  cd $MPSFOR
  rmdir lobstr_tmp
  tar -xzf lobstr_ref.tgz
  rm lobstr_ref.tgz
  # wget https://www.dropbox.com/s/2asy40bx9agfjhk/lobstr.tgz
fi

cd $MPSFOR

if [ ! -d "$HOME/.meteor" ] ; then
  # Pull down prebuilt meteor
  #wget https://cloudstor.aarnet.edu.au/plus/index.php/s/cF63EohzFRcjD22/download
  #mv download meteor.tgz
  #tar -xzf meteor.tgz
  #rm meteor.tgz
  #mv meteor "$HOME/.meteor"
  #cp "$MPSFOR/meteor" /usr/local/bin/meteor
  curl https://install.meteor.com/ | sh
fi
cd "$MPSFOR/viewer"
if [ ! -d "$MPSFOR/viewer/.meteor" ]; then
  meteor create .
fi
./install_meteor.sh

cd "$MPSFOR"

# Pull down mpsforensics_bin supporting binaries
if [ ! -d "$HOME/mpsforensics/mpsforensics_bin" ] ; then
  wget https://cloudstor.aarnet.edu.au/plus/index.php/s/SI91o90UGCkkGFN/download
  mv download mpsforensics_bin.tgz
  tar -xzf mpsforensics_bin.tgz
  rm mpsforensics_bin.tgz
fi

# install binaries as needed: FASTQC, Trimmomatic, LobSTR, STRaitRazor, Freebayes
cd "$MPSFOR/mpsforensics_bin"

# FASTQC
if [ ! -f "$MPSFOR/bin/fastqc" ]; then
  unzip -o fastqc_v0.11.5.zip
  chmod +x FastQC/fastqc
  #ln "$MPSFOR/mpsforensics_bin/FastQC/fastqc" "$MPSFOR/bin/fastqc"
fi

# Trimmomatic
if [ ! -f "$MPSFOR/lib/trimmomatic-0.36.jar" ]; then
  unzip -o Trimmomatic-0.36.zip
  ln "$MPSFOR/mpsforensics_bin/Trimmomatic-0.36/trimmomatic-0.36.jar" "$MPSFOR/lib/trimmomatic-0.36.jar"
fi

# Freebayes
if [ ! -f "$MPSFOR/bin/freebayes" ]; then
  tar -xzf freebayes-v1.0.2.tgz
  cd freebayes
  # make clean # surely this is not needed ... and it breaks the install
  make
  ln bin/freebayes bin/bamleftalign "$MPSFOR/bin"
  #sudo make install
fi

cd "$MPSFOR/mpsforensics_bin"

# LobSTR v4
tar -xzf lobSTR-bin-Linux-x86_64-4.0.0.tar.gz
if [ ! -f "$MPSFOR/bin/allelotype" ]; then
  ln "$MPSFOR/mpsforensics_bin/lobSTR-bin-Linux-x86_64-4.0.0/bin/allelotype" "$MPSFOR/bin/allelotype"
fi
if [ ! -f "$MPSFOR/bin/lobSTR" ]; then
  ln "$MPSFOR/mpsforensics_bin/lobSTR-bin-Linux-x86_64-4.0.0/bin/lobSTR" "$MPSFOR/bin/lobSTR"
fi

# STRait Razor v2.5
if [ ! -d "$MPSFOR/STRaitRazorv2.5" ] ; then
  unzip -o STRaitRazorv2.zip
  mkdir -p "$MPSFOR/STRaitRazorv2.5" 
  mv STRaitRazorv2.5/Newest_STRait_Razor/* "$MPSFOR/STRaitRazorv2.5/."
  cd "$MPSFOR/STRaitRazorv2.5"
  patch < $MPSFOR/forensicsapp/STRaitRazor.patch
  chmod +x ppss
  tar -xzf tre-0.8.0.tar.gz
  cd tre-0.8.0
  ./configure --prefix="$MPSFOR/"
  # make clean 
  make
  make install
  cd ..
  rm -rf tre-0.8.0
fi 

cd "$MPSFOR/mpsforensics_bin"

# IGV
if [ ! -d "$MPSFOR/IGV_2.3.67" ]; then
  tar -xzf IGV_2.3.67.tgz
  mv IGV_2.3.67 "$MPSFOR/IGV_2.3.67"
fi

# Picard tools
if [ ! -d "$MPSFOR/picard-tools-2.2.1" ]; then
  tar -xzf picard-tools-2.2.1.tgz
  mv picard-tools-2.2.1 "$MPSFOR/picard-tools-2.2.1"
fi

# set paths in application
cd "$MPSFOR"
./locater.sh

# create application links
if [ ! -f "$HOME/Desktop/MPSforensics.sh" ]; then
  echo '#!/bin/bash' > "$HOME/Desktop/MPSforensics.sh"
  echo "python $MPSFOR/forensics.py" >> "$HOME/Desktop/MPSforensics.sh"
  chmod +x "$HOME/Desktop/MPSforensics.sh"
fi

if [ ! -L "$HOME/Desktop/MPS_results" ]; then
  ln -s "$MPSFOR/results" "$HOME/Desktop/MPS_results"
fi

echo "Installation of MPS Forensics pipeline completed"

### End of mpsforensics installer script ###
