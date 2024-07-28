#! /bin/bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
pyinstaller read_to_clipboard.py --name=read_statement
deactivate
rm -r env
mv dist/read_statement $HOME
rm -r build
rm -r dist
rm read_statement.spec