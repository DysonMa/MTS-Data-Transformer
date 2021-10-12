@echo off
cmd /c "pip install virtualenv & virtualenv venv & cd /d .\venv\Scripts & activate & cd /d ../../src & pip install -r requirements.txt"