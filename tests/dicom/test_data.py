"""Exercise src/classes/dicom/data.py: the DicomData form each DICOM import fills in."""
from classes.dicom.data import DicomData


def test_new_dicom_data_starts_with_every_field_empty() -> None:
    """Check that a new DicomData holds None in every field.

    Fails if a field starts with a value, such as an empty list or a default diameter. The
    readers decide whether something was found by testing a field against None, so a field
    that starts filled looks like data the plan never contained.
    """
    assert set(vars(DicomData()).values()) == {None}


def test_reset_empties_every_field_that_init_declares() -> None:
    """Check that reset() returns every field __init__ declares to None.

    Fails, naming the field, when __init__ gains a field that reset() does not clear. The
    previous patient's value then survives into the next import, and a needle, a structure or
    a patient name from one plan could be shown or printed with another patient's plan.
    """
    data = DicomData()
    fields = vars(data)
    for name in fields:
        fields[name] = "left over from the previous import"
    data.reset()
    assert [name for name, value in vars(data).items() if value is not None] == []
