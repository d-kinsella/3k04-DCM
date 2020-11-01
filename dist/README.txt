##INSTALLATION INSTRUCTIONS##
-	Install python version 3.7.7 from https://www.python.org/downloads/release/python-377/
	or by using a python version control manager (such as pyenv)
	**Other versions may work fine but have not been tested
-	Navigate to this DCM-group1 folder in the command line
-	Install requirements with the following command(s) in the command line:
*optional	python -m venv ./venv
*optional	.\venv/scripts\activate
		python -m pip install -r requirements.txt
-	Start the DCM server with the following commands in the command line:
		cd src
		python __init__.py
-	open localhost:5000 in the browser of your choice
-	Enjoy :)
*** The server WILL NOT RUN if there is a directory with a number in the path leading to this folder
*** (for example, a folder named 3k04). If you run into this issue, please try moving this DCM-group1 
*** folder to the desktop and repeating the above steps.