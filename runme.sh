python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
mkdir images
mkdir logs
touch images/picture.png
ruff format   
python3 uadmuter.py

