#!/usr/bin/env bash
# Instala o APK no emulador, abre cada tela em modo demo, tira capturas e testa interações reais.
set -u
PKG=com.forja.app
mkdir -p shots
R=shots/resultado.txt
: > "$R"
adb wait-for-device
until [ "$(adb shell getprop sys.boot_completed | tr -d '\r')" = "1" ]; do sleep 2; done
sleep 25   # deixa o launcher terminar de carregar (evita o aviso "Pixel Launcher isn't responding")
adb shell settings put global window_animation_scale 0
adb shell settings put global hide_error_dialogs 1 || true
adb shell am broadcast -a android.intent.action.CLOSE_SYSTEM_DIALOGS > /dev/null 2>&1 || true
adb install -r app/build/outputs/apk/release/app-release.apk >> "$R" 2>&1 || echo "FALHA instalar" >> "$R"
adb logcat -c

dump() { adb shell uiautomator dump /sdcard/ui.xml 2>&1 | grep -qi error && echo "FALHA uiautomator dump" >> "$R"; adb shell cat /sdcard/ui.xml | tr '>' '\n'; }
fecharAvisos() { # fecha diálogos de "não está respondendo" do sistema tocando em "Wait"
  local x; x=$(dump | grep -E "text=\"(Wait|Aguardar)\"" | head -1 | sed -E 's/.*bounds="\[([0-9]+),([0-9]+)\]\[([0-9]+),([0-9]+)\]".*/\1 \2 \3 \4/' | awk '{print int(($1+$3)/2), int(($2+$4)/2)}')
  if [ -n "$x" ]; then adb shell input tap $x; sleep 1; echo "aviso do sistema fechado" >> "$R"; fi
}
shot() { fecharAvisos; adb exec-out screencap -p > "shots/$1.png"; }
vivo() { adb shell pidof $PKG > /dev/null; }
abrir() { # $1 nome  $2 tela  $3 demo(true/false)
  adb shell am start -S -W -n $PKG/.MainActivity --ez demo "${3:-true}" --es screen "$2" > /dev/null 2>&1
  sleep "${4:-4}"
  if vivo; then shot "$1"; echo "OK $1" >> "$R"; else echo "CRASH $1" >> "$R"; fi
}
centro() { # content-desc ou texto (regex) -> "x y"
  dump | grep -E "(content-desc|text)=\"$1" | head -1 | sed -E 's/.*bounds="\[([0-9]+),([0-9]+)\]\[([0-9]+),([0-9]+)\]".*/\1 \2 \3 \4/' | awk '{print int(($1+$3)/2), int(($2+$4)/2)}'
}
tocar() { local c; fecharAvisos; c=$(centro "$1"); if [ -n "$c" ]; then adb shell input tap $c; sleep "${2:-1.5}"; echo "toque '$1' em $c" >> "$R"; else echo "FALHA não achei '$1'" >> "$R"; fi; }

# 1) primeira abertura (sem dados): boas-vindas e questionário
adb shell pm clear $PKG > /dev/null
abrir 01-boas-vindas home false 5
tocar "Montar minha rotina"; shot 02-pergunta-nome
tocar "Pular"; shot 03-pergunta-modalidade
tocar "Corrida" 2; shot 04-pergunta-objetivo
tocar "Saúde e vida ativa" 2; shot 05-pergunta-experiencia
tocar "Estou começando" 2; shot 06-pergunta-dias
vivo || echo "CRASH questionario" >> "$R"

# 2) telas em modo demo
abrir 10-hoje home
adb shell input swipe 540 1800 540 700 400; sleep 1; shot 11-hoje-rolado
abrir 12-plano plano
abrir 13-mobilidade mobilidade
abrir 14-exercicios exercicios
abrir 15-progresso progresso
adb shell input swipe 540 1800 540 600 400; sleep 1; shot 16-progresso-rolado
abrir 17-perfil perfil
abrir 18-sessao sessao
abrir 19-exercicio exercicio:agachamento-barra
abrir 20-rotina rotina:pre-corrida
abrir 21-fontes fontes
abrir 22-video video:agachamento-livre 8

# 3) treino ao vivo: concluir série, ver descanso, pular
abrir 30-treino player
# passa pelo aquecimento cronometrado até a primeira série com repetições
for _ in 1 2 3 4 5 6 7 8; do
  [ -n "$(centro "Concluir série")" ] && break
  [ -n "$(centro "Pular descanso")" ] && { adb shell input tap $(centro "Pular descanso"); sleep 1.5; continue; }
  c=$(centro "Concluir agora"); [ -n "$c" ] && adb shell input tap $c; sleep 1.5
done
tocar "Concluir série" 2; shot 31-descanso
tocar "Pular descanso" 2; shot 32-treino-serie2
tocar "Sair do treino" 1.5; shot 33-sair
vivo || echo "CRASH treino" >> "$R"

# 4) rotina de mobilidade por tempo (cronômetro)
abrir 40-rotina-ao-vivo treinorotina:pre-corrida
tocar "Iniciar" 3; shot 41-cronometro
vivo || echo "CRASH cronometro" >> "$R"

adb logcat -d | grep -E "AndroidRuntime|FATAL|com.forja" | tail -200 > shots/logcat.txt
echo "fim" >> "$R"
