from __future__ import annotations

from dataclasses import dataclass
import unicodedata


@dataclass(frozen=True)
class StateCapital:
    uf: str
    estado: str
    capital: str

    @property
    def aliases(self) -> tuple[str, ...]:
        values = {
            self.uf,
            self.estado,
            self.capital,
            ascii_slug(self.estado),
            ascii_slug(self.capital),
            ascii_slug(self.capital).replace("-", " "),
        }
        return tuple(sorted(value for value in values if value))


def ascii_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    text = normalized.encode("ascii", "ignore").decode("ascii")
    return "-".join(part for part in text.lower().replace("/", " ").split() if part)


def capital_parquet_name(uf: str, capital: str) -> str:
    normalized_capital = ascii_slug(capital).replace("-", "_").upper()
    return f"{uf.upper()}_{normalized_capital}.parquet"


STATE_CAPITALS: tuple[StateCapital, ...] = (
    StateCapital("AC", "Acre", "Rio Branco"),
    StateCapital("AL", "Alagoas", "Maceio"),
    StateCapital("AP", "Amapa", "Macapa"),
    StateCapital("AM", "Amazonas", "Manaus"),
    StateCapital("BA", "Bahia", "Salvador"),
    StateCapital("CE", "Ceara", "Fortaleza"),
    StateCapital("DF", "Distrito Federal", "Brasilia"),
    StateCapital("ES", "Espirito Santo", "Vitoria"),
    StateCapital("GO", "Goias", "Goiania"),
    StateCapital("MA", "Maranhao", "Sao Luis"),
    StateCapital("MT", "Mato Grosso", "Cuiaba"),
    StateCapital("MS", "Mato Grosso do Sul", "Campo Grande"),
    StateCapital("MG", "Minas Gerais", "Belo Horizonte"),
    StateCapital("PA", "Para", "Belem"),
    StateCapital("PB", "Paraiba", "Joao Pessoa"),
    StateCapital("PR", "Parana", "Curitiba"),
    StateCapital("PE", "Pernambuco", "Recife"),
    StateCapital("PI", "Piaui", "Teresina"),
    StateCapital("RJ", "Rio de Janeiro", "Rio de Janeiro"),
    StateCapital("RN", "Rio Grande do Norte", "Natal"),
    StateCapital("RS", "Rio Grande do Sul", "Porto Alegre"),
    StateCapital("RO", "Rondonia", "Porto Velho"),
    StateCapital("RR", "Roraima", "Boa Vista"),
    StateCapital("SC", "Santa Catarina", "Florianopolis"),
    StateCapital("SP", "Sao Paulo", "Sao Paulo"),
    StateCapital("SE", "Sergipe", "Aracaju"),
    StateCapital("TO", "Tocantins", "Palmas"),
)
