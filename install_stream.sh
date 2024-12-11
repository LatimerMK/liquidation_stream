#!/bin/bash

# bash <(curl -s https://raw.githubusercontent.com/LatimerMK/liquidation_stream/main/install_stream.sh)

curl -s https://raw.githubusercontent.com/LatimerMK/bash-install/refs/heads/main/tools/logo.sh | bash

# Оновлення пакунків
echo "Оновлення системи..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Встановлення Python та pip
echo "Встановлення Python3 і pip..."
sudo apt-get install python3 python3-pip python3-venv git -y

# Клонуємо репозиторій
echo "Клонуємо репозиторій..."
git clone https://github.com/LatimerMK/liquidation_stream.git

# Перехід в каталог з проєктом
cd l_stream

# Створення віртуального середовища
echo "Створення віртуального середовища..."
python3 -m venv venv
source venv/bin/activate

# Встановлення залежностей
echo "Встановлення залежностей..."
pip install -r requirements.txt

# Створення скрипта для запуску програми
echo "Створення скрипта для запуску..."
cat <<EOT > start.sh
#!/bin/bash
# Активуємо віртуальне середовище і запускаємо програму
source ~/liquidation_stream/venv/bin/activate
python3 main.py
EOT

# Робимо start.sh виконуваним
chmod +x l_stream.sh

# Підсумок
echo "Установка завершена. Для запуску програми використовуйте './start.sh'."
