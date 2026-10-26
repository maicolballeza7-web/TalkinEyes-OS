from core.confidence import ConfidenceCalculator


def test_calcular_retorna_cero_si_no_alcanza_frames_minimos() -> None:
    calculadora = ConfidenceCalculator()

    assert calculadora.calcular(9, 0.0) == 0.0


def test_calcular_combina_score_de_tiempo_y_profundidad() -> None:
    calculadora = ConfidenceCalculator()

    assert calculadora.calcular(10, 0.08) == 0.5


def test_calcular_limita_score_de_tiempo_a_uno() -> None:
    calculadora = ConfidenceCalculator()

    assert calculadora.calcular(20, 0.0) == 1.0


def test_calcular_limita_score_de_profundidad_a_cero() -> None:
    calculadora = ConfidenceCalculator()

    assert calculadora.calcular(20, 0.2) == 0.5
