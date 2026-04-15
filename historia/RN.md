# Rio Grande do Norte (RN)

## Visao geral

Rio Grande do Norte soma 422 registros no parquet estadual e 417 registros no parquet da capital Natal. No recorte estadual, a serie vai de 2000 a 2026; na capital, de 2018 a 2026.

No estado, a base atual concentra R$ 8.008.985.700,00 em transferencias com foco em convenios e instrumentos similares. Na capital, o parquet soma R$ 78.940.349.653,00 no recorte institucional que manteve contratos e parcerias com sinal forte de OSC.

## Leitura rapida

No estadual, os maiores volumes aparecem em entidades como `FUNCITERN`, `Hospital Infantil Varela Santiago`, `FAPERN`, `ACOSAP` e `NDS`. Isso sugere uma combinacao de pesquisa, saude e desenvolvimento social.

Na capital, os maiores valores ficaram concentrados em poucos contratos/parcerias, com destaque para `Sociedade Professor Heitor Carrilho`, `FUNDEP`, `FIPE` e outras instituicoes identificadas com CNPJ valido. Como a trilha de Natal veio da rota oficial de contratos, ela e util para detectar OSC e entidades parceiras, mas deve ser lida com cuidado quando a pergunta for exclusivamente "termo de fomento/colaboracao".

## Qualidade e limites

O parquet estadual de `RN` entrou com cobertura forte de `cnpj` e `objeto`, mas a serie historica traz muitos registros com `valor_total = 0`, o que pede cuidado na leitura financeira agregada por ano.

O parquet da capital tambem preserva `cnpj`, `objeto`, valor e vigencia. O ponto de atencao e metodologico: a fonte municipal nao separou de forma limpa uma aba exclusiva de convenios, entao a selecao final privilegiou contratos e instrumentos com sinal forte de OSC.

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\RN.parquet` (422 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\RN`.
- Exemplos de arquivos brutos estaduais: `rn_2001.csv`, `rn_2002.csv`, `rn_2007.csv`, `rn_2011.csv`, `rn_2013.csv`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_rn.py`, `utils/orcamento_geral/baixar_orcamento_geral_rn.py`.
- Fontes oficiais registradas para o estado: [convenios.control.rn.gov.br/conveniorelsite.aspx](http://convenios.control.rn.gov.br/conveniorelsite.aspx).

### Capital (Natal)

- Parquet da capital consolidado: `E:\dados\capitais_processada\RN_NATAL.parquet` (417 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Natal`.
- Exemplos de arquivos brutos da capital: `natal_contratos_2024_SMS.csv`, `natal_contratos_osc_enriquecido.json`, `natal_contratos_osc_falhas_listagem.json`, `natal_contratos_osc_resumo.json`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_natal.py`.
- Fontes oficiais registradas para a capital: [www2.natal.rn.gov.br/transparencia/contratos.php](https://www2.natal.rn.gov.br/transparencia/contratos.php), [www2.natal.rn.gov.br/transparencia/contratosVisualizar.php](https://www2.natal.rn.gov.br/transparencia/contratosVisualizar.php).

## Conclusao

Rio Grande do Norte ficou util em duas camadas: o estado ajuda a localizar entidades e instrumentos historicos de parceria, e Natal complementa a leitura municipal com nomes, CNPJs e valores de contratacoes/parcerias com forte sinal de OSC.
