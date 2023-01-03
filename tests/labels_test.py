from wholeslidedata.annotation.labels import (
    Label,
    Labels,
    LabelValueError,
    NegativeLabelValueWarning,
)
import pytest


def test_create_label_with_label():
    label1 = Label(name="label_name", value=1)
    label2 = Label.create(label1)
    label1 == label2


def test_create_label_with_dict():
    label_dict = dict(name="label_name", value=1)
    label2 = Label.create(label_dict)
    assert label_dict["name"] == label2.name
    assert label_dict["value"] == label2.value


def test_create_label_with_str():
    label = Label.create(label="label_name", value=1)
    assert "label_name" == label.name
    assert 1 == label.value


def test_label_to_dict():
    label = Label.create(label="label_name", value=1)
    label_dict = label.todict()
    label_dict == dict(label="label_name", value=1)


def test_create_labels_with_labels():
    label1 = Label(name="label_name", value=1)
    labels1 = Labels([label1])
    labels2 = Labels.create(labels1)
    assert labels1 == labels2


def test_create_labels_with_dict():
    labels_dict = dict(label1=1, label2=2)
    labels = Labels.create(labels_dict)
    l1 = labels.get_label_by_name("label1")
    l2 = labels.get_label_by_name("label2")
    assert l1.name == "label1"
    assert l1.value == 1
    assert l2.name == "label2"
    assert l2.value == 2


class TestLabel:
    def test_init(self):
        label = Label(name="label1", value=1)
        assert label.name == "label1"
        assert label.value == 1
        with pytest.raises(LabelValueError):
            Label(name="label1", value="invalid")

    def test_eq(self):
        label1 = Label(name="label1", value=1)
        label2 = Label(name="label1", value=1)
        label3 = Label(name="label2", value=2)
        assert label1 == label2
        assert label1 != label3
        assert label1 != "invalid"

    def test_todict(self):
        label = Label(name="label1", value=1)
        assert label.todict() == {"name": "label1", "value": 1}

    def test_str(self):
        label = Label(name="label1", value=1)
        assert str(label) == "Label(name=label1, value=1)"

    def test_negative_value(self):
        with pytest.warns(NegativeLabelValueWarning):
            Label(name="label1", value=-1)


class TestLabels:
    def test_init(self):
        labels = Labels([Label(name="label1", value=1), Label(name="label2", value=2)])
        assert len(labels) == 2
        assert labels.names == ["label1", "label2"]
        assert labels.values == [1, 2]
        assert labels.map == {"label1": 1, "label2": 2}
        assert labels.name_map == {
            "label1": Label(name="label1", value=1),
            "label2": Label(name="label2", value=2),
        }
        assert labels.value_map == {
            1: Label(name="label1", value=1),
            2: Label(name="label2", value=2),
        }

    def test_getitem(self):
        labels = Labels([Label(name="label1", value=1), Label(name="label2", value=2)])
        assert labels[0] == Label(name="label1", value=1)
        assert labels[1] == Label(name="label2", value=2)
        with pytest.raises(IndexError):
            labels[2]

    def test_setitem(self):
        labels = Labels([Label(name="label1", value=1), Label(name="label2", value=2)])
        labels[0] = {"name": "label3", "value": 3}
        assert labels[0] == Label(name="label3", value=3)
        with pytest.raises(TypeError):
            labels[0] = "invalid"

    def test_iter(self):
        labels = Labels([Label(name="label1", value=1), Label(name="label2", value=2)])
        assert list(labels) == [
            Label(name="label1", value=1),
            Label(name="label2", value=2),
        ]

    def test_get_label_by_value(self):
        labels = Labels([Label(name="label1", value=1), Label(name="label2", value=2)])
        assert labels.get_label_by_value(1) == Label(name="label1", value=1)
        with pytest.raises(KeyError):
            labels.get_label_by_value(3)

    def test_get_label_by_name(self):
        labels = Labels([Label(name="label1", value=1), Label(name="label2", value=2)])
        assert labels.get_label_by_name("label1") == Label(name="label1", value=1)
        with pytest.raises(KeyError):
            labels.get_label_by_name("label3")
