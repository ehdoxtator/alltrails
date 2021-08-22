import pytest

import numpy as np

import at_tool
from at_user_date_diff import TSV_FILES


EXPECTED_RAW_COLUMNS = {'recordings_2017.tsv': ['Recording_ID', 'Date_Time', 'Pseudo_User_ID',
                                                'Activity_Type', 'Recording_Summary',
                                                'City', 'State', 'Country'],
                        'users_2017.tsv': ['Pseudo_User_ID', 'signup_date', 'start_date']
                        }

EXPECTED_CLEAN_COLUMNS = {'recordings_2017.tsv': ['recording_id', 'date_time', 'pseudo_user_id',
                                                  'activity_type', 'recording_summary',
                                                  'city', 'state', 'country'],
                           'users_2017.tsv': ['pseudo_user_id', 'signup_date', 'start_date']
                           }

EXPECTED_JOINED_COLUMNS = ['recording_id', 'date_time', 'pseudo_user_id', 'activity_type', 'recording_summary', 'city',
                           'state', 'country', 'signup_date', 'start_date']

EXPECTED_SUMMARY_COLUMNS = ['recording_id', 'date_time', 'pseudo_user_id', 'activity_type', 'recording_summary',
                            'city', 'state', 'country', 'signup_date', 'start_date', 'calories', 'duration',
                            'timetotal', 'updatedat', 'timemoving', 'paceaverage', 'speedaverage', 'distancetotal',
                            'elevationgain', 'elevationloss']


class TestAtTool:

    def setup_method(self):
        """General setup, load the required DFs
        """
        self.loaded_dfs = dict()
        for tsv in TSV_FILES:
            self.loaded_dfs[tsv] = at_tool.get_tsv(tsv)

    def test_get_tsv_file(self):
        """Make sure the TSV files loaded correctly
        """
        for tsv in EXPECTED_RAW_COLUMNS.keys():
            assert EXPECTED_RAW_COLUMNS[tsv] == self.loaded_dfs[tsv].columns.tolist(), \
                f"fail: {self.loaded_dfs[tsv].columns.tolist()}"

    def test_clean(self):
        """Make sure the cleaning function works correctly
        """
        for tsv in EXPECTED_RAW_COLUMNS.keys():
            df_clean = at_tool.clean(self.loaded_dfs[tsv])
            assert EXPECTED_CLEAN_COLUMNS[tsv] == df_clean.columns.tolist(), f"fail: {df_clean.columns.tolist()}"

    def test_validate(self):
        """Make sure the validation function works correctly
        """
        # Check for bad join column
        bad_join_column = None
        with pytest.raises(ValueError):
            _ = at_tool.validate(self.loaded_dfs[TSV_FILES[0]], bad_join_column)

        # Check for df with duff column values
        join_column = 'City'
        bad_df = self.loaded_dfs[TSV_FILES[0]].copy()
        bad_df['nando'] = np.nan
        with pytest.raises(ValueError):
            _ = at_tool.validate(bad_df, join_column)

    def test_join(self):
        """Make sure the join returns the right concatenation of columns
        """
        join_column = 'pseudo_user_id'
        join_dfs = {tsv: at_tool.validate(at_tool.clean(self.loaded_dfs[tsv]), join_column)
                    for tsv in EXPECTED_RAW_COLUMNS.keys()}

        join_df = at_tool.join(join_dfs, join_column)

        assert EXPECTED_JOINED_COLUMNS == join_df.columns.tolist(), f"fail: {join_df.columns.tolist()}"

    def test_get_summary(self):
        """Make sure the recording summary can be extracted and added to the df as individual columns
        """
        join_column = 'pseudo_user_id'
        join_dfs = {tsv: at_tool.validate(at_tool.clean(self.loaded_dfs[tsv]), join_column)
                    for tsv in EXPECTED_RAW_COLUMNS.keys()}

        join_df = at_tool.join(join_dfs, join_column)

        summary_df = at_tool.get_summary(join_df)

        assert summary_df.shape == (360202, 20)
        assert EXPECTED_SUMMARY_COLUMNS == summary_df.columns.to_list()

    def test_filter_df(self):
        """Make sure the full dataframe (user, recording, summary) can drop the rows where the timedelta is null
        """

        join_column = 'pseudo_user_id'
        join_dfs = {tsv: at_tool.validate(at_tool.clean(self.loaded_dfs[tsv]), join_column)
                    for tsv in EXPECTED_RAW_COLUMNS.keys()}

        join_df = at_tool.join(join_dfs, join_column)

        summary_df = at_tool.get_summary(join_df)
        time_df = at_tool.get_time_diff(summary_df)
        full_df = at_tool.get_time_diff(time_df)
        filtered_df = at_tool.filter_df(full_df, 'delta_start_signup')

        assert filtered_df.shape == (83839, 23)
