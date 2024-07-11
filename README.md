# Querium-2.0
A Search Engine called: Querium, version 2.0

Languages: 🇧🇷 & 🇺🇸

## Querium V2.0

O Querium, em sua versão 2.0, traz uma grande evolução. A principal mudança está no seu _crawler_. Como o objetivo é que o Querium seja semelhante a um mecanismo de busca profissional, implementamos grandes modificações no seu _crawler_ com o intuito de indexar páginas mais rapidamente com processamento paralelo. Além disso, agora o _crawler_ consegue renderizar páginas dinâmicas que exigem JavaScript.

## Processamento paralelo

O Querium agora utiliza a biblioteca `ThreadPoolExecutor` do Python, que permite realizar processamento paralelo, tornando o processo de _crawling_ e _scraping_ mais ágil. Com essa funcionalidade, o Querium consegue processar várias páginas simultaneamente em _threads_ diferentes, com um nível de paralelismo completamente ajustável.

## Renderização de páginas dinâmicas

Essa funcionalidade tem dois propósitos principais. O primeiro, como já mencionado, é permitir que o _crawler_ indexe páginas construídas com _frameworks_ que utilizam JSX ou que requerem JavaScript para renderização (React.js, Vue, Next.js, Angular etc.), algo que antes não era possível. O segundo propósito é servir como um sistema para "bypass" ou "contornar" problemas relacionados ao bloqueio de _bots_ por alguns _sites_. Alguns _sites_ implementam mecanismos de segurança que bloqueiam _bots_ com base em interações suspeitas na página ou ativam CAPTCHAs para evitar ataques de DoS ou DDoS. O novo sistema do Querium atua como um `fake_usaragent`, porém de forma mais eficaz. Basicamente, ele utiliza o Selenium (headless) para emular um navegador Firefox (por ser mais leve). Inicialmente, o Querium tenta realizar o _crawling_ e _scraping_ utilizando as bibliotecas `BeautifulSoup` e `requests`, pois são mais rápidas, leves e funcionais. Caso a página necessite de JavaScript ou retorne erros 501, 502 ou 503, o Querium tenta novamente, mas desta vez utilizando o Selenium, que emula um usuário real e renderiza as páginas de forma mais completa, o que permite contornar os problemas mencionados. Além disso, ele também aceita _cookies_. Tudo isso em paralelo

## Novo _Crawler_ saves

Anteriormente, o _crawler_ realizava todo o processo de _crawling_ e _scraping_ de uma vez e armazenava os dados na memória de uma variável, salvando tudo em um arquivo JSON ao final. Essa abordagem consumia muita memória e era ineficiente para lidar com grandes volumes de dados. Agora, o processo foi otimizado. Implementamos um sistema de "steps", utilizando o parâmetro `save_interval`, que define a quantidade de páginas processadas antes de realizar um salvamento. Após processar o número de páginas definido em `save_interval`, o _crawler_ salva os dados em um arquivo JSON e limpa a memória. Ao final do processo, ele reúne todos os arquivos JSON gerados em um único arquivo final. Ainda estamos trabalhando em um controle mais eficiente do uso de memória, e nas próximas versões, pretendemos substituir o salvamento em JSON por um banco de dados.

## Indexer

As principais mudanças foram implementadas no sistema de pontuação. Anteriormente, utilizávamos apenas a pontuação da URL. Agora, também consideramos a classificação do conteúdo. O sistema de análise de conteúdo ainda será aprimorado, mas, por enquanto, estamos utilizando uma IA de classificação para analisar os textos extraídos de cada página indexada e classificá-los em um total de 20 categorias. Essas categorias serão utilizadas pelo mecanismo de busca. A IA utilizada é a **finbert**, disponível no Hugging Face: **nickmuchi/finbert-tone-finetuned-finance-topic-classification** (https://huggingface.co/nickmuchi/finbert-tone-finetuned-finance-topic-classification).

## PageRank

Sem mudanças significativas até o momento.

## Conclusão

Querium está evoluindo cada vez mais como um projeto open-source. Futuramente poderá ser um concorrente a Search Engines já existentes, e um estímulo a SE open-source. Poderá ser usando como um SE para IAs, isso é uma das ideias inicias do Querium. No entanto isso poder ser uma fragilidade pois os "fatores de indexação", segredo guardado a sete chaves dos SE, para evitar SEO que beneficie muito uma página inútil, esse segredo estaria publico. Mas uma das soluções é que cada um aplique suas regras e técnicas de Indexação em sua versão, enfim, no futuro decidiremos isso.

Não faremos um WebUI ainda, só após evoluções futuras do projeto.

O foco principal desta versão foi aprimorar o _crawler_ para que ele esteja no mesmo nível dos _crawlers_ utilizados pelos mecanismos de busca modernos e profissionais. Nas próximas versões, vamos focar em melhorar o gerenciamento de memória, o armazenamento de dados e a capacidade de indexar outros tipos de arquivos, como PDFs, imagens etc. 

Uma Searche Engine como qualquer software exige que todos os seus módulos funcionem corretamente e "perfeitamente", para o software como inteiro funcionar bem. Por isso estamos focando em certas partes do sistema aos poucos, melhorando o máximo possível de um para depois passarmos para o outro sistema. Esse update foi mais focado no Crawler, e ele ainda sofrerá grandes mudanças até julgarmos que ele chegou há um apogeu de eficiência satisfatório para enfim passarmos para outras partes desse sistema.

# English Version:

### Querium V2.0: A Major Leap Forward

Querium 2.0 represents a significant evolution in the project. The most impactful change resides in its crawler. Aiming to rival professional search engines, we've implemented substantial modifications to expedite page indexing through parallel processing. Additionally, the crawler can now render dynamic JavaScript-heavy pages.

### Parallel Processing for Enhanced Speed

Leveraging Python's `ThreadPoolExecutor` library, Querium now performs parallel processing, drastically accelerating crawling and scraping. This enables simultaneous processing of multiple pages across independent threads, with a fully customizable level of parallelism.

### Rendering Dynamic Pages: Unlocking the Web

This functionality serves two primary purposes. First, it empowers the crawler to index pages built with JSX frameworks or those requiring JavaScript for rendering (React.js, Vue, Next.js, Angular, etc.), a capability previously absent. Second, it acts as a system to bypass bot detection mechanisms employed by certain websites. 

Some sites implement security measures that block bots based on suspicious interactions or deploy CAPTCHAs to prevent DoS/DDoS attacks. Querium's new system effectively acts as a sophisticated `fake_useragent`. It utilizes Selenium (headless mode) to emulate a Firefox browser (chosen for its lightweight nature).

Initially, Querium attempts crawling and scraping using the faster and more efficient `BeautifulSoup` and `requests` libraries. If a page relies on JavaScript or returns 501, 502, or 503 errors, Querium switches to Selenium, which emulates real user behavior and comprehensively renders pages, successfully circumventing these obstacles.  This system also handles cookies seamlessly, and all of this occurs in parallel.

### Revamped Crawler Saving System for Efficiency

Previously, the crawler performed the entire crawling and scraping process in one go, storing data in memory before saving it to a JSON file at the end. This approach proved memory-intensive and inefficient for large datasets.

We've optimized this process by implementing a "step-based" system using the `save_interval` parameter, which defines the number of pages processed before triggering a save. After processing the specified number of pages, the crawler saves the data to a JSON file and clears the memory. Upon completion, it merges all generated JSON files into a single final file.  We're actively working on more efficient memory management, and future versions will likely replace JSON storage with a database.

### Enhanced Indexer for Precise Results

The scoring system has undergone significant changes. Previously, we relied solely on URL scoring. Now, we also factor in content classification. While the content analysis system will be further refined, we currently utilize a classification AI to analyze extracted text from each indexed page and categorize it into 20 distinct categories. These categories will be used by the search engine. We are currently using the **finbert** AI model available on Hugging Face: **nickmuchi/finbert-tone-finetuned-finance-topic-classification** (https://huggingface.co/nickmuchi/finbert-tone-finetuned-finance-topic-classification).

### PageRank: Future Enhancements Planned

No significant changes have been made to PageRank in this version.

### Conclusion: Open-Source Innovation

Querium is steadily evolving as a robust open-source project. In the future, it has the potential to rival existing search engines and inspire further open-source SE development. One of the initial visions for Querium is its use as a search engine specifically for AI applications. 

However, this presents a potential challenge: the "ranking factors" – closely guarded secrets of commercial SEs to prevent SEO manipulation – would be publicly available. A possible solution is to allow for customization, where users can implement their own indexing rules and techniques in their versions of Querium. This is something we will decide upon in the future.

We will not be developing a WebUI at this stage; it will come later in the project's lifecycle.

This version primarily focused on elevating the crawler to the standards of those employed by modern, professional search engines.  Future versions will prioritize improved memory management, data storage, and the ability to index additional file types like PDFs and images.

Like any software, a robust search engine demands flawless functionality across all modules. Therefore, we're taking a focused approach, perfecting one system at a time before moving on to the next. This update centered around the crawler, and it will undergo further substantial enhancements until we deem it sufficiently efficient. Once we reach that milestone, we will shift our focus to other components of the system. 
