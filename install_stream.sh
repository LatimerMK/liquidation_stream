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
cd liquidation_stream

# Створення віртуального середовища
echo "Створення віртуального середовища..."
mkdir .venv
python3 -m venv .venv
source .venv/bin/activate

# Встановлення залежностей
echo "Встановлення залежностей..."
pip install -r requirements.txt

# Створення скрипта для запуску програми
echo "Створення скрипта для запуску..."
cat <<EOT > start.sh
#!/bin/bash
# Активуємо віртуальне середовище і запускаємо програму
source ~/liquidation_stream/.venv/bin/activate
python3 main.py
EOT

echo "Створення скрипта для запуску Tmux..."
cat <<EOT > start_tmux.sh
#!/bin/bash
# Створення нової сесії tmux
tmux new-session -d -s liq_stream

# Запуск команд у tmux сесії
tmux send-keys -t liq_stream "source ~/liquidation_stream/.venv/bin/activate" C-m
tmux send-keys -t liq_stream "python3 main.py" C-m
tmux send-keys -t echo "tmux new-session -d -s liq_stream"

tmux send-keys -t liq_stream "echo 'Створення нової сесії: tmux new-session -d -s liq_stream'" C-m
tmux send-keys -t liq_stream "echo 'Вхід в сесію: tmux attach -t liq_stream'" C-m
tmux send-keys -t liq_stream "echo 'Щоб вийти з сесії Ctrl + b, потім d'" C-m
tmux send-keys -t liq_stream "echo 'Закриття сесії з середини: exit'" C-m

# Підключення до сесії для моніторингу
tmux attach -t liq_stream
EOT

# Робимо start.sh виконуваним
chmod +x start.sh

# Підсумок
echo "Налаштування config.json,"
echo "Установка завершена. Для запуску програми використовуйте './start.sh' './start_tmux.sh'."

# на випадок проблем з бібліотеками AttributeError: module 'websocket' has no attribute 'WebSocketApp'
# pip install --force-reinstall websocket-client