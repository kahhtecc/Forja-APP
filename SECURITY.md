# Segurança do Forja

## Como reportar uma falha
Abra uma issue em https://github.com/kaiqueguimacuper-bit/teste-3/issues com o título "Segurança" (sem detalhes que permitam explorar a falha) e combinamos um canal privado. Resposta em até 7 dias.

## O que o app faz para proteger quem usa
| Área | Android | iPhone | Web |
|---|---|---|---|
| Dados pessoais e de saúde | só no aparelho (armazenamento privado do app); fora do backup na nuvem | só no aparelho (área privada do app, protegida pela criptografia do iOS) | só no navegador (localStorage) |
| Rede | só HTTPS, sem CAs instaladas pelo usuário (`network_security_config`) | só HTTPS (App Transport Security padrão, sem exceções) | Content-Security-Policy restrita |
| Conteúdo atualizado sem reinstalar | manifesto por HTTPS + hash de cada arquivo; caminhos validados (sem `../`), só json/mp4/webp/png/jpg, limite de tamanho | igual ao Android; conteúdo baixado fora do backup do iCloud | — |
| Atualização do APK (fora da Play) | só links do próprio repositório; o Android exige a mesma chave de assinatura para atualizar | — | — |
| Links externos | só `https://` | só `https://` | `rel="noopener"` |
| Player de vídeo | WebView sem acesso a arquivos; links abrem no navegador; ID do vídeo validado | WKWebView sem cookies persistentes; links abrem no Safari; ID validado | — |
| Componentes expostos | só a tela principal e as telas de permissão de saúde; modo demo só pelo adb (permissão DUMP); PendingIntents imutáveis | intents da Atividade ao Vivo só concluem série / pulam descanso | — |
| Permissões | todas opcionais além de internet e notificações; Bluetooth sem localização (`neverForLocation`) | Saúde e Bluetooth só quando o usuário liga | nenhuma |
| Rastreamento e anúncios | nenhum | nenhum (`PrivacyInfo.xcprivacy`) | nenhum |
| Código | R8 (minify) no release | build Release | — |

## Chaves
A chave de assinatura (`forja-upload.jks`), a senha e as chaves da App Store Connect ficam só nos *secrets* do GitHub e com o dono do projeto. O `.gitignore` bloqueia esses arquivos.
