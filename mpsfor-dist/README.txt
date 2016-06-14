The MPSforensics.zip file contains 3 files:
* install_mpsforensics.sh
* install_user.sh
* README.txt (this file)

A system administrator needs to run the install_mpsforensics.sh 
script on the system before a user can use this system. This installs 
essential system components and then calls the install_user.sh script 
which setups a dedicated user installation and all the associated 
program files for the pipelines.

To install it on your own Ubuntu 14.04.4 LTS or Ubuntu 16.04 LTS installation:

1) You can either download it directly on the Ubuntu computer using a web 
browser, or copy it using a memory stick from another machine.

2) Place the install_mpsforensics.sh file on the Desktop.
 
You will need to use the command line to install it, but this isn't 
too hard to do...

3) On the left hand side of the screen is the Task Bar. At the top of 
the Task Bar is a purple and white icon, which when you move mouse over 
it, says "Search your computer". Click on this icon.

4) A window will appear next to the button. At the top of this is an 
empty text box. Click in this, and type (without the quotes) "terminal".

5) Now a header will appear directly under the text box that 
reads "Applications", and under this is a black and white icon 
and the words underneath read "Terminal". Click on this icon.

6) A command-line terminal should appear and present you with a prompt 
that looks like:
 
username@computername"~$
 
The ~ symbol means you are in your home folder. 
 
7) At the $ prompt type the following and press the Enter key (don't 
type the $ sign):
 
$ bash Desktop/install_mpsforensics.sh
 
8) 6 lines of text will appear, the last one reads:
 
[sudo] password for username:
 
The username shown will be your username, not the actual word. Here 
you need to type the password for your account and press the Enter 
key when you are done. This lets the installer set up system-wide 
software libraries. When you type the password the characters will 
not appear on the screen. This is to protect you from people watching 
over your shoulder, but it also means it's easy to mistype it. Don't 
worry if you get it wrong, just try again. If you get it wrong three 
times the installation will fail, but you can simply repeat 
instruction (7) to try again.
 
9) The installation should run to completion. Depending on the speed 
of your internet connection the installation should take between 5 
and 20 minutes. If the a download breaks then just repeat from 
step (7) to try again. The installer only downloads what it doesn't 
already have. 

If it completes successfully you see one the last messages 
"Installation of MPS Forensics pipeline complete".
 
10) There will now be two new links on your Desktop. 
a) The first is an icon with the name "MPSforensics.sh" - double 
clicking this icon will start the MPS Forensics software, as well 
as the Meteor web engine and the IGV genome browser.
b) The second is link with the name "MPS_results" - double clicking 
this will open the /home/username/mpsforensics/results folder, which 
is where all the pipeline runs are placed by default.

To install the pipeline for extra users on the same computer, an 
administrator can put the MPSforensicsSetup.sh script on the user's
Desktop. They can double click it to install the application for 
their own use.
