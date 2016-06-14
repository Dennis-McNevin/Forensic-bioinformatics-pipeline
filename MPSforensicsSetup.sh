MPSFOR="$HOME/mpsforensics"

cd
[ -d $MPSFOR ] || git clone https://cameronjack@bitbucket.org/gdu_jcsmr/mpsforensics.git

cd  $MPSFOR
. install_user.sh
