#!/bin/bash
# Скрипт для остановки бота

# Находим PID процесса
BOT_PID=$(pgrep -f "python3 spy.py")

if [ -z "$BOT_PID" ]; then
    echo "Бот не запущен."
else
    echo "Останавливаем бота (PID: $BOT_PID)..."
    kill $BOT_PID
    echo "Бот остановлен."
fi
