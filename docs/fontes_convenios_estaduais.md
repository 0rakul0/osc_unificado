# Fontes de dados dos convenios estaduais

Inventario das fontes de convenios estaduais ja registradas no projeto. A ideia aqui e deixar claro onde buscar os dados, o que ja tem automacao e qual formato o pipeline espera quando os arquivos chegam na base local.

## Fontes com link oficial registrado

| UF | Fonte oficial registrada | Automacao no repo | Formato bruto esperado pelo pipeline |
| --- | --- | --- | --- |
| AC | [Portal de convenios](https://transparencia.ac.gov.br/convenios) / [Detalhamento PDF](https://transparencia.ac.gov.br/convenios/detalhamento-pdf) | Nao | `convenios_ac.csv` |
| AL | [Portal da Transparencia de Alagoas](https://transparencia.al.gov.br/convenio) | Sim: [baixar_convenios_al_transparencia.py](/D:/github/osc_unificado/utils/convenios/baixar_convenios_al_transparencia.py) | JSONs por ano e ZIPs `convenio-AAAA.zip` |
| AM | [Portal da Transparencia do Amazonas](https://www.transparencia.am.gov.br/) | Nao | planilhas legadas em `bases_convenios/AM` |
| AP | [Portal da Transparencia do Amapa](https://www.transparencia.ap.gov.br/) | Nao | `TERMO DE FOMENTO.xlsx` |
| DF | [Dados Abertos do DF](https://dados.df.gov.br/) | Nao | `dados_credor_convenios_DF.xlsx` |
| GO | [Busca de datasets de convenios no Dados Abertos GO](https://dadosabertos.go.gov.br/dataset/?q=convenios) | Sim: [baixar_convenios_go_dadosabertos.py](/D:/github/osc_unificado/utils/convenios/baixar_convenios_go_dadosabertos.py) | `convenios_2008_2018.zip` e downloads do CKAN |
| RN | [Consulta de convenios do RN](http://convenios.control.rn.gov.br/conveniorelsite.aspx) | Nao | CSVs anuais locais |
| RO | [Transferencias / convenios RO](https://transparencia.ro.gov.br/convenios/filtrartransferencias) | Nao | `convenios_por_ano - rondonia.xlsx` |
| RR | [API de despesa detalhada RR](https://api.transparencia.rr.gov.br/api/v1/portal/transparencia/visualizar-despesa-detalhada) | Nao | `dados_convenios_receita.xlsx` |
| SC | [Consulta SC Transferencias](https://consultas.sctransferencias.cge.sc.gov.br/) / [CSV de transferencias](https://sctransf-api.prod.okd4.ciasc.sc.gov.br/csv/transferencias) | Nao | `sc_transferencias.csv` |
| SP | [Portal Parcerias Sociais](http://www.parceriassociais.sp.gov.br) / [Termos e acordos](http://www.parceriassociais.sp.gov.br/OSC/Termos_Acordos) | Nao | `sp_parcerias_osc_enriquecido.csv/json` |

## UFs com parser mas sem link oficial ainda registrado no projeto

| UF | Formato bruto esperado | Observacao |
| --- | --- | --- |
| BA | planilhas locais em `bases_convenios/BA` | Falta registrar URL oficial no repositorio. |
| CE | `convenios_sem_fins_lucrativos.xlsx` | Falta registrar URL oficial no repositorio. |
| ES | `convenios-*.csv`, `aditivosconvenios-*.csv`, `conveniosexecucaoorcamentaria-*.csv` | Falta registrar URL oficial no repositorio. |
| MA | planilhas locais em `bases_convenios/MA` | Falta registrar URL oficial no repositorio. |
| MG | `convenios.xlsx` | Falta registrar URL oficial no repositorio. |
| MS | planilhas locais em `bases_convenios/MS` | Falta registrar URL oficial no repositorio. |
| MT | planilha principal mais `transparencia_csv.csv` auxiliar | Falta registrar URL oficial no repositorio. |
| PA | planilhas e CSVs locais em `bases_convenios/PA` | Falta registrar URL oficial no repositorio. |
| PB | `consolidado.xlsx` | Falta registrar URL oficial no repositorio. |
| PE | planilhas locais em `bases_convenios/PE` | Falta registrar URL oficial no repositorio. |
| PI | `convenios_pi_v2.xlsx` | Falta registrar URL oficial no repositorio. |
| PR | `CONVENIOS-*/TB_CONVENIO_EMPREENDIMENTO-*.csv` | Falta registrar URL oficial no repositorio. |
| RJ | `transferencias-voluntarias-aos-municipios-2015-a-2023.csv`, `transferencias-voluntarias-aos-municipios-2024.csv` e planilhas locais | Falta registrar URL oficial no repositorio. |
| RS | `ConveniosDespesa-RS.csv` ou `ConveniosDespesa-RS.xlsx` | Falta registrar URL oficial no repositorio. |
| SE | planilhas locais em `bases_convenios/SE` | Falta registrar URL oficial no repositorio. |
| TO | `convenios_completo.xlsx` | Falta registrar URL oficial no repositorio. |

## Comandos uteis

Baixar AL:

```powershell
python D:\github\osc_unificado\utils\convenios\baixar_convenios_al_transparencia.py
```

Baixar GO:

```powershell
python D:\github\osc_unificado\utils\convenios\baixar_convenios_go_dadosabertos.py
```

Processar todos os convenios depois que os brutos estiverem no lugar:

```powershell
python D:\github\osc_unificado\utils\convenios\processar_convenios.py
```

## Observacoes

- Este documento lista as fontes que ja aparecem no codigo e nas historias do projeto; ele nao garante que a URL continua ativa sem nova verificacao.
- Quando uma UF ainda nao tem link oficial registrado, o caminho mais seguro e registrar a URL de origem junto com um exemplo de arquivo bruto e, se possivel, adicionar um baixador dedicado em `utils/convenios/`.
