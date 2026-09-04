import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import test from "node:test";

const sourceUrl = (path) => new URL(`../${path}`, import.meta.url);

function readRequired(path) {
  const url = sourceUrl(path);
  assert.ok(existsSync(fileURLToPath(url)), `${path} precisa existir para cumprir o contrato do modo claro`);
  return readFileSync(url, "utf8");
}

function quotedUnionValues(source, typeName) {
  const declaration = source.match(new RegExp(`(?:export\\s+)?type\\s+${typeName}\\s*=\\s*([^;]+);`));
  assert.ok(declaration, `o tipo ${typeName} precisa declarar os temas permitidos`);
  return [...declaration[1].matchAll(/["']([^"']+)["']/g)].map((match) => match[1]);
}

function matchingBrace(source, openingIndex) {
  let depth = 0;
  let quote = "";

  for (let index = openingIndex; index < source.length; index += 1) {
    const character = source[index];
    if (quote) {
      if (character === "\\") index += 1;
      else if (character === quote) quote = "";
      continue;
    }
    if (character === '"' || character === "'") {
      quote = character;
      continue;
    }
    if (character === "{") depth += 1;
    if (character === "}") {
      depth -= 1;
      if (depth === 0) return index;
    }
  }

  throw new Error("folha de estilo do modo claro possui chaves não balanceadas");
}

function nextCssDelimiter(source, from) {
  let quote = "";
  let parentheses = 0;
  let brackets = 0;

  for (let index = from; index < source.length; index += 1) {
    const character = source[index];
    if (quote) {
      if (character === "\\") index += 1;
      else if (character === quote) quote = "";
      continue;
    }
    if (character === '"' || character === "'") {
      quote = character;
      continue;
    }
    if (character === "(") parentheses += 1;
    if (character === ")") parentheses -= 1;
    if (character === "[") brackets += 1;
    if (character === "]") brackets -= 1;
    if (parentheses === 0 && brackets === 0 && (character === "{" || character === ";")) {
      return { character, index };
    }
  }

  return null;
}

function cssRules(source) {
  const clean = source.replace(/\/\*[\s\S]*?\*\//g, "");
  const rules = [];

  function visit(fragment) {
    let cursor = 0;
    while (cursor < fragment.length) {
      while (/\s/.test(fragment[cursor] || "")) cursor += 1;
      if (cursor >= fragment.length) break;

      const delimiter = nextCssDelimiter(fragment, cursor);
      if (!delimiter) break;
      const header = fragment.slice(cursor, delimiter.index).trim();
      if (delimiter.character === ";") {
        cursor = delimiter.index + 1;
        continue;
      }

      const closingIndex = matchingBrace(fragment, delimiter.index);
      const body = fragment.slice(delimiter.index + 1, closingIndex);
      if (/^@(media|supports|container|layer|scope|starting-style)\b/i.test(header)) visit(body);
      else if (!header.startsWith("@")) rules.push({ body, header });
      cursor = closingIndex + 1;
    }
  }

  visit(clean);
  return rules;
}

function splitSelectorList(header) {
  const selectors = [];
  let start = 0;
  let quote = "";
  let parentheses = 0;
  let brackets = 0;

  for (let index = 0; index < header.length; index += 1) {
    const character = header[index];
    if (quote) {
      if (character === "\\") index += 1;
      else if (character === quote) quote = "";
      continue;
    }
    if (character === '"' || character === "'") {
      quote = character;
      continue;
    }
    if (character === "(") parentheses += 1;
    if (character === ")") parentheses -= 1;
    if (character === "[") brackets += 1;
    if (character === "]") brackets -= 1;
    if (character === "," && parentheses === 0 && brackets === 0) {
      selectors.push(header.slice(start, index).trim());
      start = index + 1;
    }
  }
  selectors.push(header.slice(start).trim());
  return selectors.filter(Boolean);
}

function pxMinimums(source) {
  const customProperties = new Map(
    [...source.matchAll(/--([\w-]+)\s*:\s*(\d+(?:\.\d+)?)px\b/g)]
      .map((match) => [match[1], Number(match[2])]),
  );
  const values = [];
  const minimum = /min-(?:height|block-size)\s*:\s*(\d+(?:\.\d+)?)px\b|min-(?:height|block-size)\s*:\s*var\(\s*--([\w-]+)\s*\)/g;
  for (const match of source.matchAll(minimum)) {
    if (match[1]) values.push(Number(match[1]));
    else if (customProperties.has(match[2])) values.push(customProperties.get(match[2]));
  }
  return values;
}

function relativeLuminance(hex) {
  const normalized = hex.replace("#", "");
  const channels = normalized.match(/.{2}/g).map((value) => Number.parseInt(value, 16) / 255);
  const linear = channels.map((value) => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4);
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
}

function contrastRatio(foreground, background) {
  const values = [relativeLuminance(foreground), relativeLuminance(background)].sort((a, b) => b - a);
  return (values[0] + 0.05) / (values[1] + 0.05);
}

test("o tema global é independente dos três modos de trabalho e começa no dark", () => {
  const theme = readRequired("src/lib/corviaTheme.tsx");
  const main = readRequired("src/main.tsx");

  assert.deepEqual(
    [...new Set(quotedUnionValues(theme, "CorviaTheme"))].sort(),
    ["dark", "light"],
    "CorviaTheme deve aceitar somente dark e light",
  );
  assert.doesNotMatch(theme, /\b(?:complete|essential|scientific)\b/, "aparência não pode reutilizar o estado dos modos de trabalho");

  const hasDarkDefault =
    /\bDEFAULT[_A-Z]*THEME\b[^=\n]*=\s*["']dark["']/i.test(theme)
    || /useState\s*<\s*CorviaTheme\s*>\s*\(\s*(?:\(\)\s*=>\s*)?["']dark["']\s*\)/.test(theme)
    || /(?:fallback|default|padr[aã]o)[\s\S]{0,160}\b(?:return\s+)?["']dark["']/i.test(theme)
    || /return\s+["']dark["']\s*;/.test(theme);
  assert.ok(hasDarkDefault, "o modo escuro tradicional precisa continuar sendo o padrão explícito");
  assert.doesNotMatch(theme, /\bDEFAULT[_A-Z]*THEME\b[^=\n]*=\s*["']light["']/i);
  assert.doesNotMatch(theme, /useState\s*<\s*CorviaTheme\s*>\s*\(\s*(?:\(\)\s*=>\s*)?["']light["']\s*\)/);

  const authOpen = main.indexOf("<AuthProvider>");
  const providerOpen = main.indexOf("<CorviaThemeProvider>");
  const app = main.indexOf("<App />", providerOpen);
  const providerClose = main.indexOf("</CorviaThemeProvider>", app);
  const authClose = main.indexOf("</AuthProvider>", providerClose);
  assert.ok(
    authOpen >= 0 && providerOpen > authOpen && app > providerOpen && providerClose > app && authClose > providerClose,
    "CorviaThemeProvider precisa envolver o App dentro do contexto autenticado global",
  );
});

test("a preferência persiste por usuário e é aplicada ao elemento html", () => {
  const theme = readRequired("src/lib/corviaTheme.tsx");

  assert.match(theme, /corvia:cardiology-spaces:theme(?::v\d+)?/);
  assert.match(theme, /\buseAuth\s*\(\s*\)/);
  assert.match(theme, /\busuario\??\.id\b|\buserId\b|\busuarioId\b/);
  assert.match(theme, /(?:window\.)?localStorage\.getItem\s*\(/);
  assert.match(theme, /(?:window\.)?localStorage\.setItem\s*\(/);

  const literalPerUserKey = /`[^`]*corvia:cardiology-spaces:theme(?::v\d+)?[^`]*\$\{[^}]+\}[^`]*`/.test(theme);
  const keyBuilder = /(?:function\s+\w*(?:theme|storage)\w*Key|const\s+\w*(?:theme|storage)\w*Key)\s*\([^)]*\b(?:userId|usuarioId|id)\b[^)]*\)[\s\S]{0,500}(?:corvia:cardiology-spaces:theme|\b(?:THEME|STORAGE)[_A-Z]*PREFIX\b)[\s\S]{0,240}\$\{[^}]*(?:userId|usuarioId|id)[^}]*\}/i.test(theme);
  assert.ok(literalPerUserKey || keyBuilder, "a chave de tema deve incluir o identificador do usuário, não ser global ao navegador");

  const documentRootBinding = theme.match(/(?:const|let)\s+(\w+)\s*=\s*document\.documentElement\b/);
  const rootExpression = documentRootBinding ? documentRootBinding[1] : "document\\.documentElement";
  const usesDataset = new RegExp(`${rootExpression}\\.dataset\\.corviaTheme\\s*=\\s*theme\\b`).test(theme);
  const usesAttribute = new RegExp(`${rootExpression}\\.setAttribute\\(\\s*["']data-corvia-theme["']\\s*,\\s*theme\\s*\\)`).test(theme);
  assert.ok(usesDataset || usesAttribute, "o tema precisa ser refletido como data-corvia-theme no html");
});

test("o seletor oferece exatamente dark e light como um grupo de rádio acessível", () => {
  const selector = readRequired("src/components/CorviaThemeSelector.tsx");
  const descriptorValues = [...selector.matchAll(/\b(?:theme|value|id)\s*:\s*["'](dark|light)["']/g)].map((match) => match[1]);
  const directValues = [...selector.matchAll(/\bsetTheme\s*\(\s*["'](dark|light)["']\s*\)/g)].map((match) => match[1]);
  const optionValues = descriptorValues.length ? descriptorValues : directValues;

  assert.equal(optionValues.length, 2, "o seletor deve declarar dois controles de aparência");
  assert.deepEqual([...new Set(optionValues)].sort(), ["dark", "light"]);
  assert.match(selector, /role=["']radiogroup["']/);
  assert.match(selector, /aria-(?:label|labelledby)=/);
  assert.match(selector, /role=["']radio["']/);
  assert.match(selector, /aria-checked=/);
  assert.match(selector, /type=["']button["']/);
  assert.match(selector, /Modo escuro/i);
  assert.match(selector, /Modo claro/i);
  assert.doesNotMatch(selector, /\b(?:complete|essential|scientific|autom[aá]tico|sistema)\b/i);

  const renderedRadioRoles = [...selector.matchAll(/role=["']radio["']/g)].length;
  assert.ok(
    renderedRadioRoles === 2 || (renderedRadioRoles === 1 && /\.map\s*\(/.test(selector)),
    "os dois temas precisam renderizar exatamente dois radio buttons",
  );
});

test("a aparência é escolhida no login e continua disponível na conta, sem virar modo de trabalho", () => {
  const home = readRequired("src/pages/CardiologySpacesHome.tsx");
  const frame = readRequired("src/components/CardiologySpacesAppFrame.tsx");
  const login = readRequired("src/pages/Entrar.tsx");

  const choiceStart = home.indexOf("if (!mode)");
  const choiceCards = home.indexOf('className="spaces-choice__cards"', choiceStart);
  assert.ok(choiceStart >= 0 && choiceCards > choiceStart, "a escolha de experiência precisa continuar após o login");
  assert.doesNotMatch(home.slice(choiceStart, choiceCards), /CorviaThemeSelector/, "o tema não deve competir com os três modos na tela seguinte");
  assert.match(login, /className="login-gateway__theme-choice"/);
  assert.deepEqual([...login.matchAll(/id: "(light|dark)"/g)].map((match) => match[1]), ["light", "dark"]);

  const workNavStart = home.indexOf('<nav aria-label="Modo de trabalho">');
  const workNavEnd = home.indexOf("</nav>", workNavStart);
  assert.ok(workNavStart >= 0 && workNavEnd > workNavStart, "a navegação dos modos precisa permanecer identificável");
  const workNav = home.slice(workNavStart, workNavEnd);
  assert.doesNotMatch(workNav, /CorviaThemeSelector|setTheme|toggleTheme/, "aparência não pode entrar na navegação dos modos");
  assert.deepEqual(
    [...workNav.matchAll(/chooseMode\(\s*["'](complete|essential|scientific)["']\s*\)/g)].map((match) => match[1]),
    ["complete", "essential", "scientific"],
    "a navegação deve continuar com exatamente os três modos aprovados",
  );

  const accountStart = frame.indexOf('className="cv-account-menu"');
  const accountEnd = frame.indexOf("</div>", accountStart);
  const accountSelector = frame.indexOf("<CorviaThemeSelector", accountStart);
  assert.ok(accountStart >= 0 && accountSelector > accountStart && accountSelector < accountEnd, "o menu da conta precisa expor o seletor de aparência");
});

test("o AppFrame troca os dois logos para o asset claro segundo o tema", () => {
  const frame = readRequired("src/components/CardiologySpacesAppFrame.tsx");

  assert.match(frame, /\buseCorviaTheme\s*\(\s*\)/);
  assert.match(frame, /["']\/corvia-logo-spaces\.svg["']/);
  assert.match(frame, /["']\/corvia-logo-spaces-dark\.svg["']/);
  assert.match(frame, /theme\s*===\s*["'](?:light|dark)["']/);

  const dynamicLogoSources = [...frame.matchAll(/<img\s+src=\{[^}]*logo[^}]*\}/gi)].length;
  assert.ok(dynamicLogoSources >= 2, "topbar e drawer devem consumir a mesma escolha dinâmica de logo");
});

test("os portais claros usam ambientes com luz natural sem alterar as cenas escuras", () => {
  const scene = readRequired("src/components/CardiologySpaceScene.tsx");
  const lightStyles = readRequired("src/styles/cardiology-spaces-light-mode.css");
  const spaces = ["consultorio", "hospital", "ensino", "pesquisa", "gestao"];

  assert.match(scene, /\buseCorviaTheme\s*\(\s*\)/);
  assert.match(scene, /theme\s*===\s*["']light["']\s*\?\s*LIGHT_SCENE_BY_SPACE\[space\]\s*:\s*SCENE_BY_SPACE\[space\]/,
    "a escolha da cena precisa depender apenas do tema atual");
  assert.match(scene, /data-scene-theme=\{theme\}/,
    "a cena renderizada precisa expor o tema para a validação visual");

  for (const space of spaces) {
    const darkAsset = `/spaces/corvia-room-${space}.jpg`;
    const lightAsset = `/spaces/corvia-room-${space}-light-640.webp`;
    const lightAssetBytes = readFileSync(sourceUrl(`public${lightAsset}`));
    assert.ok(scene.includes(darkAsset), `${space} precisa preservar a fotografia escura original`);
    assert.ok(scene.includes(lightAsset), `${space} precisa possuir uma variante de luz natural`);
    assert.ok(
      existsSync(fileURLToPath(sourceUrl(`public${lightAsset}`))),
      `o asset de luz natural de ${space} precisa existir em public/spaces`,
    );
    assert.equal(lightAssetBytes.toString("ascii", 0, 4), "RIFF", `${space} precisa usar WebP válido`);
    assert.ok(lightAssetBytes.byteLength <= 120_000, `${space} precisa manter o portal abaixo de 120 kB`);
  }

  assert.doesNotMatch(lightStyles, /\b(?:invert|hue-rotate)\s*\(/i,
    "o tema claro não pode produzir aparência de negativo fotográfico");
  assert.match(lightStyles, /\.spaces-door\s+\.spaces-door__scene\s*\{[^}]*filter:\s*none/s,
    "a luz natural deve vir do asset, não de um clareamento CSS global");
});

test("o GalaxyThemeToggle (vídeo em loop) fica abaixo da marca, nos dois temas e nas duas telas", () => {
  // Substitui o contrato anterior, escrito para a astrofotografia estática
  // (corvia-galaxy-cameo.webp) — fechamento do PR #811, 03/09/2026: o
  // asset antigo ficou deliberadamente obsoleto, a representação virou
  // vídeo em loop contínuo, mas o propósito do gate é o mesmo — proteger o
  // desenho aprovado (footprint, tema, decoratividade).
  const toggle = readRequired("src/components/GalaxyThemeToggle.tsx");
  const home = readRequired("src/pages/CardiologySpacesHome.tsx");
  const homeStyles = readRequired("src/styles/cardiology-spaces-home.css");
  const lightStyles = readRequired("src/styles/cardiology-spaces-light-mode.css");
  const video = "public/spaces/galaxy-loop-v2.mp4";
  const poster = "public/spaces/galaxy-loop-poster.webp";

  // 1-2: o componente existe e usa o vídeo aprovado.
  assert.ok(existsSync(fileURLToPath(sourceUrl(video))), "galaxy-loop-v2.mp4 precisa existir em public/spaces");
  assert.match(toggle, /src="\/spaces\/galaxy-loop-v2\.mp4"/,
    "o componente precisa apontar para o vídeo aprovado");

  // 3: atributos nativos obrigatórios do <video> — autoplay em mobile
  // depende da combinação exata autoPlay+muted+playsInline.
  for (const atributo of ["autoPlay", "muted", "loop", "playsInline"]) {
    assert.match(toggle, new RegExp(`\\b${atributo}\\b`), `<video> precisa do atributo ${atributo}`);
  }

  // 4-5: decorativo, nunca rouba o clique do botão pai; tema continua ligado.
  assert.match(toggle, /aria-hidden=\{?["']true["']\}?/, "o <video> precisa ser aria-hidden (decorativo)");
  assert.match(homeStyles, /\.galaxy-theme-toggle__video\s*\{[^}]*pointer-events:\s*none/s,
    "o vídeo não pode roubar o clique do <button> pai");
  assert.match(toggle, /useCorviaTheme\s*\(\s*\)/, "precisa reutilizar useCorviaTheme(), não um segundo mecanismo de tema");
  assert.match(toggle, /onClick=\{toggleTheme\}/, "o controle precisa alternar o tema");

  // 6: aria-label dinâmico, refletindo o tema OPOSTO ao atual.
  assert.match(toggle, /aria-label=\{`Ativar modo \$\{theme === "light" \? "escuro" : "claro"\}`\}/,
    "o controle precisa anunciar o tema que será ativado, não o atual");

  // 7: footprint aprovado preservado — mesmas dimensões/posição do cameo antigo.
  assert.match(
    homeStyles,
    /\.galaxy-theme-toggle\s*\{[^}]*left:\s*50%[^}]*width:\s*140px[^}]*height:\s*52px[^}]*transform:\s*translateX\(-50%\)/s,
    "a área de toque precisa manter o footprint aprovado (140×52, centralizada abaixo da marca)",
  );
  assert.match(
    homeStyles,
    /\.galaxy-theme-toggle__video\s*\{[^}]*width:\s*132px[^}]*height:\s*44px/s,
    "o chip visual precisa manter as dimensões aprovadas (132×44)",
  );
  // width/height/aspect-ratio fixos de antemão — sem isso, o <video> pode
  // causar layout shift ao carregar/começar a tocar.
  assert.match(homeStyles, /\.galaxy-theme-toggle__video\s*\{[^}]*aspect-ratio:\s*132\s*\/\s*44/s,
    "aspect-ratio fixo evita CLS quando o vídeo carrega");

  // 8-9: mix-blend-mode + fundo de acento — a calibração de cor aprovada.
  assert.match(homeStyles, /\.galaxy-theme-toggle__video\s*\{[^}]*mix-blend-mode:\s*screen/s,
    "precisa usar mix-blend-mode: screen para remover o fundo preto do vídeo");
  assert.match(homeStyles, /\.galaxy-theme-toggle__video\s*\{[^}]*background:\s*var\(--space-accent\)/s,
    "o fundo precisa ser a cor de acento do espaço, não transparente nem cinza");

  // 10: tratamento de intensidade/cromia (sóbrio, não a cor crua do vídeo).
  assert.match(homeStyles, /\.galaxy-theme-toggle__video\s*\{[^}]*filter:\s*brightness\([^)]+\)\s*saturate\([^)]+\)\s*contrast\([^)]+\)/s,
    "precisa calibrar brilho/saturação/contraste para o azul sóbrio aprovado");
  assert.match(homeStyles, /\.galaxy-theme-toggle__video\s*\{[^}]*opacity:\s*0\.\d+/s,
    "a intensidade deve ficar discretamente reduzida, não em opacidade total");

  // 11: nenhum uso visual do asset antigo resta em código-fonte.
  assert.doesNotMatch(`${home}\n${homeStyles}\n${lightStyles}`, /corvia-galaxy-cameo\.webp|spaces-theme-cameo/,
    "não pode restar referência ao cameo estático antigo");

  // 12: a página de decisão (Completo/Essencial/Ciência & Ensino) também tem o controle.
  assert.match(home, /<GalaxyThemeToggle\s+className="spaces-choice__theme-toggle"\s*\/>/,
    "a tela de escolha de experiência precisa ter o mesmo controle, abaixo do logo");
  assert.match(homeStyles, /\.spaces-choice__brand-cluster\s*\{[^}]*position:\s*relative/s,
    "o toggle da tela de escolha precisa ancorar só sob a marca, não sob o header inteiro");

  // 13: reduced-motion e poster de fallback protegidos.
  assert.match(toggle, /prefers-reduced-motion:\s*reduce/,
    "precisa respeitar prefers-reduced-motion (pausar o vídeo)");
  assert.match(toggle, /poster="\/spaces\/galaxy-loop-poster\.webp"/,
    "precisa ter poster estático de fallback, nunca área vazia nem o cameo antigo");
  assert.ok(existsSync(fileURLToPath(sourceUrl(poster))), "o poster precisa existir em public/spaces");

  // Layout não pode ter se movido: os mesmos marcos estruturais de antes
  // (faixa mobile reservada para a galáxia, nav abaixo dela) continuam.
  assert.match(homeStyles, /grid-template-rows:\s*60px\s+38px\s+48px/,
    "o mobile precisa manter a faixa reservada para a galáxia (layout não pode ter mudado)");
  assert.match(homeStyles, /\.spaces-home__topbar\s*>\s*nav\s*\{[^}]*grid-row:\s*3/s,
    "os três modos continuam abaixo da galáxia, sem sobreposição de alvos");
  assert.doesNotMatch(lightStyles, /\.spaces-workspace__greeting::(?:before|after)/,
    "o cabeçalho clínico central não deve receber a ilustração espacial");
  assert.match(lightStyles, /\.spaces-home\s*\{[\s\S]{0,420}radial-gradient\(ellipse 540px 330px at 0% 0%, rgba\(4, 43, 57, 0\.29\)/,
    "o destaque claro por trás do controle continua vindo do mesmo degradê azul-petróleo");
});

test("a paleta textual e os indicadores essenciais mantêm contraste WCAG no canvas claro", () => {
  const lightStyles = readRequired("src/styles/cardiology-spaces-light-mode.css");
  const textColors = ["#1b2440", "#4d5873", "#5e687f", "#626c82", "#4b4fc4", "#7957c8", "#c42068", "#0f727a", "#14764c"];
  const lightCanvases = ["#f7f3fa", "#eef2fa"];
  for (const color of textColors) {
    assert.ok(lightStyles.includes(color), `${color} precisa continuar declarado na paleta clara`);
    for (const canvas of lightCanvases) {
      assert.ok(contrastRatio(color, canvas) >= 4.5, `${color} precisa atingir 4,5:1 sobre o canvas ${canvas}`);
    }
  }

  assert.ok(lightStyles.includes("#eef2fa"), "o canvas lavanda precisa permanecer na paleta Aurora Lunar");
  for (const decorativeColor of ["#d12870", "#137a80", "#b78a52"]) {
    assert.ok(lightStyles.includes(decorativeColor), `${decorativeColor} precisa permanecer restrito a detalhes decorativos da Aurora Lunar`);
  }
  assert.ok(contrastRatio("#4b4fc4", "#ffffff") >= 3, "o anel de foco precisa atingir 3:1 sobre branco");
  for (const canvas of lightCanvases) {
    assert.ok(contrastRatio("#81899e", canvas) >= 3, `a borda dos radios precisa atingir 3:1 sobre ${canvas}`);
  }
  assert.ok(contrastRatio("#ffffff", "#b31f3a") >= 4.5, "ações de emergência precisam manter texto branco legível");
});

test("o modo claro usa figura clínica funcional por rota e preserva a cenografia escura", () => {
  const frame = readRequired("src/components/CardiologySpacesAppFrame.tsx");
  const figure = readRequired("src/components/ClinicalFunctionFigure.tsx");
  const figureStyles = readRequired("src/styles/cardiology-function-figure.css");
  const registry = readRequired("src/lib/clinicalRouteRegistry.ts");
  const routeGroups = [...new Set(quotedUnionValues(registry, "RouteGroup"))];

  assert.match(frame, /theme\s*===\s*["']light["'][\s\S]{0,500}<ClinicalFunctionFigure/,
    "o tema claro precisa renderizar a figura da função atual");
  assert.match(frame, /<ClinicalFunctionFigure[^>]+icon=\{route\.icon\}[^>]+group=\{route\.group\}[^>]+space=\{space\}/,
    "a figura precisa receber função, família e espaço da rota atual");
  assert.match(frame, /theme\s*===\s*["']dark["']\s*\?\s*\{\s*["']--cv-room["']:\s*`url\(\$\{spaceMeta\.roomImage\}\)`/,
    "o modo escuro precisa continuar carregando a fotografia original do ambiente");
  assert.match(frame, /cv-space-horizon__orb/,
    "o elemento cenográfico tradicional precisa permanecer no ramo escuro");

  assert.match(figure, /satisfies\s+Record<RouteGroup,\s*GroupFigureDefinition>/,
    "a cobertura das famílias funcionais precisa ser verificada pelo TypeScript");
  assert.ok(routeGroups.length >= 10, "o registro precisa expor as famílias funcionais esperadas");
  for (const group of routeGroups) {
    assert.match(figure, new RegExp(`\\b${group}\\s*:`), `a família ${group} precisa ter composição visual`);
  }
  assert.match(figure, /aria-hidden=["']true["']/);
  assert.match(figure, /focusable=["']false["']/);
  assert.doesNotMatch(`${figure}\n${figureStyles}`, /\burl\s*\(|telesc[oó]pio|montanha|planeta/i,
    "a figura funcional não pode depender de bitmap ou cenografia espacial literal");

  const unscopedFigureRules = cssRules(figureStyles)
    .flatMap(({ header }) => splitSelectorList(header))
    .filter((selector) => !/^html\[data-corvia-theme=(?:"light"|'light')\](?:$|[\s>+~.#:[*])/.test(selector));
  assert.deepEqual(unscopedFigureRules, [], `estilos da figura fora do tema claro: ${unscopedFigureRules.join(", ")}`);
});

test("a camada clara é a última folha, escopada no html e cobre todas as superfícies autenticadas", () => {
  const main = readRequired("src/main.tsx");
  const selectorStyles = readRequired("src/styles/corvia-theme-selector.css");
  const lightStyles = readRequired("src/styles/cardiology-spaces-light-mode.css");
  const imports = [...main.matchAll(/^\s*import\s+["']([^"']+\.css)["'];?/gm)].map((match) => match[1]);
  const selectorImport = imports.indexOf("./styles/corvia-theme-selector.css");
  const darkContrastImport = imports.indexOf("./styles/clinical-form-control-contrast.css");
  assert.ok(selectorImport >= 0 && selectorImport < darkContrastImport,
    "a geometria escura do seletor precisa existir antes do contrato final de contraste");
  assert.equal(imports.at(-1), "./styles/cardiology-spaces-light-mode.css", "a camada clara precisa ser o último CSS da cascata");

  assert.match(selectorStyles, /\.corvia-theme-selector__options\s*>\s*button/,
    "o seletor precisa manter geometria própria também no modo escuro padrão");
  assert.ok(pxMinimums(selectorStyles).some((value) => value >= 44),
    "as opções no modo escuro também precisam de alvo de toque de pelo menos 44px");

  const rules = cssRules(lightStyles);
  assert.ok(rules.length >= 8, "a camada clara precisa ser substancial, não apenas trocar uma cor de fundo");
  const unscoped = rules
    .flatMap(({ header }) => splitSelectorList(header))
    .filter((selector) => !/^html\[data-corvia-theme=(?:"light"|'light')\](?:$|[\s>+~.#:[*])/.test(selector));
  assert.deepEqual(unscoped, [], `seletores fora do tema claro: ${unscoped.join(", ")}`);

  for (const surface of [".spaces-choice", ".spaces-home", ".cv-app", ".clinical-os"]) {
    assert.ok(rules.some(({ header }) => header.includes(surface)), `${surface} precisa receber a paleta clara`);
  }
  assert.ok(rules.some(({ body }) => /\bcolor-scheme\s*:\s*light\b/.test(body)), "controles nativos precisam adotar color-scheme light");

  assert.match(
    lightStyles,
    /html\[data-corvia-theme="light"\]\s+#root\s+\.clinical-os\s+input:not\(\[type="checkbox"\]\):not\(\[type="radio"\]\)[^{]+\{[^}]*background-color:\s*#ffffff\s*!important/s,
    "o alias claro de alta especificidade precisa vencer os aliases escuros legados dos inputs",
  );
  assert.match(lightStyles, /\.clinical-os\s+\.cos-command-mini\s+button\s*\{[^}]*color:\s*#0f727a\s*!important/s,
    "o botão da busca legada precisa manter contraste no claro");
  assert.match(lightStyles, /\.cv-function-deck\s+\.cv-nav-link\[data-feature="exam-ai"\][^{]+\{[^}]*color:\s*#14764c/s,
    "o destaque Exame com IA precisa usar verde legível no claro");
  assert.match(lightStyles, /button\[role="radio"\]:focus-visible\s*\{[^}]*outline:\s*3px\s+solid\s+#4b4fc4/s,
    "o foco do seletor precisa alcançar contraste não textual de 3:1");

  const themeControlCss = rules
    .filter(({ header }) => /(?:theme|tema|appearance|aparencia)/i.test(header))
    .map(({ body, header }) => `${header}{${body}}`)
    .join("\n");
  assert.ok(themeControlCss, "a folha clara precisa estilizar o seletor de aparência");
  const dimensionTokens = [...lightStyles.matchAll(/--[\w-]+\s*:\s*\d+(?:\.\d+)?px\b/g)].map((match) => match[0]).join(";");
  assert.ok(pxMinimums(`${dimensionTokens};${themeControlCss}`).some((value) => value >= 44), "cada opção de tema precisa ter alvo de toque de pelo menos 44px");
});
