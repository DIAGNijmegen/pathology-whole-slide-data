from wholeslidedata.mode import WholeSlideMode, create_mode
import pytest

class TestWholeSlideMode:
    def test_enum(self):
        assert WholeSlideMode.default.name == 'default'
        assert WholeSlideMode.default.value == 1
        assert WholeSlideMode.training.name == 'training'
        assert WholeSlideMode.training.value == 2
        assert WholeSlideMode.validation.name == 'validation'
        assert WholeSlideMode.validation.value == 3
        assert WholeSlideMode.test.name == 'test'
        assert WholeSlideMode.test.value == 4
        assert WholeSlideMode.inference.name == 'inference'
        assert WholeSlideMode.inference.value == 5

    def test_create_mode(self):
        assert create_mode('default') == WholeSlideMode.default
        assert create_mode('training') == WholeSlideMode.training
        assert create_mode('validation') == WholeSlideMode.validation
        assert create_mode('test') == WholeSlideMode.test
        assert create_mode('inference') == WholeSlideMode.inference
        with pytest.raises(KeyError):
            create_mode('invalid')
