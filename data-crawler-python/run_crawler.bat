@echo off
echo Cleaning database...
cd scripts
python clean_db.py
cd ..

echo.
echo Running crawler...
python -m src.main

echo.
echo Done!
pause 