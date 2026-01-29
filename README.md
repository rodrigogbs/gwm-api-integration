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
- Usuário do app (e-mail)
- Senha do app (texto normal; a integração aplica MD5 como no Postman/original)
- Chassis/VIN (usado como deviceid no login, como no Postman)
- Senha de comandos do veículo (opcional)

## Debug
Se der `cannot_connect`, teste conectividade do host `br-app-gateway.gwmcloud.com` e veja Logs do HA.
