
set -ex

MPSFOR="$HOME/mpsforensics"

cd

# Pull down application
# Dev repo held by ANU Bioinformatics Consultancy
#[ -d "$MPSFOR" ] || git clone https://cameronjack@bitbucket.org/gdu_jcsmr/mpsforensics.git
# Production repo held by UC CFFS
[ -d "$MPSFOR" ] || git clone https://github.com/Dennis-McNevin/Forensic-bioinformatics-pipeline.git

cd "$MPSFOR"
mkdir -p results bin lib

# Pull down BWA indexed human reference
if [ ! -f .human-done ] ; then
  curl https://cloudstor.aarnet.edu.au/plus/index.php/s/7i9TqFBIKZCtrPL/download | tar -xzf -
  touch .human-done
fi

cd $MPSFOR

# Pull down LobSTR prebuilt
if [ ! -f .lobstr_ref-done ] ; then
  curl https://cloudstor.aarnet.edu.au/plus/index.php/s/hsEux0bosXjtcnB/download | tar -xzf -
  touch .lobstr_ref-done
fi

cd $MPSFOR

if [ ! -d "$HOME/.meteor" ] ; then
  curl https://install.meteor.com/ | sh
fi
cd "$MPSFOR/viewer"
if [ ! -d "$MPSFOR/viewer/.meteor" ]; then
  meteor create .
fi
if [ ! -f .meteor-done ] ; then
  ./install_meteor.sh
  touch .meteor-done
fi

cd "$MPSFOR"

# Pull down mpsforensics_bin supporting binaries
if [ ! -f .bin-done ] ; then
  # dev repo
  # curl https://cloudstor.aarnet.edu.au/plus/index.php/s/SI91o90UGCkkGFN/download | tar -xzf -
  curl https://cloudstor.aarnet.edu.au/plus/index.php/s/b7DLXSR3uINHPVY/download | tar -xzf -
  touch .bin-done
fi

# install binaries: FASTQC, Trimmomatic, LobSTR, STRaitRazor, Freebayes
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

if [ ! -f $HOME/Desktop/MPSfor.desktop ] ; then
  [ -d $HOME/Desktop ] || mkdir $HOME/Desktop
  cat >$HOME/Desktop/MPSfor.desktop <<-EOM
	[Desktop Entry]
	Name=MPS Forensics
	Comment=Start the MPS Forensic GUI
	# Exec=bash -c "python $HOME/mpsforensics/forensics.py ; read -p 'Done? ' ans"
	Exec=python $MPSFOR/forensics.py
	Icon=$MPSFOR/mpsfor-dist/MPSforIcon.png
	Terminal=false
	Type=Application
	Categories=Application
EOM
  chmod ug+x $HOME/Desktop/MPSfor.desktop
fi

if [ ! -L "$HOME/Desktop/MPS_results" ]; then
  ln -s "$MPSFOR/results" "$HOME/Desktop/MPS_results"
fi

echo "Installation of MPS Forensics pipeline completed"

### End of mpsforensics installer script ###
