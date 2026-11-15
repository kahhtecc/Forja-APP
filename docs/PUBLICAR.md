# Publicar o Forja

Passo a passo para colocar o Forja na **Google Play** e no **iPhone** (de graça agora, e na App Store quando quiser).
A parte de código e segurança já está pronta (ver `SECURITY.md`). O que sobra são cadastros que só o dono da conta pode fazer.

**Dados que você vai precisar copiar e colar**

| Item | Valor |
|---|---|
| Nome do pacote / Bundle ID | `com.kaiquecupertino.forja` |
| Bundle ID da extensão (Atividade ao Vivo) | `com.kaiquecupertino.forja.widgets` |
| Política de privacidade | `https://kahhtecc.github.io/Forja-APP/privacidade.html` |
| Site | `https://kahhtecc.github.io/Forja-APP/` |
| SHA-256 da chave de assinatura | `35:99:90:E6:E5:A6:49:86:33:F7:43:EC:2E:5F:BB:73:75:2A:E5:BC:5B:1D:FC:47:F7:AE:28:70:D4:4E:19:41` |
| Textos da ficha, ícone, destaque e capturas | `docs/loja/` |
| Nível de API alvo (targetSdk) | 36 (Android 16), o mínimo exigido pela Play desde 31/08/2026 para apps novos e atualizações |

> Requisitos da Play Console conferidos em 15/11/2026 (ver "Fontes" no fim). As regras mudam: se algo no console estiver diferente, vale o que o console mostra.

---

## Parte 1 · Android na Google Play

### Passo 1: guardar a chave e ligar a assinatura automática (5 minutos, uma vez só)
A chave `forja-upload.jks` e a senha são a identidade do app. **Sem elas não dá para atualizar o app nunca mais.**
1. Guarde a pasta `chave/` (forja-upload.jks, senha.txt e forja-upload.jks.base64.txt) em dois lugares seguros: Google Drive pessoal e um pendrive. Não mande por WhatsApp nem e-mail.
2. No GitHub: repositório **teste-3** › **Settings** › **Secrets and variables** › **Actions** › **New repository secret**. Crie os quatro:

| Nome | Valor |
|---|---|
| `FORJA_KEYSTORE_BASE64` | todo o conteúdo de `forja-upload.jks.base64.txt` |
| `FORJA_KEYSTORE_SENHA` | a senha em `senha.txt` |
| `FORJA_CHAVE_SENHA` | a mesma senha |
| `FORJA_CHAVE_ALIAS` | `forja` |

Daí em diante, todo build sai assinado com a chave do Forja e vira a release `build-N` (APK + `Forja-N-play.aab`).
Sem os secrets, o CI gera só builds de teste (`teste-N`), que o app nunca oferece como atualização.

### Passo 2: conta de desenvolvedor (1 a 3 dias para aprovar)
1. Acesse **play.google.com/console** com a conta Google que vai ser a dona do app e pague a taxa única de **US$ 25**.
2. Tipo de conta: **Pessoal**.
3. Faça a **verificação de identidade**: nome completo, endereço, documento (RG ou CNH) e telefone. Espere o e-mail de aprovação. A taxa não é devolvida se o documento ou o cartão forem recusados, então use dados no seu nome.
4. Confirme o **e-mail de contato** e o **telefone** (o console manda códigos).
5. **Verificação do aparelho Android** (contas pessoais novas): instale o app **Google Play Console** num celular Android de verdade (Android 10 ou mais novo, sem root), entre com a mesma conta, escolha a conta de desenvolvedor e toque em **Verificar**. Leva menos de um minuto. Sem isso o app não pode ser disponibilizado na Play.
6. **Verificação de desenvolvedor Android** (proteção ativa no Brasil desde 30/09/2026): o Google diz que a Play registra sozinha a grande maioria dos apps. Mesmo assim, abra **Verificação de desenvolvedor Android** no Play Console e confira se o pacote `com.kaiquecupertino.forja` aparece registrado. Adicione também a SHA-256 acima, para o APK distribuído pelo GitHub (fora da Play o registro é manual).

### Passo 3: criar o app
1. **Todos os apps › Criar app**.
2. Nome: *Forja: treino sob medida* · Idioma padrão: Português (Brasil) · **App** · **Gratuito** · aceite as declarações › **Criar app**.
3. **Testar e lançar › Configuração › Integridade do app › Assinatura de apps pelo Google Play**: aceite. A `forja-upload.jks` vira a sua *chave de upload*. O Google guarda a chave final de assinatura.

### Passo 4: Conteúdo do app (menu **Política e programas › Conteúdo do app**)
Responda cada cartão assim:

| Cartão | Resposta |
|---|---|
| Política de privacidade | o link da tabela do topo |
| Acesso ao app | Todas as funcionalidades estão disponíveis sem acesso especial (sem login) |
| Anúncios | Não, o app não contém anúncios |
| ID de publicidade | Não, o app não usa o ID de publicidade |
| Classificação do conteúdo | e-mail de contato › categoria **Referência, notícias ou educação** (ou *Todos os outros tipos*) › responda **Não** a violência, sexo, linguagem, drogas, apostas, compras e interação entre usuários. Resultado esperado: **Livre** |
| Público-alvo | **18 anos ou mais** (pode marcar também 13 a 17). Não é direcionado a crianças |
| Apps de notícias / governo / financeiro / VPN | Não |
| **Apps de saúde** | recurso **Atividade e condicionamento físico** (grupo Saúde e fitness). Não é dispositivo médico. As justificativas do Health Connect ficam **dentro deste mesmo formulário** (ver abaixo) |
| **Segurança dos dados** | ver abaixo |
| **Serviço em primeiro plano** | ver abaixo |
| Recursos financeiros / Apps de vigilância | Não |

**Segurança dos dados** (a resposta mais importante):
1. *O app coleta ou compartilha algum dos tipos de dados exigidos?* **Não.**
   Motivo: "coletar" na Play significa enviar para fora do aparelho. O Forja guarda perfil, treinos e batimentos só no aparelho. O Health Connect e o Bluetooth também são lidos só no aparelho.
2. *Os dados são criptografados em trânsito?* **Sim** (só HTTPS, e só para baixar conteúdo público).
3. *Os usuários podem pedir a exclusão?* Sim: Perfil › Apagar todos os dados, ou desinstalando.

**Health Connect** (dentro do formulário **Apps de saúde**: depois de marcar o recurso, o console pede uma explicação para cada tipo de dado; o antigo formulário separado de pedido de acesso foi desativado). Se a lista de tipos de dados ainda não aparecer, envie antes o AAB para a faixa de teste fechado (Passo 6) e volte aqui:

| Permissão | Justificativa para colar |
|---|---|
| `WRITE_EXERCISE` | Grava no Health Connect cada treino concluído no Forja (tipo, horário, duração e calorias estimadas), para o usuário somar ao seu histórico de atividade. Só quando o usuário liga a opção em Perfil › Relógio e saúde. |
| `READ_HEART_RATE` | Lê a frequência cardíaca registrada pelo relógio do usuário durante o treino, para mostrar a FC média e máxima na tela de conclusão. Os dados ficam só no aparelho e não são enviados a servidores. |

A tela de justificativa do app abre pelo próprio Health Connect. Política: o mesmo link de privacidade.

**Serviço em primeiro plano (tipo Saúde):**
- Tipo: **Saúde** (`FOREGROUND_SERVICE_HEALTH`).
- Descrição: "Mostra o treino em andamento (exercício, série e cronômetro de descanso) na notificação e no relógio Wear OS, com botões para concluir série e pular descanso. Começa quando o usuário inicia um treino e termina quando ele encerra."
- Impacto se adiado: o cronômetro de descanso e os avisos no relógio parariam com a tela desligada.
- Vídeo: grave a tela do celular por uns 20 s (iniciar treino › bloquear a tela › ver a notificação) e envie como vídeo não listado do YouTube.

### Passo 5: ficha da loja (menu **Expandir o crescimento › Presença na loja › Versão principal da página**)
- Nome, descrição curta e descrição completa: copie de `docs/loja/ficha.md`.
- Ícone: `docs/loja/icone-512.png` · Recurso gráfico: `docs/loja/destaque-1024x500.png`.
- Capturas de tela: de 2 a 8 imagens. Use as 8 de `docs/loja/capturas/` (1080×2160). As capturas brutas da release (`01-boas-vindas.png`…) têm 1080×2400, mais compridas que a proporção máxima de 2:1 que a Play aceita, e por isso foram recortadas (sem a barra de status e a barra de gestos).
- Categoria: **Saúde e fitness** · E-mail de contato: o da conta.

### Passo 6: teste fechado obrigatório (14 dias)
Contas pessoais criadas depois de 13/11/2023 precisam de um teste fechado com **pelo menos 12 testadores inscritos por 14 dias seguidos** antes de liberar a produção (contas de organização não têm essa regra). A contagem vale no momento do pedido: se alguém sair do teste no meio, os 14 dias dele recomeçam. Por isso convide 15 ou mais.
1. **Testar e lançar › Teste › Teste fechado › Criar faixa**.
2. **Testadores**: crie uma lista com os e-mails (conta Google) de pelo menos 12 pessoas, ou use um Grupo do Google.
3. **Criar versão** › envie o `Forja-N-play.aab` (da release `build-N` mais recente ou o que recebeu assinado) › notas: "Primeira versão de teste" › **Revisar e lançar**.
4. Mande aos testadores o **link de participação** que aparece na faixa. Cada um abre o link, aceita e instala pela Play.
5. Peça para manterem o app instalado e abrirem de vez em quando por 14 dias.

### Passo 7: produção
1. Depois dos 14 dias: **Painel › Solicitar acesso à produção** e responda o questionário (como recrutou os testadores, o que eles acharam e o que você mudou). A resposta costuma sair em até 7 dias.
2. Com o acesso liberado: **Produção › Criar versão** › mesmo AAB (ou um mais novo) › **Países**: Brasil (ou todos) › **Revisar e lançar**.
3. A análise leva de algumas horas a 7 dias, ou mais em casos excepcionais; contas novas costumam cair na revisão mais demorada. Saindo na Play, o aviso do Play Protect some.

**Atualizações depois:** a cada push, o GitHub gera um novo `Forja-N-play.aab` (o número da versão sobe sozinho; a Play recusa um AAB com número repetido). Envie em **Produção › Criar versão**. Cada atualização precisa continuar mirando o nível de API exigido no ano. Animações e exercícios novos chegam sozinhos (atualização de conteúdo, sem código), o que a Play permite.

**Se o Play Protect bloquear o APK do GitHub antes de sair na Play:** peça revisão em support.google.com/googleplay/android-developer/contact/protectappeals.

---

## Parte 2 · iPhone

| Forma | Custo | Precisa de computador | Validade | Relógio (Atividade ao Vivo / Apple Watch) |
|---|---|---|---|---|
| **A. App da Tela de Início (PWA)** | grátis | não | permanente, atualiza sozinho | não |
| **B. IPA com Sideloadly** | grátis (Apple ID comum) | sim (Windows ou Mac) | reassinar a cada 7 dias | sim |
| **C. TestFlight e App Store** | US$ 99 por ano | não (o GitHub compila) | permanente | sim |

### A. App da Tela de Início (começa hoje, sem custo)
1. No iPhone, abra **https://kahhtecc.github.io/Forja-APP/** no **Safari**.
2. Toque em **Compartilhar** (quadrado com seta) › **Adicionar à Tela de Início** › **Adicionar**.

Fica com ícone próprio, abre em tela cheia, funciona offline e se atualiza sozinho. Passo a passo com imagens: https://kahhtecc.github.io/Forja-APP/instalar.html

### B. App nativo pelo Sideloadly (grátis, renovar a cada 7 dias)
1. Baixe o `Forja-ios-N.ipa` mais recente em **Releases** no GitHub (ou use o que recebeu).
2. No computador, instale o **iTunes** (no Windows, a versão do site da Apple, não a da Microsoft Store) e o **Sideloadly** (sideloadly.io).
3. Conecte o iPhone pelo cabo e toque em **Confiar** no iPhone.
4. Abra o Sideloadly, arraste o IPA, digite seu Apple ID e clique em **Start**. Se preferir, use um Apple ID secundário: a senha vai só para a Apple.
5. No iPhone:
   - **Ajustes › Privacidade e Segurança › Modo de Desenvolvedor** › ativar (reinicia o aparelho);
   - **Ajustes › Geral › VPN e Gerenciamento de Dispositivo** › seu Apple ID › **Confiar**.
6. A cada 7 dias, abra o Sideloadly com o iPhone conectado e clique em Start de novo (ou ative *Auto refresh*). Os dados do app continuam.

> A Atividade ao Vivo (tela bloqueada, Dynamic Island e Smart Stack do Apple Watch) funciona por aqui. Se a assinatura gratuita recusar a capacidade de Saúde, desmarque-a nas opções avançadas do Sideloadly. O app abre normal, só a integração com o Saúde fica desligada, e a cinta Bluetooth continua funcionando.

### C. TestFlight e App Store (US$ 99/ano)
**C1. Conta Apple Developer**
1. Em **developer.apple.com/programs/enroll**, inscreva-se como **Pessoa física** com seu Apple ID (precisa da autenticação de dois fatores) e pague US$ 99. A aprovação leva até 48 h.
2. Anote o **Team ID** em developer.apple.com › Account › Membership details.

**C2. Identificadores**
Em developer.apple.com › **Certificates, Identifiers & Profiles › Identifiers › +** › App IDs:
1. `com.kaiquecupertino.forja`: marque **HealthKit**.
2. `com.kaiquecupertino.forja.widgets`: sem capacidades extras.

**C3. App no App Store Connect**
1. **appstoreconnect.apple.com › Apps › + › Novo app** › iOS › Nome *Forja: treino sob medida* › Português (Brasil) › Bundle ID `com.kaiquecupertino.forja` › SKU `forja`.
2. **Users and Access › Integrations › App Store Connect API › Team Keys › +** › nome "GitHub" › acesso **Admin**, necessário para o GitHub criar os certificados sozinho › baixe o arquivo `.p8` (ele só baixa uma vez) e anote o **Key ID** e o **Issuer ID**.

**C4. Ligar o envio automático no GitHub** (Settings › Secrets and variables › Actions):

| Secret | Valor |
|---|---|
| `ASC_KEY_ID` | Key ID |
| `ASC_ISSUER_ID` | Issuer ID |
| `ASC_KEY_P8` | todo o texto do arquivo `.p8` |
| `APPLE_TEAM_ID` | Team ID |

No próximo push em `ios/` (ou em **Actions › iOS › Run workflow**), o GitHub compila, assina e envia o build para o **TestFlight**. Em uns 15 minutos ele aparece em App Store Connect › TestFlight.

**C5. TestFlight**
- **Testes internos**: adicione até 100 pessoas da sua equipe, sem revisão.
- **Testes externos**: crie um grupo, adicione até 10.000 e-mails ou um link público e envie para a revisão beta (1 dia em média).
- Os testadores instalam pelo app **TestFlight**. Cada build vale 90 dias.

**C6. Enviar para a App Store**
Em **App Store Connect › Forja › Distribuição**, preencha:

| Campo | Resposta |
|---|---|
| Capturas | iPhone 6,9" (1320×2868) ou 6,5" (1242×2688): use as capturas do simulador da release `ios-N` |
| Textos | `docs/loja/ficha.md` (subtítulo até 30 caracteres: "Treino sob medida") |
| Palavras-chave | treino,academia,musculação,corrida,mobilidade,alongamento,hiit,bike,luta |
| URL de suporte | o Site · **URL da política de privacidade:** o link da tabela do topo |
| Categoria | **Saúde e fitness** (secundária: Esportes) |
| Classificação etária | responda **Nenhum** em tudo (resultado 4+). Se a revisão pedir, marque "Informações médicas/tratamento: Infrequente" (12+) |
| **Privacidade do app** | **Dados não coletados** (nada sai do aparelho; o `PrivacyInfo.xcprivacy` já declara isso) |
| Criptografia | já respondido no app (`ITSAppUsesNonExemptEncryption = NO`) |
| Build | escolha o que veio do TestFlight |
| Notas para a revisão | "Sem login. O HealthKit grava os treinos concluídos e lê a frequência cardíaca para mostrar FC média e máxima; tudo fica no aparelho. A Atividade ao Vivo mostra o treino em andamento. Para testar: responda o questionário, toque em Começar treino e conclua uma série." |

Clique em **Adicionar para revisão › Enviar**. A revisão leva de 1 a 3 dias. Depois de aprovado, você escolhe quando lançar.

**O que a Apple costuma conferir (já atendido):** o app diz onde usa o Saúde (Perfil › Relógio e saúde), tem política de privacidade, não manda dados de saúde para servidores, e o conteúdo baixado fica fora do backup do iCloud.

### D. Lojas alternativas (Brasil, iOS 26.5+)
Também exigem a conta Apple Developer (US$ 99) e a **notarização** da Apple. Com o item C pronto, o mesmo build pode ir para uma loja alternativa: siga as instruções da loja escolhida.

---

## Antes de cada publicação (checklist rápido)
- [ ] Workflows *Android APK* e *iOS* verdes no GitHub Actions, sem `CRASH` / `FALHA` no `resultado.txt`.
- [ ] Release Android chamada `build-N`, não `teste-N` (sinal de que os secrets da chave estão configurados).
- [ ] Notas da versão escritas em "Novidades desta versão".
- [ ] Política de privacidade atualizada se o app passou a usar algo novo.

## Fontes (conferidas em 15/11/2026)
- Taxa, identidade e verificação do aparelho: Ajuda do Play Console (support.google.com/googleplay/android-developer, artigos 6112435, 10841920 e 14316361).
- Teste fechado com 12 testadores por 14 dias: Ajuda do Play Console, artigo 14151465.
- Nível de API alvo: developer.android.com/google/play/requirements/target-sdk.
- Assinatura de apps pelo Google Play e chave de upload: developer.android.com/studio/publish/app-signing.
- Health Connect no formulário Apps de saúde: developer.android.com/health-and-fitness/guides/health-connect/publish/declare-access.
- Serviço em primeiro plano (declaração e vídeo): Ajuda do Play Console, artigo 13392821.
- Verificação de desenvolvedor Android: developer.android.com/developer-verification.
