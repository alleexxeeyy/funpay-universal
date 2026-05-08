#!/bin/bash

# ============================================================
#  Установщик бота FunPay Universal
# ============================================================

set -e

BOT_NAME="funpayuniversal"
BOT_DIR="/root/funpayuniversal"
BOT_FILE="bot.py"
REPO_URL="https://github.com/alleexxeeyy/funpay-universal"
SERVICE_FILE="/etc/systemd/system/${BOT_NAME}.service"
PYTHON="python3.12"
CMD="fpuniversal"

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'
BOLD='\033[1m'

# Символы
CHECK="${GREEN}✔${NC}"
CROSS="${RED}✘${NC}"
ARROW="${CYAN}›${NC}"
DOT="${GRAY}·${NC}"

info()    { echo -e "  ${CYAN}  ${NC} $1"; }
success() { echo -e "  ${CHECK}  $1"; }
warn()    { echo -e "  ${YELLOW}⚠${NC}  $1"; }
error()   { echo -e "\n  ${CROSS}  ${RED}${BOLD}$1${NC}\n"; exit 1; }
step()    { echo -e "\n  ${BOLD}${WHITE}$1${NC}"; echo -e "  ${GRAY}$(printf '─%.0s' {1..44})${NC}"; }

clear

echo ""
echo -e "  ${CYAN}${BOLD}███████╗██████╗  ${NC}"
echo -e "  ${CYAN}${BOLD}██╔════╝██╔══██╗ ${NC}  ${WHITE}${BOLD}FunPay Universal${NC}"
echo -e "  ${CYAN}${BOLD}█████╗  ██████╔╝ ${NC}  ${GRAY}Установщик${NC}"
echo -e "  ${CYAN}${BOLD}██╔══╝  ██╔═══╝  ${NC}"
echo -e "  ${CYAN}${BOLD}██║     ██║      ${NC}  ${GRAY}github.com/alleexxeeyy/funpay-universal${NC}"
echo -e "  ${CYAN}${BOLD}╚═╝     ╚═╝      ${NC}"
echo ""
echo -e "  ${GRAY}$(printf '═%.0s' {1..48})${NC}"
echo ""

if [[ $EUID -ne 0 ]]; then
  error "Запустите скрипт от root: sudo bash install.sh"
fi

# ── 1. Обновление системы ────────────────────────────────────
step "Подготовка системы"
info "Обновление списка пакетов..."
apt-get update -qq
success "Система обновлена"

# ── 2. Установка git ─────────────────────────────────────────
info "Проверка git..."
if ! command -v git &>/dev/null; then
  apt-get install -y git -qq
  success "git установлен"
else
  success "git уже установлен"
fi

# ── 3. Источник файлов бота ──────────────────────────────────
step "Источник установки"
echo ""
echo -e "  ${WHITE}Откуда установить бота?${NC}"
echo ""
echo -e "  ${CYAN}${BOLD}1${NC}  ${WHITE}Скачать с GitHub${NC}  ${GRAY}(рекомендуется)${NC}"
echo -e "  ${CYAN}${BOLD}2${NC}  ${WHITE}Из локальных файлов${NC}  ${GRAY}(бот уже загружен вручную)${NC}"
echo ""
read -rp "$(echo -e "  ${CYAN}›${NC} Ваш выбор [1/2]: ")" SOURCE_CHOICE

case "$SOURCE_CHOICE" in
  1)
    echo ""
    if [[ -d "$BOT_DIR/.git" ]]; then
      info "Репозиторий найден — получаю обновления..."
      cd "$BOT_DIR" && git pull -q
      success "Репозиторий обновлён до последней версии"
    elif [[ -d "$BOT_DIR" ]]; then
      error "Папка $BOT_DIR существует, но не является git-репозиторием.\n     Удалите её: rm -rf $BOT_DIR — и запустите снова."
    else
      info "Клонирование репозитория..."
      git clone -q "$REPO_URL" "$BOT_DIR"
      success "Репозиторий скачан в $BOT_DIR"
    fi
    ;;
  2)
    echo ""
    read -rp "$(echo -e "  ${CYAN}›${NC} Путь к папке с ботом [${GRAY}$BOT_DIR${NC}]: ")" CUSTOM_DIR
    CUSTOM_DIR="${CUSTOM_DIR:-$BOT_DIR}"
    echo ""
    if [[ ! -d "$CUSTOM_DIR" ]]; then
      error "Папка не найдена: $CUSTOM_DIR"
    fi
    if [[ "$CUSTOM_DIR" != "$BOT_DIR" ]]; then
      info "Копирую файлы из $CUSTOM_DIR..."
      cp -r "$CUSTOM_DIR/." "$BOT_DIR"
      success "Файлы скопированы в $BOT_DIR"
    else
      success "Используем файлы из $BOT_DIR"
    fi
    ;;
  *)
    error "Неверный выбор. Запустите установщик снова."
    ;;
esac

if [[ ! -f "$BOT_DIR/$BOT_FILE" ]]; then
  error "Файл бота не найден: $BOT_DIR/$BOT_FILE"
fi

# ── 4. Установка Python 3.12 ─────────────────────────────────
step "Python 3.12"
info "Проверка Python 3.12..."
if ! command -v python3.12 &>/dev/null; then
  info "Устанавливаю Python 3.12..."
  apt-get install -y software-properties-common -qq
  add-apt-repository -y ppa:deadsnakes/ppa > /dev/null 2>&1
  apt-get update -qq
  apt-get install -y python3.12 python3.12-venv python3.12-distutils -qq
  success "Python 3.12 установлен"
else
  success "Python $(python3.12 --version | cut -d' ' -f2) уже установлен"
fi

# ── 5. Виртуальное окружение ─────────────────────────────────
step "Виртуальное окружение"
info "Подготовка окружения..."
cd "$BOT_DIR"
if [[ -d "venv" ]]; then
  success "Окружение уже существует — пропускаю"
else
  $PYTHON -m venv venv
  success "Виртуальное окружение создано"
fi

# ── 6. Зависимости ───────────────────────────────────────────
step "Зависимости"
if [[ -f "$BOT_DIR/requirements.txt" ]]; then
  info "Устанавливаю пакеты из requirements.txt..."
  "$BOT_DIR/venv/bin/pip" install --upgrade pip -q
  "$BOT_DIR/venv/bin/pip" install -r "$BOT_DIR/requirements.txt" -q
  success "Все зависимости установлены"
else
  warn "requirements.txt не найден — пропускаю"
fi

# ── 7. Wrapper-скрипт ────────────────────────────────────────
step "Настройка запуска"
info "Создаю wrapper-скрипт..."

cat > "${BOT_DIR}/run.sh" << 'WRAPPER'
#!/bin/bash
export PYTHONUNBUFFERED=1
export TERM=xterm-256color
cd /root/funpayuniversal
exec /root/funpayuniversal/venv/bin/python - << 'PYEOF'
import colorama.ansitowin32 as _a32
class _FakeWinTerm:
    def set_title(self, t): pass
    def set_cursor_position(self, *a, **k): pass
    def set_foreground(self, *a, **k): pass
    def set_background(self, *a, **k): pass
    def reset_all(self, *a, **k): pass
    def style(self, *a, **k): pass
_a32.winterm = _FakeWinTerm()
import colorama
colorama.init()
import runpy, sys
sys.argv = ['/root/funpayuniversal/bot.py']
runpy.run_path('/root/funpayuniversal/bot.py', run_name='__main__')
PYEOF
WRAPPER

chmod +x "${BOT_DIR}/run.sh"
success "Wrapper-скрипт создан"

# ── 8. Systemd-сервис ────────────────────────────────────────
info "Создаю systemd-сервис..."

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Telegram Bot - FunPay Universal
After=network.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=${BOT_DIR}
ExecStart=/bin/bash ${BOT_DIR}/run.sh
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${BOT_NAME}
Environment=PYTHONUNBUFFERED=1
Environment=TERM=xterm-256color

[Install]
WantedBy=multi-user.target
EOF

success "Systemd-сервис зарегистрирован"

# ── 9. Команда fpuniversal ───────────────────────────────────
info "Устанавливаю команду '${CMD}'..."

cat > /usr/local/bin/$CMD << 'BOTCMD'
#!/bin/bash
SERVICE="funpayuniversal"
BOT_DIR="/root/funpayuniversal"
CONFIG="$BOT_DIR/bot_settings/config.json"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'
BOLD='\033[1m'

is_configured() {
  [[ -f "$CONFIG" ]] || return 1
  token=$(python3 -c "import json; c=json.load(open('$CONFIG')); print(c['telegram']['api']['token'])" 2>/dev/null)
  password=$(python3 -c "import json; c=json.load(open('$CONFIG')); print(c['telegram']['bot']['password'])" 2>/dev/null)
  [[ -n "$token" && -n "$password" ]]
}

case "$1" in
  start)
    if ! is_configured; then
      echo ""
      echo -e "  ${YELLOW}⚠  Бот не настроен!${NC}"
      echo -e "  ${GRAY}Запустите настройку:${NC} ${CYAN}fpuniversal setup${NC}"
      echo ""
      exit 1
    fi
    systemctl start "$SERVICE"
    echo ""
    echo -e "  ${GREEN}✔${NC}  Бот запущен"
    echo -e "  ${GRAY}Логи:${NC} fpuniversal log"
    echo ""
    ;;
  stop)
    systemctl stop "$SERVICE"
    echo ""
    echo -e "  ${RED}■${NC}  Бот остановлен"
    echo ""
    ;;
  restart)
    if ! is_configured; then
      echo ""
      echo -e "  ${YELLOW}⚠  Бот не настроен!${NC}"
      echo -e "  ${GRAY}Запустите настройку:${NC} ${CYAN}fpuniversal setup${NC}"
      echo ""
      exit 1
    fi
    systemctl restart "$SERVICE"
    echo ""
    echo -e "  ${CYAN}↺${NC}  Бот перезапущен"
    echo -e "  ${GRAY}Логи:${NC} fpuniversal log"
    echo ""
    ;;
  status)
    echo ""
    IS_ACTIVE=$(systemctl is-active "$SERVICE" 2>/dev/null)
    IS_ENABLED=$(systemctl is-enabled "$SERVICE" 2>/dev/null)

    if [[ "$IS_ACTIVE" == "active" ]]; then
      STATUS_ICON="${GREEN}●${NC}"
      STATUS_TEXT="${GREEN}${BOLD}запущен${NC}"
    else
      STATUS_ICON="${RED}●${NC}"
      STATUS_TEXT="${RED}${BOLD}остановлен${NC}"
    fi

    if [[ "$IS_ENABLED" == "enabled" ]]; then
      AUTOSTART="${GREEN}включён${NC}"
    else
      AUTOSTART="${YELLOW}выключен${NC}"
    fi

    echo -e "  ${STATUS_ICON}  FunPay Universal — ${STATUS_TEXT}"
    echo ""
    echo -e "  ${GRAY}Автозапуск:${NC}  $AUTOSTART"

    if [[ "$IS_ACTIVE" == "active" ]]; then
      UPTIME=$(systemctl show "$SERVICE" --property=ActiveEnterTimestamp | cut -d= -f2)
      echo -e "  ${GRAY}Запущен:${NC}     $UPTIME"
    fi

    if is_configured; then
      echo -e "  ${GRAY}Конфиг:${NC}      ${GREEN}заполнен${NC}"
    else
      echo -e "  ${GRAY}Конфиг:${NC}      ${YELLOW}не заполнен${NC}  › fpuniversal setup"
    fi
    echo ""
    ;;
  log | logs)
    echo ""
    echo -e "  ${GRAY}FunPay Universal — живые логи  ${NC}${CYAN}(Ctrl+C для выхода)${NC}"
    echo -e "  ${GRAY}$(printf '─%.0s' {1..44})${NC}"
    echo ""
    journalctl -u "$SERVICE" -f --output=cat
    ;;
  log100)
    echo ""
    echo -e "  ${GRAY}FunPay Universal — последние 100 строк${NC}"
    echo -e "  ${GRAY}$(printf '─%.0s' {1..44})${NC}"
    echo ""
    journalctl -u "$SERVICE" -n 100 --output=cat
    ;;
  setup)
    echo ""
    echo -e "  ${CYAN}${BOLD}Первоначальная настройка FunPay Universal${NC}"
    echo -e "  ${GRAY}$(printf '─%.0s' {1..44})${NC}"
    echo ""
    systemctl stop "$SERVICE" 2>/dev/null || true
    cd "$BOT_DIR"
    export TERM=xterm-256color
    /root/funpayuniversal/venv/bin/python -c "
import colorama.ansitowin32 as _a32
class _FakeWinTerm:
    def set_title(self, t): pass
    def set_cursor_position(self, *a, **k): pass
    def set_foreground(self, *a, **k): pass
    def set_background(self, *a, **k): pass
    def reset_all(self, *a, **k): pass
    def style(self, *a, **k): pass
_a32.winterm = _FakeWinTerm()
import colorama; colorama.init()
import sys; sys.path.insert(0, '/root/funpayuniversal')
from utils import configure_config
configure_config()
"
    echo ""
    echo -e "  ${GREEN}✔${NC}  Настройка завершена — запускаю бота..."
    systemctl start "$SERVICE"
    sleep 1
    if systemctl is-active --quiet "$SERVICE"; then
      echo -e "  ${GREEN}✔${NC}  Бот запущен успешно"
      echo -e "  ${GRAY}Логи:${NC} fpuniversal log"
    else
      echo -e "  ${RED}✘${NC}  Не удалось запустить. Проверьте логи: fpuniversal log"
    fi
    echo ""
    ;;
  update)
    if [[ ! -d "$BOT_DIR/.git" ]]; then
      echo ""
      echo -e "  ${YELLOW}⚠${NC}  Бот установлен локально — обновление через git недоступно"
      echo ""
      exit 1
    fi
    echo ""
    echo -e "  ${CYAN}⬇${NC}  Получаю обновления с GitHub..."
    cd "$BOT_DIR" && git pull
    echo -e "  ${CYAN}◈${NC}  Обновляю зависимости..."
    /root/funpayuniversal/venv/bin/pip install -r /root/funpayuniversal/requirements.txt -q
    systemctl restart "$SERVICE"
    echo ""
    echo -e "  ${GREEN}✔${NC}  Бот обновлён и перезапущен"
    echo -e "  ${GRAY}Логи:${NC} fpuniversal log"
    echo ""
    ;;
  enable)
    systemctl enable "$SERVICE" 2>/dev/null
    echo ""
    echo -e "  ${GREEN}✔${NC}  Автозапуск при старте сервера включён"
    echo ""
    ;;
  disable)
    systemctl disable "$SERVICE" 2>/dev/null
    echo ""
    echo -e "  ${YELLOW}■${NC}  Автозапуск отключён"
    echo ""
    ;;
  *)
    echo ""
    echo -e "  ${CYAN}${BOLD}FunPay Universal${NC}  ${GRAY}управление ботом${NC}"
    echo -e "  ${GRAY}$(printf '─%.0s' {1..44})${NC}"
    echo ""
    echo -e "  ${CYAN}fpuniversal setup${NC}    ${GRAY}→${NC}  первоначальная настройка"
    echo -e "  ${CYAN}fpuniversal start${NC}    ${GRAY}→${NC}  запустить бота"
    echo -e "  ${CYAN}fpuniversal stop${NC}     ${GRAY}→${NC}  остановить бота"
    echo -e "  ${CYAN}fpuniversal restart${NC}  ${GRAY}→${NC}  перезапустить бота"
    echo -e "  ${CYAN}fpuniversal status${NC}   ${GRAY}→${NC}  статус и информация"
    echo -e "  ${CYAN}fpuniversal log${NC}      ${GRAY}→${NC}  живые логи  ${GRAY}(Ctrl+C для выхода)${NC}"
    echo -e "  ${CYAN}fpuniversal log100${NC}   ${GRAY}→${NC}  последние 100 строк"
    echo -e "  ${CYAN}fpuniversal update${NC}   ${GRAY}→${NC}  обновить с GitHub"
    echo -e "  ${CYAN}fpuniversal enable${NC}   ${GRAY}→${NC}  включить автозапуск"
    echo -e "  ${CYAN}fpuniversal disable${NC}  ${GRAY}→${NC}  выключить автозапуск"
    echo ""
    ;;
esac
BOTCMD

chmod +x /usr/local/bin/$CMD
success "Команда '${CMD}' установлена"

# ── 10. Автозапуск ───────────────────────────────────────────
step "Финальная настройка"
systemctl daemon-reload
systemctl enable "$BOT_NAME" > /dev/null 2>&1
success "Автозапуск при старте сервера включён"

# ── 11. Запуск ───────────────────────────────────────────────
CONFIG_FILE="$BOT_DIR/bot_settings/config.json"
CONFIGURED=false

if [[ -f "$CONFIG_FILE" ]]; then
  TOKEN=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['telegram']['api']['token'])" 2>/dev/null || echo "")
  PASSWORD=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['telegram']['bot']['password'])" 2>/dev/null || echo "")
  if [[ -n "$TOKEN" && -n "$PASSWORD" ]]; then
    CONFIGURED=true
  fi
fi

if [[ "$CONFIGURED" == "true" ]]; then
  info "Конфиг заполнен — запускаю бота..."
  systemctl start "$BOT_NAME"
  sleep 2
  if systemctl is-active --quiet "$BOT_NAME"; then
    success "Бот запущен!"
  else
    warn "Бот не запустился — проверьте логи: fpuniversal log"
  fi
fi

# ── Итог ─────────────────────────────────────────────────────
echo ""
echo ""
echo -e "  ${GRAY}$(printf '═%.0s' {1..48})${NC}"
echo ""
echo -e "  ${GREEN}${BOLD}Установка завершена успешно!${NC}"
echo ""

if [[ "$CONFIGURED" == "false" ]]; then
  echo -e "  ${YELLOW}⚠${NC}  Конфиг не заполнен — запустите настройку:"
  echo ""
  echo -e "      ${CYAN}${BOLD}fpuniversal setup${NC}"
  echo ""
else
  echo -e "  ${GREEN}✔${NC}  Бот работает в фоне"
  echo ""
  echo -e "      ${CYAN}fpuniversal log${NC}     ${GRAY}— посмотреть логи${NC}"
  echo -e "      ${CYAN}fpuniversal status${NC}  ${GRAY}— статус бота${NC}"
  echo ""
fi

echo -e "  ${GRAY}Все команды:${NC} fpuniversal"
echo -e "  ${GRAY}$(printf '═%.0s' {1..48})${NC}"
echo ""
