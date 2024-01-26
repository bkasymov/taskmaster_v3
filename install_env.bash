#!/bin/bash

# Проверка наличия Python 3.10
if command -v python3.10 &>/dev/null; then
    echo "Python 3.10 is installed."
else
    echo "Python 3.10 is not installed. Please install it and run the script again."
    exit 1
fi

# Переменная для имени виртуального окружения
venv_name="myenv"

# Проверка существования виртуального окружения
if [ -d "$venv_name" ]; then
    echo "Virtual environment $venv_name already exists."
else
    # Создание виртуального окружения
    python3.10 -m venv $venv_name
    echo "Virtual environment $venv_name created."
fi

# Активация виртуального окружения
source $venv_name/bin/activate

# Установка зависимостей из requirements.txt
pip install -r requirements.txt
pip install --upgrade pip

mkdir result
# Сообщение о завершении
echo "Всё готово. Ваше виртуальное окружение активировано, и зависимости установлены."

