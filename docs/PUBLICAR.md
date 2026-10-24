# Publicar o Forja

Este guia junta o que falta para o app passar na verificação do Google e ser instalado no iPhone.
A parte de código já está pronta: o que sobra são cadastros que só o dono da conta pode fazer.

---

## 1. Android: verificação do Google

### O que mudou em 2026
- **Verificação de desenvolvedor (Brasil, desde 30/09/2026).** Em aparelhos Android certificados, os apps precisam estar registrados por um desenvolvedor com identidade verificada. O registro liga o **nome do pacote** à **impressão digital SHA-256 da chave de assinatura**. Vale para a Google Play e para lojas parceiras; a Google diz que vai estender para o mundo todo em 2027. Apps não registrados ainda podem ser instalados por adb ou pelo fluxo avançado, com aviso.
- **API 36.** Desde 31/08/2026, app novo na Play precisa mirar o Android 16 (API 36).

### O que já está feito no projeto
| Exigência | Situação |
|---|---|
| Mira API 36 (Android 16) | `compileSdk`/`targetSdk` 36 |
| Nome de pacote próprio e permanente | `com.kaiquecupertino.forja` (Android e iOS) |
| Chave de assinatura própria (não a de depuração) | gerada: `forja-upload.jks` (entregue à parte) |
| Pacote para a Play (AAB) | `Forja-N-play.aab` em cada release |
| Sem atualização de APK por fora da Play | o build da Play (`-Pplay`) não mostra o aviso de APK novo; só o conteúdo (exercícios e animações, sem código) é atualizado |
| Política de privacidade pública | `https://kaiqueguimacuper-bit.github.io/teste-3/privacidade.html` (também dentro do app, em Perfil) |
| Permissões mínimas | internet, notificações, iniciar com o aparelho (lembretes), vibração; opcionais: Bluetooth (cinta cardíaca, sem localização), serviço em primeiro plano de saúde (treino ao vivo no relógio) e Health Connect (gravar treino, ler FC) |
| Sem anúncios, rastreamento ou coleta de dados | tudo fica no aparelho |

**Impressão digital da chave (SHA-256):**
```
35:99:90:E6:E5:A6:49:86:33:F7:43:EC:2E:5F:BB:73:75:2A:E5:BC:5B:1D:FC:47:F7:AE:28:70:D4:4E:19:41
```

### Passo 1: guardar a chave e ligar a assinatura automática (5 minutos)
A chave `forja-upload.jks` e a senha são a identidade do app. **Guarde uma cópia em lugar seguro** (Google Drive pessoal, pendrive). Sem elas não dá para publicar atualizações do APK direto.

No GitHub: repositório › **Settings › Secrets and variables › Actions › New repository secret**. Crie quatro secrets:

| Nome | Valor |
|---|---|
| `FORJA_KEYSTORE_BASE64` | todo o conteúdo do arquivo `forja-upload.jks.base64.txt` |
| `FORJA_KEYSTORE_SENHA` | a senha em `senha.txt` |
| `FORJA_CHAVE_SENHA` | a mesma senha |
| `FORJA_CHAVE_ALIAS` | `forja` |

A partir daí, todo build sai assinado com a chave do Forja (o aviso "assinado com a chave de depuração" some do log).

> O APK assinado com a chave nova não atualiza um Forja instalado antes (chave e nome de pacote mudaram). Desinstale o antigo uma vez.

### Passo 2: conta de desenvolvedor e verificação de identidade
1. Crie a conta em **play.google.com/console** (taxa única de US$ 25). Conta **pessoal** serve.
2. Faça a verificação de identidade que o console pedir: nome legal, endereço, documento e telefone.
3. Em **Verificação de desenvolvedor Android** (no Play Console ou no Android Developer Console), registre o pacote `com.kaiquecupertino.forja` com a SHA-256 acima. Para apps publicados pela Play, o console faz esse registro com a chave de assinatura da Play automaticamente. Registre também a chave acima para o APK distribuído pelo GitHub.

### Passo 3: criar o app na Play
1. **Criar app** › nome *Forja: treino sob medida* › idioma Português (Brasil) › App › Gratuito.
2. **Assinatura de apps pelo Google Play:** aceite. O `forja-upload.jks` vira a chave de upload.
3. **Teste fechado obrigatório (contas pessoais novas):** pelo menos **12 testadores** com o app instalado por **14 dias seguidos**, antes de pedir acesso à produção. Crie a faixa *Teste fechado*, envie o `Forja-N-play.aab` e convide os testadores por e-mail ou Grupo do Google.
4. Depois dos 14 dias: **Produção › Solicitar acesso** e responda o questionário sobre o teste.

### Passo 4: formulários do console (respostas prontas)
**Política do app**
- *Política de privacidade:* `https://kaiqueguimacuper-bit.github.io/teste-3/privacidade.html`
- *Anúncios:* não contém anúncios.
- *Acesso ao app:* todas as funções disponíveis sem login.
- *Público-alvo:* 18+ (ou 13+). Não é direcionado a crianças.
- *Apps de saúde (declaração):* categoria **Fitness e exercícios físicos**. Não é dispositivo médico. Usa Health Connect só com o usuário ligando a opção: grava sessões de exercício e lê frequência cardíaca, tudo no aparelho, sem enviar a servidores.
- *Health Connect (formulário de permissões):* `WRITE_EXERCISE` para gravar o treino concluído; `READ_HEART_RATE` para mostrar FC média e máxima do treino. Link da política acima.
- *Serviço em primeiro plano (tipo health):* mostra o treino em andamento na notificação e no relógio Wear OS, com botões de concluir série e pular descanso; começa quando o usuário inicia um treino e para ao encerrar.
- *Segurança dos dados:* **não coleta nem compartilha dados**. Os dados digitados (idade, peso, limitações) ficam só no aparelho e não são transmitidos. Criptografia em trânsito: sim (HTTPS). Exclusão: o usuário apaga dentro do app (Perfil › Apagar todos os dados) ou desinstalando.
- *Classificação de conteúdo (IARC):* categoria "Referência, notícias ou educação" ou "Utilitário"; responda "não" a violência, sexo, drogas, apostas, interação entre usuários e compras. Resultado esperado: Livre.
- *Notícias / governo / financeiro / VPN:* não se aplica.

**Ficha da loja:** textos em `docs/loja/ficha.md`; ícone 512×512, gráfico de destaque 1024×500 e capturas em `docs/loja/`.

### Se o Play Protect avisar na instalação do APK
- Com o app publicado na Play (ou registrado na verificação de desenvolvedor), o aviso de "app desconhecido" não aparece mais.
- Antes disso, se o Play Protect bloquear por engano, o dono da conta pode pedir uma revisão em **support.google.com/googleplay/android-developer/contact/protectappeals**.

---

## 2. iPhone: formas de instalar

| Forma | Custo | Precisa de computador | Validade |
|---|---|---|---|
| **App da Tela de Início (PWA)** | grátis | não | permanente, atualiza sozinho |
| **IPA com Sideloadly ou AltStore** | grátis (Apple ID comum) | sim (Windows ou Mac) | reassinar a cada 7 dias (automático com o app do computador) |
| **TestFlight / App Store** | US$ 99 por ano (Apple Developer Program) | não | permanente |
| Lojas alternativas no Brasil (iOS 26.5+) | conta de desenvolvedor + notarização da Apple | não | permanente |

### 2.1 App da Tela de Início (recomendado para começar)
Página com o passo a passo: **https://kaiqueguimacuper-bit.github.io/teste-3/instalar.html**
1. Abra **https://kaiqueguimacuper-bit.github.io/teste-3/** no Safari.
2. Toque em **Compartilhar › Adicionar à Tela de Início**.

Ganha ícone próprio, abre em tela cheia, funciona offline depois da primeira abertura e se atualiza sozinho.

> O site é publicado pelo workflow *Site* (Settings › Pages › Source: **GitHub Actions**). O GitHub Pages grátis exige repositório **público**.

### 2.2 IPA (app nativo SwiftUI)
1. Baixe o `Forja-ios-N.ipa` mais recente em **Releases** (ou nos artefatos do workflow *iOS*).
2. Instale o **Sideloadly** (sideloadly.io) no computador e conecte o iPhone pelo cabo.
3. Arraste o IPA, digite seu Apple ID e clique em **Start**.
4. No iPhone: **Ajustes › Geral › VPN e Gerenciamento de Dispositivo** › confiar no seu Apple ID; e **Ajustes › Privacidade e Segurança › Modo de Desenvolvedor** › ativar (reinicia o aparelho).

### 2.3 TestFlight e App Store (quando quiser publicar de verdade)
1. Assine o Apple Developer Program (US$ 99/ano).
2. No App Store Connect, crie o app com o bundle ID `com.kaiquecupertino.forja`.
3. Crie uma chave de API (**Users and Access › Integrations › App Store Connect API**, papel *App Manager*) e adicione ao GitHub os secrets:
   `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_KEY_P8` (conteúdo do arquivo .p8) e `APPLE_TEAM_ID`.
4. O workflow *iOS* passa a assinar e enviar cada build para o **TestFlight** sozinho. De lá, até 10.000 testadores instalam pelo app TestFlight, e você envia para revisão da App Store quando quiser.
