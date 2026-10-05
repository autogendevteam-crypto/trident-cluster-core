<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# **LookIntoBitcoin: Analisi Completa per Trade Bot Solutions**

**LookIntoBitcoin**, fondato da Philip Swift nel 2019, rappresenta una delle piattaforme più affidabili per l'analisi on-chain di Bitcoin. Nel luglio 2024, la piattaforma è stata integrata con Bitcoin Magazine Pro attraverso una partnership strategica, mantenendo l'accesso gratuito agli indicatori chiave mentre espandendo le funzionalità premium.[^1][^2][^3]

## **Indicatori On-Chain Gratuiti Disponibili**

La piattaforma offre accesso gratuito a diversi indicatori fondamentali per l'analisi di mercato, senza necessità di registrazione:[^4][^5]

### **Pi Cycle Top Indicator**

L'indicatore **Pi Cycle Top** è il tool più celebre della piattaforma, sviluppato da Philip Swift nell'aprile 2019. Utilizza due medie mobili specifiche:[^6][^7]

- **111-Day Moving Average (111DMA)**: cattura i trend di breve termine
- **350-Day Moving Average x 2 (350DMA x2)**: fornisce prospettiva a lungo termine

**Interpretazione operativa**: Quando la 111DMA incrocia al rialzo la 350DMA x2, storicamente indica il picco del ciclo di mercato entro **3 giorni** di precisione. Il rapporto 350/111 = 3.153, molto vicino a Pi (3.142), da cui deriva il nome dell'indicatore.[^8][^7][^9][^6]

**Performance storica verificata**:[^9]

- **5 aprile 2013**: segnale 5 giorni prima del picco, -65.5% nei successivi 11 giorni
- **3 dicembre 2013**: segnale 1 giorno prima del picco, -86.11% in 623 giorni
- **16 dicembre 2017**: segnale 1 giorno prima del picco, -84.3% in 364 giorni
- **12 aprile 2021**: segnale 2 giorni prima del picco, -52.94% in 71 giorni


### **MVRV Z-Score**

Il **MVRV Z-Score** identifica periodi di estrema sovra/sottovalutazione di Bitcoin rispetto al "fair value". Utilizza tre componenti:[^10][^11]

1. **Market Value** (linea nera): prezzo attuale × supply circolante
2. **Realized Value** (linea blu): prezzo medio ponderato all'ultima movimentazione delle monete
3. **Z-Score** (linea arancione): deviazione standard che evidenzia gli estremi

**Segnali operativi**:[^12][^10]

- **Z-Score > 7**: condizioni euforiche, potenziale top di ciclo (zona rosa)
- **Z-Score < 0**: sottovalutazione estrema, opportunità di accumulo (zona verde)
- **Precisione storica**: ha identificato i massimi di ogni ciclo entro **2 settimane**


### **Net Unrealized Profit/Loss (NUPL)**

Il **NUPL** misura la differenza tra profitti e perdite non realizzati nel mercato. Formula: (Market Cap - Realized Cap) / Market Cap.[^13][^14]

**Zone interpretative**:[^13]

- **>0.75**: Greed/Euforia (zona rossa) - potenziale distribuzione
- **0.5-0.75**: Belief/Convinzione - mercato rialzista maturo
- **0.25-0.5**: Hope/Speranza - recovery iniziale
- **0-0.25**: Fear/Paura - accumulo opportunistico
- **<0**: Capitulation/Capitolazione - massima opportunità


### **Altri Indicatori Disponibili Gratuitamente**

- **HODL Waves**: distribuzione dell'età delle monete per cohort temporali
- **Address Balance Charts**: numero di wallet per fasce di holding (0.01, 0.1, 1, 10+ BTC)
- **Puell Multiple**: redditività dei miner vs media annuale
- **Stock-to-Flow Model**: rapporto scorte/produzione annuale
- **Rainbow Chart**: curve di crescita logaritmiche con bande colorate


## **Struttura dei Prezzi e Funzionalità Premium**

### **Tier Gratuito**

- Accesso a chart fondamentali aggiornati giornalmente
- Nessuna registrazione richiesta
- Spiegazioni dettagliate sotto ogni grafico[^5][^1]


### **Advanced Plan - \$29/mese** (fatturato annualmente)[^15][^16]

- Chart aggiornati con risoluzione oraria
- Alerts personalizzabili su +40 indicatori
- Newsletter settimanale con analisi
- Indicatori privati TradingView
- Macro Suite con liquidità globale, DXY, yields


### **Pro Plan - \$49/mese** (fatturato annualmente)[^16][^15]

- Accesso completo a Macro Suite
- Portfolio tools e dashboard interattivi
- Data download e API access
- Analisi video esclusive
- Supporto prioritario


## **Comparazione con Alternative**

### **vs Glassnode**

- **LookIntoBitcoin/BM Pro**: focus su Bitcoin, interfaccia più semplice, spiegazioni educative dettagliate
- **Glassnode**: copertura multi-asset, metriche più avanzate, prezzi superiori (\$29-\$799/mese)[^17][^18]


### **vs CryptoQuant**

- **LookIntoBitcoin**: chart gratuiti senza registrazione, indicatori proprietari (Pi Cycle)
- **CryptoQuant**: alerts gratuiti, exchange flows dettagliati, registrazione richiesta[^18]


## **Integrazione Operativa per Trade Bot Solutions**

### **Automazione con n8n**

Sebbene LookIntoBitcoin non offra API dirette gratuite, è possibile implementare:

1. **Web Scraping**: estrarre dati dai chart pubblici via n8n HTTP Request nodes
2. **Screenshot Analysis**: catturare chart visually e processarli con OCR
3. **RSS/Feed Monitoring**: tracciare aggiornamenti via social media di Philip Swift (@PositiveCrypto)

### **Segnali Operativi Automatizzabili**

**Pi Cycle Top Alert**:

```
IF 111DMA approaches 350DMA x2 → 
TRIGGER: Reduce long positions, prepare short signals
```

**MVRV Z-Score Signals**:

```  
IF Z-Score > 6 → SIGNAL: Distribution zone
IF Z-Score < 0 → SIGNAL: Accumulation zone
```

**NUPL Market Phase Detection**:

```
IF NUPL > 0.75 → Phase: Euphoria (sell signals)
IF NUPL < 0 → Phase: Capitulation (buy signals)
```


## **Vantaggi Competitivi per il Business**

### **Per la Generazione di Contenuti**

- **Chart visually appealing** per post Telegram/social
- **Spiegazioni educative** integrate per newsletter
- **Dati storicamente verificati** per credibilità


### **Per l'Analisi di Mercato**

- **Indicatori proprietari** non replicabili altrove (Pi Cycle)
- **Precisione storica documentata** per backtesting
- **Interfaccia intuitiva** per analisi rapide


### **Per il Monitoraggio Competitivo**

- **Philip Swift** come thought leader da seguire
- **Bitcoin Magazine Pro** come benchmark del settore
- **Community feedback** sui social per sentiment


## **Limitazioni da Considerare**

1. **Bitcoin-only focus**: non copre altcoin per analisi multi-asset
2. **No API gratuita**: richiede scraping o abbonamento premium per automazione
3. **Aggiornamento giornaliero**: tier gratuito non real-time per trading veloce
4. **Dipendenza da pattern storici**: efficacia potrebbe diminuire con maturazione del mercato[^8]

## **Raccomandazioni Operative**

### **Utilizzo Immediato (Gratuito)**

1. **Monitoraggio manuale giornaliero** di Pi Cycle Top e MVRV Z-Score
2. **Integrazione nei report settimanali** con screenshot dei chart chiave
3. **Content creation** usando le spiegazioni educative della piattaforma

### **Upgrade Strategico (Premium)**

1. **Advanced Plan** per alerts automatici e TradingView integration
2. **API access** per integrazione diretta con infrastruttura n8n/Docker
3. **Macro Suite** per correlazioni Bitcoin-tradfi essenziali per segnali

**LookIntoBitcoin/Bitcoin Magazine Pro** rappresenta uno strumento indispensabile per il tuo business di segnali crypto, combinando affidabilità storica, accessibilità gratuita e potenziale di automazione premium. L'integrazione graduale, partendo dalle funzionalità gratuite, permetterà di validare l'efficacia prima dell'investimento in tier premium.
<span style="display:none">[^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^33][^34][^35][^36][^37][^38][^39][^40][^41][^42][^43]</span>

<div style="text-align: center">⁂</div>

[^1]: https://www.cypherhunter.com/en/p/look-into-bitcoin/

[^2]: https://bitcoinmagazine.com/business/bitcoin-magazine-and-look-into-bitcoin-partner-to-launch-enhanced-bitcoin-magazine-pro

[^3]: https://www.linkedin.com/showcase/bitcoin-magazine-pro/

[^4]: https://medium.datadriveninvestor.com/free-on-chain-crypto-analysis-tools-list-9ec391a5a4e9

[^5]: https://www.binance.com/en/square/post/239228

[^6]: https://charts.bitbo.io/pi-cycle-top/

[^7]: https://www.blockchain.com/explorer/charts/pi-cycle-top-indicator

[^8]: https://www.bitcoinmagazinepro.com/charts/pi-cycle-top-indicator/

[^9]: https://newhedge.io/bitcoin/pi-cycle-top-indicator

[^10]: https://www.bitcoinmagazinepro.com/charts/mvrv-zscore/

[^11]: https://charts.bitbo.io/mvrv-z-score/

[^12]: https://charts.bgeometrics.com/mvrv.html

[^13]: https://www.bitcoinmagazinepro.com/charts/relative-unrealized-profit--loss/

[^14]: https://charts.bitbo.io/net-unrealized-profit-loss/

[^15]: https://www.bitcoinmagazinepro.com

[^16]: https://www.bitcoinmagazinepro.com/bitcoin-indicators/

[^17]: https://glassnode.com

[^18]: https://www.reddit.com/r/CryptoTrainingFree/comments/sd4txb/glassnode_vs_cryptoquant_which_is_the_best/

[^19]: https://www.bitcoinmagazinepro.com/charts/

[^20]: https://bitbo.io/tools/charts/

[^21]: https://blog.bitmex.com/top-bitcoin-indicators/

[^22]: https://www.bitcoinmagazinepro.com/blog/15-best-free-bitcoin-api-sources-for-seamless-blockchain-integration/

[^23]: https://charts.bitbo.io/mvrv/

[^24]: https://forklog.com/en/report-on-chain-indicators-point-to-the-end-of-bitcoins-capitulation-period/

[^25]: https://studio.glassnode.com/charts/indicators.PiCycleTop

[^26]: https://x.com/positivecrypto

[^27]: https://twitter.com/PositiveCrypto/status/1724064084339921110

[^28]: https://x.com/PositiveCrypto/status/1603748277735882755

[^29]: https://www.bitcoinmagazinepro.com/charts/bitcoin-investor-tool/

[^30]: https://bitcoinmagazine.com/markets/5-free-metrics-bitcoin-investor

[^31]: https://www.tradingview.com/script/vj0oe2nu-2-Year-MA-Multiplier/

[^32]: https://bitcoinmagazine.com/markets/3-signals-predict-bitcoin-big-move

[^33]: https://x.com/bitcoinmagpro

[^34]: https://www.bitcoinmagazinepro.com/charts/pi-cycle-top-prediction/

[^35]: https://twitter.com/PositiveCrypto/status/1712416947856355753

[^36]: https://www.mql5.com/en/market/product/66183

[^37]: https://bmpro.substack.com/p/3-month-free-trial-the-new-bitcoin

[^38]: https://www.nasdaq.com/articles/bitcoin-pi-cycle-top-indicator-how-accurately-time-market-cycle-peaks

[^39]: https://www.bitcoinmagazinepro.com/blog/a-comprehensive-on-chain-vs-chain-guide-for-bitcoin-investors/

[^40]: https://www.tradingview.com/script/BW9wJyuh-CryptoSignalScanner-Pi-Cycle-Golden-Ratio-Multiplier/

[^41]: https://research.ark-invest.com/hubfs/1_Download_Files_ARK-Invest/White_Papers/ARKInvest_123021_Whitepaper_OnChainData.pdf

[^42]: https://www.bitcoinmagazinepro.com/blog/top-11-bitcoin-tools-for-security-analytics-privacy-more/

[^43]: https://www.nasdaq.com/articles/bitcoin-magazine-and-look-bitcoin-partner-launch-enhanced-bitcoin-magazine-pro?time=1721235600

