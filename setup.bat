@echo off
pixi shell
python -m ensure pip
python -m pip install --upgrade pip
pip install PyQt6