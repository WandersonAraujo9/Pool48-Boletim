# Boletim do Pool 48 — ANEC 73 (Streamlit)

App de consulta online do pool de qualidade ANEC 73, com login por senha
única (todos os clientes veem os mesmos dados) e área de administrador
para publicar o motor de cálculo atualizado todo mês.

## Rodar localmente

```bash
pip install -r requirements.txt
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edite .streamlit/secrets.toml com suas senhas
streamlit run app.py
```

## Publicar no Streamlit Community Cloud (gratuito)

1. Crie um repositório no GitHub e suba esta pasta inteira (o `.gitignore`
   já impede que suas senhas e o motor.xlsx subam junto).
2. Entre em https://share.streamlit.io, conecte sua conta GitHub e escolha
   o repositório, o branch e o arquivo `app.py`.
3. Antes de publicar (ou depois, em Settings > Secrets), cole o conteúdo
   do `secrets.toml.example` com suas senhas reais.
4. Publique. Vai gerar uma URL do tipo
   `https://SEU-APP.streamlit.app` — é esse link que você distribui para
   os 12 clientes do pool.

## Fluxo mensal

1. Atualize o `Motor_Controle_Qualidade_ANEC73_Pool.xlsx` (aba DADOS) e
   deixe recalcular.
2. Abra o app publicado, entre com a senha de administrador.
3. Na barra lateral, em "Área do administrador", envie o arquivo
   atualizado.
4. Pronto — todos os clientes que acessarem o link já veem os números
   novos, sem precisar reenviar nada para eles.

## Observação sobre persistência

O arquivo enviado fica salvo no disco do próprio app enquanto ele estiver
no ar. Se o Streamlit Community Cloud reiniciar o app por inatividade
prolongada, será preciso reenviar o motor.xlsx uma vez (mesma tela de
administrador). Para um uso mensal isso raramente é um problema, mas vale
saber.
