"""Files vendored from the MCI-GRU repository so ``jev_filings`` stands alone.

Each module is a verbatim copy of an MCI-GRU file with only its ``mci_gru.*``
imports rewritten to point here: ``input_manifest``, ``eodhd_prices``,
``quality_contract`` and ``input_observations`` from ``mci_gru/data/``,
``artifacts`` from ``mci_gru/evaluation/`` and ``hashing`` from ``mci_gru/utils/``. ``prediction_clock`` is
the one exception: it holds just the ``PredictionClock`` class (and the regex it
uses), copied verbatim out of ``mci_gru/data/pit.py``, because the rest of that
file needs PyTorch and the training pipeline.
"""
