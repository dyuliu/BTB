# -*- coding: utf-8 -*-

from unittest import TestCase
from unittest.mock import MagicMock, patch

import numpy as np
from copulas.univariate import Univariate
from sklearn.gaussian_process import GaussianProcessRegressor

from btb.tuning.metamodels.gaussian_process import (
    GaussianCopulaProcessMetaModel, GaussianProcessMetaModel)


class TestGaussianProcessMetaModel(TestCase):

    def test___init__(self):
        # run
        instance = GaussianProcessMetaModel()

        # assert
        assert instance._MODEL_KWARGS_DEFAULT == {'normalize_y': True}
        assert instance._MODEL_CLASS == GaussianProcessRegressor

    def test__predict(self):
        # setup
        instance = MagicMock()
        instance._model_instance.predict.return_value = [[1], [2]]

        # run
        result = GaussianProcessMetaModel._predict(instance, 1)

        # assert
        instance._model_instance.predict.assert_called_once_with(1, return_std=True)
        np.testing.assert_array_equal(result, np.array([[1, 2]]))


class TestGaussianCopulaProcessMetaModel(TestCase):

    def test___init__(self):
        # run
        instance = GaussianCopulaProcessMetaModel()
        # assert
        assert instance._MODEL_KWARGS_DEFAULT == {'normalize_y': True}
        assert instance._MODEL_CLASS == GaussianProcessRegressor

    def test__trasnform(self):
        # setup
        instance = MagicMock()
        trials = np.array([
            [0.1, 0.8, 0.2],
            [0.7, 0.6, 0.4],
            [0.4, 0.2, 0.3],
            [0.7, 0.8, 0.9],
            [0.2, 0.3, 0.4]
        ])

        distributions = []
        for column in trials.T:
            distribution = Univariate()
            distribution.fit(column)
            distributions.append(distribution)

        instance._distributions = distributions

        # run
        result = GaussianCopulaProcessMetaModel._transform(instance, trials)

        # assert
        expected_result = np.array([
            [-0.93051407, 0.72584367, -1.05823838],
            [0.78865964, 0.1155097, 0.3732126],
            [-0.04619363, -0.96388991, -0.49278658],
            [0.78865964, 0.72584367, 1.82607428],
            [-0.60472608, -0.66069297, 0.3732126]
        ])

        np.testing.assert_allclose(result, expected_result)

    @patch('btb.tuning.metamodels.gaussian_process.super')
    def test__fit(self, mock_super):
        # setup
        instance = GaussianCopulaProcessMetaModel()
        trials = np.array([
            [0.1, 0.8, 0.2],
            [0.7, 0.6, 0.4],
            [0.4, 0.2, 0.3],
            [0.7, 0.8, 0.9],
            [0.2, 0.3, 0.4]
        ])
        scores = np.array([0.1, 0.4, 0.8, 0.9])

        # run
        instance._fit(trials, scores)

        # assert
        expected_trials = np.array([
            [-0.93051407, 0.72584367, -1.05823838],
            [0.78865964, 0.1155097, 0.3732126],
            [-0.04619363, -0.96388991, -0.49278658],
            [0.78865964, 0.72584367, 1.82607428],
            [-0.60472608, -0.66069297, 0.3732126]
        ])
        expected_scores = np.array([
            -0.98370794,
            -0.33734483,
            0.50839651,
            0.75551369
        ])

        mock_fit_call = mock_super.return_value._fit.call_args_list
        np.testing.assert_allclose(expected_trials, mock_fit_call[0][0][0])
        np.testing.assert_allclose(expected_scores, mock_fit_call[0][0][1])
