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

function declarationValue(rule, property) {
  assert.ok(rule, `regra ausente para ${property}`);
  const escaped = property.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const value = rule.body.match(new RegExp(`(?:^|;)\\s*${escaped}\\s*:\\s*([^;!]+)`))?.[1]?.trim();
  assert.ok(value, `${property} precisa ser explícito no par de contraste`);
  return value;
}

test("monitor científico mantém texto, estado e controles contrastantes apenas no tema escuro", () => {
  const rules = cssRules(readRequired("src/styles/corvia-atelier.css"))
    .filter(({ header }) => header.includes(".scientific-intelligence-monitor"));
  assert.ok(rules.length >= 8);
  for (const { header } of rules) assert.match(header, /^html\[data-corvia-design="atelier"\]\[data-corvia-theme="dark"\]/);
  const find = suffix => rules.find(({ header }) => header.endsWith(suffix));
  const panel = declarationValue(find(".scientific-intelligence-monitor"), "background");
  const button = find(".scientific-intelligence-monitor button");
  for (const rule of [find(":is(h3, h4, strong, dd)"), find(":is(dt, small, p:not(.scientific-intelligence-monitor__health))"),
    find(".scientific-intelligence-monitor a"), find(".scientific-intelligence-monitor__health.is-active"),
    find(".scientific-intelligence-monitor__health:is(.is-degraded, .is-inactive)")]) {
    assert.ok(contrastRatio(declarationValue(rule, "color"), panel) >= 4.5, rule.header);
  }
  const control = declarationValue(button, "background");
  assert.ok(contrastRatio(declarationValue(button, "color"), control) >= 4.5);
  assert.ok(contrastRatio(declarationValue(button, "border-color"), control) >= 3);
  assert.ok(contrastRatio(declarationValue(find(":is(a, button):focus-visible"), "outline-color"), panel) >= 3);
});

test("favoritos e decisões editoriais escuros resolvem aliases locais e preservam os pares de leitura", () => {
  const rules = cssRules(readRequired("src/styles/corvia-atelier-content.css"))
    .filter(({ header }) => /\.favorites-page|\.admin-clinical-changes/.test(header));
  assert.ok(rules.length >= 10);
  for (const { header } of rules) assert.match(header, /^html\[data-corvia-design="atelier"\]\[data-corvia-theme="dark"\]/);
  const tokens = rules.find(({ header }) => header.endsWith(":is(.favorites-page, .admin-clinical-changes)"));
  const resolved = (value, depth = 0) => {
    assert.ok(depth < 5, "aliases de cor não podem ser cíclicos");
    const variable = value.match(/^var\((--[\w-]+)\)$/)?.[1];
    return variable ? resolved(declarationValue(tokens, variable), depth + 1) : value;
  };
  const color = (rule, property) => resolved(declarationValue(rule, property));
  const panel = color(tokens, "background");
  for (const token of ["--texto", "--texto-secundario", "--cv-text", "--cv-text-2", "--atelier-teal"]) {
    assert.ok(contrastRatio(color(tokens, token), panel) >= 4.5, token);
  }
  const find = fragment => rules.find(({ header }) => header.includes(fragment));
  for (const rule of [find(":is(h1, h2, h3, h4, legend, label)"), find(".favorites-page .eyebrow"),
    find(".favorites-page a:not(.botao)"), find(":is(p, small):not([role=")]) {
    assert.ok(contrastRatio(color(rule, "color"), panel) >= 4.5, rule.header);
  }
  const control = rules.find(({ header }) => header.endsWith(":is(button, a.botao):not(:disabled)"));
  const controlBackground = color(control, "background");
  assert.ok(contrastRatio(color(control, "color"), controlBackground) >= 4.5);
  assert.ok(contrastRatio(color(control, "border-color"), controlBackground) >= 3);
  const hover = find(":is(button, a.botao):not(:disabled):hover");
  assert.ok(contrastRatio(color(control, "color"), color(hover, "background")) >= 4.5);
  assert.ok(contrastRatio(color(control, "border-color"), color(hover, "background")) >= 3);
  const placeholder = find("::placeholder");
  assert.equal(declarationValue(placeholder, "opacity"), "1");
  assert.ok(contrastRatio(color(placeholder, "color"), controlBackground) >= 4.5);
  assert.equal(color(placeholder, "-webkit-text-fill-color"), color(placeholder, "color"));
  const action = find(".admin-clinical-changes .botao:not");
  assert.ok(contrastRatio(color(action, "color"), color(action, "background")) >= 4.5);
  assert.ok(contrastRatio(declarationValue(find(":focus-visible"), "outline-color"), panel) >= 3);
});

test("o tema global é independente dos modos e começa claro sem apagar a preferência escura", () => {
  const theme = readRequired("src/lib/corviaTheme.tsx");
  const main = readRequired("src/main.tsx");

  assert.deepEqual(
    [...new Set(quotedUnionValues(theme, "CorviaTheme"))].sort(),
    ["dark", "light"],
    "CorviaTheme deve aceitar somente dark e light",
  );
  assert.doesNotMatch(theme, /\b(?:complete|essential|scientific)\b/, "aparência não pode reutilizar o estado dos modos de trabalho");

  assert.match(theme, /\bDEFAULT_THEME\b[^=\n]*=\s*"light"/);
  assert.match(theme, /isCorviaTheme\(stored\) \? stored : DEFAULT_THEME/);
  assert.match(theme, /loginTheme \?\? readStoredTheme\(userId\)/);

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

test("a aparência continua no login e na conta, independente dos três modos de organização", () => {
  const view = readRequired("src/components/AtelierHomeView.tsx");
  const frame = readRequired("src/components/CardiologySpacesAppFrame.tsx");
  const login = readRequired("src/pages/Entrar.tsx");
  assert.match(login, /className="login-gateway__theme-choice login-gateway__theme-choice--top"/);
  assert.deepEqual([...login.matchAll(/id: "(light|dark)"/g)].map((match) => match[1]), ["light", "dark"]);

  const start = view.indexOf('<select aria-label="Modo de trabalho"');
  const end = view.indexOf("</select>", start);
  assert.ok(start >= 0 && end > start, "a organização precisa permanecer identificada por um select nativo");
  const modes = view.slice(start, end);
  assert.deepEqual([...modes.matchAll(/<option value="([^"]+)"/g)].map((match) => match[1]), ["complete", "essential", "scientific"]);
  assert.match(modes, /onChange=.*props\.onMode/);
  assert.doesNotMatch(modes, /CorviaThemeSelector|setTheme|toggleTheme/);
  assert.match(view, /<CorviaThemeSelector/);
  const accountStart = frame.indexOf('className="cv-account-menu"');
  const accountEnd = frame.indexOf("</div>", accountStart);
  const accountSelector = frame.indexOf("<CorviaThemeSelector", accountStart);
  assert.ok(accountStart >= 0 && accountSelector > accountStart && accountSelector < accountEnd);
});

test("a mesma marca arquitetônica identifica o topo e o catálogo de tarefas", () => {
  const frame = readRequired("src/components/CardiologySpacesAppFrame.tsx");
  assert.match(frame, /const logoSrc = "\/atelier\/corvia-logo-atelier\.svg"/);
  assert.equal([...frame.matchAll(/<img src=\{logoSrc\} alt="CorVIA Cardiology Spaces"/g)].length, 2);
  const logo = readRequired("public/atelier/corvia-logo-atelier.svg");
  assert.match(logo, /<svg/);
  assert.doesNotMatch(logo, /<script|<foreignObject|(?:href|src)=["']https?:\/\//i);
});

test("cinco ambientes reais possuem WebP responsivo e não mudam conforme o modo de organização", () => {
  const view = readRequired("src/components/AtelierHomeView.tsx");
  const home = readRequired("src/pages/CardiologySpacesHome.tsx");
  const styles = readRequired("src/styles/corvia-atelier.css");
  assert.match(home, /const availableSpaces = SPACES;/);
  assert.match(view, /srcSet=/);
  assert.match(view, /loading=\{/);
  assert.doesNotMatch(view, /LIGHT_SCENE_BY_SPACE|SCIENTIFIC_SPACES|<canvas|GalaxyThemeToggle|UniverseStars/);
  for (const space of ["consultorio", "hospital", "ensino", "pesquisa", "gestao"]) {
    for (const suffix of ["", "-small"]) {
      const path = "public/atelier/atelier-" + space + suffix + ".webp";
      assert.ok(existsSync(fileURLToPath(sourceUrl(path))), path + " precisa existir");
      const bytes = readFileSync(sourceUrl(path));
      assert.equal(bytes.toString("ascii", 0, 4), "RIFF");
      assert.equal(bytes.toString("ascii", 8, 12), "WEBP");
      assert.ok(bytes.byteLength <= (suffix ? 180_000 : 650_000), path + " precisa continuar otimizado");
    }
  }
  assert.doesNotMatch(styles, /\b(?:invert|hue-rotate)\s*\(/i);
});

test("paleta Atelier separa texto legível de cobre polido e preserva foco contrastante", () => {
  const content = readRequired("src/styles/corvia-atelier-content.css");
  const styles = readRequired("src/styles/corvia-atelier.css");
  const textColors = ["#24343a", "#58666a", "#16776d"];
  for (const foreground of textColors) {
    assert.ok(content.includes(foreground), foreground + " precisa estar na camada real de conteúdo");
    for (const background of ["#fffdfa", "#f6f3eb"]) {
      assert.ok(content.includes(background));
      assert.ok(contrastRatio(foreground, background) >= 4.5, foreground + " precisa atingir 4,5:1 sobre " + background);
    }
  }
  assert.ok(content.includes("#b66d48"), "cobre continua como acento, não como tinta de leitura");
  for (const background of ["#d39770", "#f2d1af", "#d8a27c", "#c98c66", "#e2b18d"]) {
    assert.ok(styles.includes(background), "reflexo do cobre precisa existir no controle real");
    assert.ok(contrastRatio("#1e2a22", background) >= 4.5, "CTA precisa manter contraste em cada reflexo do cobre");
  }
  assert.match(styles, /:focus-visible\{outline:3px solid #167d71/);
  assert.ok(contrastRatio("#167d71", "#fffdfa") >= 3);
  assert.ok(contrastRatio("#ffffff", "#b31f3a") >= 4.5, "emergência conserva contraste de texto");
});

test("a tarefa tem cabeçalho funcional com foco reversível e conteúdo sem fotografia", () => {
  const frame = readRequired("src/components/CardiologySpacesAppFrame.tsx");
  const styles = readRequired("src/styles/corvia-atelier.css");
  assert.match(frame, /<header className="atelier-taskbar">/);
  assert.match(frame, /className="atelier-taskbar__title"><Icone nome=\{route\.icon\}/);
  assert.match(frame, /aria-pressed=\{focusMode\}/);
  assert.match(frame, /Sair do foco/);
  assert.match(frame, /Trocar função/);
  assert.doesNotMatch(frame, /<ClinicalFunctionFigure|className="cv-space-horizon"|className="cv-function-deck"/);
  assert.match(styles, /\.atelier-app--focus \.atelier-taskbar\{position:sticky;top:0/);
  assert.match(styles, /\.atelier-app \.cv-content\{[^}]*background:var\(--atelier-paper\)!important/);
});

test("a cascata preserva contraste legado e aplica Atelier por último com conteúdo clínico escopado", () => {
  const main = readRequired("src/main.tsx");
  const theme = readRequired("src/lib/corviaTheme.tsx");
  const selectorStyles = readRequired("src/styles/corvia-theme-selector.css");
  const lightStyles = readRequired("src/styles/cardiology-spaces-light-mode.css");
  const content = readRequired("src/styles/corvia-atelier-content.css");
  const surfaces = readRequired("src/styles/corvia-atelier-surfaces.css");
  const imports = [...main.matchAll(/^\s*import\s+["']([^"']+\.css)["'];?/gm)].map((match) => match[1]);
  const expected = ["./styles/corvia-theme-selector.css", "./styles/clinical-form-control-contrast.css",
    "./styles/cardiology-spaces-light-mode.css", "./styles/corvia-atelier.css", "./styles/corvia-atelier-content.css", "./styles/corvia-atelier-surfaces.css"];
  for (let index = 0; index < expected.length; index += 1) {
    assert.ok(imports.includes(expected[index]), expected[index] + " precisa permanecer importado");
    if (index) assert.ok(imports.indexOf(expected[index - 1]) < imports.indexOf(expected[index]));
  }
  assert.equal(imports.at(-1), expected.at(-1));
  assert.match(theme, /root\.dataset\.corviaDesign = "atelier"/);
  assert.ok(pxMinimums(selectorStyles).some((value) => value >= 44));

  for (const [source, scope] of [[lightStyles, /^html\[data-corvia-theme=(?:"light"|'light')\]/],
    [content, /^html\[data-corvia-design=(?:"atelier"|'atelier')\]/],
    // Recovery/loading can render before the theme provider mounts; those
    // three explicitly named component boundaries are the only exceptions.
    [surfaces, /^(?:html\[data-corvia-design=(?:"atelier"|'atelier')\]|#root (?:\.app-recovery--atelier\b|\.corvia-loading-state\b|\.atelier-coming-soon(?:__light)?\b|:is\(\.app-recovery--atelier, \.atelier-coming-soon\)))/]]) {
    const rules = cssRules(source);
    assert.ok(rules.length >= 8);
    const unscoped = rules.flatMap(({ header }) => splitSelectorList(header)).filter((selector) => !scope.test(selector));
    assert.deepEqual(unscoped, [], "a mudança visual não pode escapar do escopo explícito");
  }
  for (const surface of [".cv-content", ".agenda-modal", ".legal-page", ".cc-", ".cv-page-hero"]) {
    assert.ok(content.includes(surface), surface + " precisa receber adaptação do conteúdo");
  }
  assert.match(content, /color-scheme:\s*light/);
  assert.match(content, /font-size:\s*16px/);
  assert.ok(pxMinimums(content).some((value) => value >= 44));
  assert.match(content, /prefers-reduced-motion/);
  assert.match(lightStyles, /\.clinical-os\s+input:not\(\[type="checkbox"\]\):not\(\[type="radio"\]\)[^{]+\{[^}]*background-color:\s*#ffffff\s*!important/s);
});
