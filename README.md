# Haval / GWM Vehicle (HTTP-only) – Home Assistant

Integração **nativa** (sem MQTT) para consultar status e enviar comandos remotos para veículos GWM/Haval via API do app.

> **Aviso**: integração não-oficial. A API pode mudar sem aviso.

## Instalação via HACS (Custom repository)
1. HACS → *Integrations* → ⋮ → *Custom repositories*
2. Cole a URL do seu repositório
3. Category: **Integration**
4. Instale e reinicie o Home Assistant

## Configuração
Configurações → Dispositivos e serviços → **Adicionar integração** → `Haval / GWM Vehicle`

Você informará:
- **Usuário** do app (e-mail)
- **Senha** do app (texto normal; a integração aplica MD5 como no projeto original)
- **Senha de comandos do veículo** (opcional; se vazia, comandos ficam indisponíveis)

## Entidades
- Sensores (bateria/autonomia/odômetro/estado bruto)
- Device tracker (se latitude/longitude estiverem presentes no status)
- Controle de ar-condicionado (se a senha de comandos for configurada)

## Debug
Se der `auth failed`, veja **Configurações → Sistema → Logs** e procure por `custom_components.haval`.

