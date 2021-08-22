import logging
import sys

import at_tool

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s: %(message)s')
logger = logging.getLogger(__name__)

TSV_FILES = ['recordings_2017.tsv', 'users_2017.tsv']
JOIN_COLUMN = 'pseudo_user_id'


def main(outfile, tsv_files=TSV_FILES, join_column=JOIN_COLUMN):

    joined_df = at_tool.join({tsv_file: at_tool.validate(at_tool.clean(at_tool.get_tsv(tsv_file)), join_column)
                              for tsv_file in tsv_files}, join_column)

    full_df = at_tool.get_time_diff(at_tool.get_summary(joined_df))

    filtered_df = at_tool.filter_df(full_df, 'delta_start_signup')

    at_tool.write_csv(filtered_df, outfile)


if __name__ == '__main__':
    outfile = 'full_filtered_result.csv'
    if len(sys.argv) ==2:
        outfile = sys.argv[1]

    main(outfile)
    logger.info("Done.")