"""
Unit tests for crypto_utils.py.

Ensures features are created successfully by comparing to hand-calculated
figures.
"""

import unittest

import pandas as pd

import crypto_utils as cryp

DEC_ACCY = 5  # decimals to check for accuracy


class TestDesignMatrix(unittest.TestCase):

    def setUp (self):
        """Load design matrix we'll be testing."""
        x_cryptos = ['ltc', 'xrp', 'xlm', 'eth']
        y_crypto = 'btc'
        kwargs = {'n_rolling_price':1, 'n_rolling_volume':2,
                  'x_assets':['SP500'], 'n_std_window':20}

        self.dm = cryp.DesignMatrix(x_cryptos=x_cryptos, y_crypto=y_crypto,
                                    **kwargs)

    def test_load_time_series (self):
        """Ensure initial time series is created successfully by comparing
        price- and volume-change data.
        """
        self.dm._load_time_series()
        df = self.dm.df
        # Define expected results.
        dt_1 = pd.to_datetime('3/1/2018')
        dt_2 = pd.to_datetime('2/10/2018')

        expected = [('SP500', dt_1, -0.013324),
                    ('btc', dt_1, 0.053193),
                    ('btc_volume', dt_1, 0.05040065),
                    ('eth', dt_2, -0.026542),
                    ('eth_volume', dt_2, -0.209714)]
        for (col, idx, value) in expected:
            msg = '{0} value not what expected on {1}'.format(
                  col, cryp.fmt_date(idx))
            actual_value = df.loc[idx, col]
            self.assertAlmostEqual(value, actual_value, DEC_ACCY, msg)

        ##############################
        # Test non-crypto-asset (SPX) to ensure returns properly rolled forward.
        ##############################
        # Return on 1/13/2018 (Saturday), 1/14 (Sunday), and 1/15 (MLK day)
        # should all be equal to the return on 1/12 (Friday).
        # Next "new" return should be on 1/16 (price change from 1/12 to 1/16).
        expected_return_1 = 0.006750  # index change from 1/11 -> 1/12.
        expected_return_2 = -0.003524  # index change from 1/12 -> 1/16.
        expected_spx = [(pd.to_datetime('1/12/2018'), expected_return_1),
                        (pd.to_datetime('1/13/2018'), expected_return_1),
                        (pd.to_datetime('1/14/2018'), expected_return_1),
                        (pd.to_datetime('1/15/2018'), expected_return_1),
                        (pd.to_datetime('1/16/2018'), expected_return_2)]

        for (idx, value) in expected_spx:
            msg = 'SP500 return on {} not what expected.'.format(
                  cryp.fmt_date(idx))
            actual_value = df.loc[idx, 'SP500']
            self.assertAlmostEqual(value, actual_value, DEC_ACCY, msg)

    def test_standardize_crypto_figures (self):
        self.dm._load_time_series()
        self.dm._standardize_crypto_figures()
        df = self.dm.df

        # Define expected results.
        # Rolling figures for 7/1 were standardized by data from 20-day
        # window between 6/11 - 6/30 (inclusive).
        test_date = pd.to_datetime('7/1/2016')

        expected = [('btc_px_std', test_date, -0.087190233),
                    ('btc_volume_std', test_date, -0.402742414)]
        for (col, idx, value) in expected:
            msg = '{0} value not what expected on {1}'.format(
                  col, cryp.fmt_date(idx))
            actual_value = df.loc[idx, col]
            self.assertAlmostEqual(value, actual_value, DEC_ACCY, msg)



if __name__=='__main__':
    unittest.main()