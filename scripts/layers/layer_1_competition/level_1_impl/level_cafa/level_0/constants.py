"""CAFA ontology constants."""

CAFA_ONTOLOGIES = ("F", "P", "C")


def validate_ontology(ontology: str) -> None:
    """Raise ValueError if ontology not in CAFA_ONTOLOGIES."""
    if ontology not in CAFA_ONTOLOGIES:
        raise ValueError(
            f"Invalid CAFA ontology: {ontology}. Expected one of {CAFA_ONTOLOGIES}"
        )
