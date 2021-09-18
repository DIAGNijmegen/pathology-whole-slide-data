from wholeslidedata.labels import Label, Labels


class TestLabels:
    def test_list_labels(self):
        label_names = ["label1", "label2"]
        labels = Labels.create(label_names)
        assert labels.names == label_names
        assert labels.values == [1, 2]
        assert labels.map == {"label1": 1, "label2": 2}
        assert labels.name_map == {
            "label1": labels.get_label_by_name("label1"),
            "label2": labels.get_label_by_name("label2"),
        }
        assert labels.value_map == {
            1: labels.get_label_by_value(1),
            2: labels.get_label_by_value(2),
        }

        label1 = labels.get_label_by_name("label1")
        assert label1.name == "label1"
        assert label1.value == 1

        label2 = labels.get_label_by_name("label2")
        assert label2.name == "label2"
        assert label2.value == 2

    def test_list_dict_labels(self):
        labels = [
            {
                "name": "label1",
                "value": 1,
                "weight": 1.0,
                "color": "red",
                "overlay_index": 0,
                "extra_option": 'extra_value'
            },
            {
                "name": "label2",
                "value": 2,
                "weight": 0.5,
                "color": "blue",
                "overlay_index": 1,
            },
        ]
        labels = Labels.create(labels)
        assert labels.names == ["label1", "label2"]
        assert labels.values == [1, 2]

        label1 = labels.get_label_by_name("label1")
        assert label1.weight == 1.0
        assert label1.color == "red"
        assert label1.overlay_index == 0

        label2 = labels.get_label_by_name("label2")
        assert label2.weight == 0.5
        assert label2.color == "blue"
        assert label2.overlay_index == 1

    def test_dict_labels(self):
        label_map = {'label1': 1, 'label2': 2}
        labels = Labels.create(label_map)
        assert labels.map == label_map

    def test_label_iteration(self):
        label_names = ["label1", "label2"]
        labels = Labels.create(label_names)
        assert ['label1',  'label2'] == [label.name for label in labels]
        
    def test_indexes(self):
        label_names = ["label1", "label2"]
        labels = Labels.create(label_names)
        assert ['label1',  'label2'] == [labels[0].name, labels[1].name]
        
    def test_set_item(self):
        label_names = ["label1", "label2"]
        labels = Labels.create(label_names)
        labels[1] = 'label3'
        labels[0] = Label.create(labels[0])
        assert ['label1',  'label3'] == [labels[0].name, labels[1].name]
    
    def test_length(self):
        label_names = ["label1", "label2"]
        labels = Labels.create(label_names)
        assert len(labels) == 2
        