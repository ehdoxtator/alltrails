# AllTrails Take Home Assignment

# Intro
This README contains information regarding the AllTrails take home assignment for Ed Doxtator.

# Requirements

| Item | Notes |
---|---
| Python Runtime Used | Python 3.9. Did not test other versions |
| pytest | 6.2.4 Required. |
| pandas | 1.3.2 Required. |
| numpy | 1.21.1 Required. |
| pytest-sugar | 0.9.4 Optional. |


# Installation

This application is hosted on git, and can be installed to a local directory with:

# Items In Release
| Item | Notes |
---|---
| .gitignore | Standard Python .gitignore file |
| README.md | This file | 
| \_\_init__.py | Python-required file for namespace separation |
| at\_tool.py | Support functions for at\_user\_date\_diff.py |
| at\_user\_date\_diff.py | Main driver, loads, joins, extracts, and filters data. Saves to an output CSV. |
| pytest.ini | pytest configuration|
| recordings_2017.tsv	| AT-supplied input CSV |
| test\_at\_tool.py | Unit tests for at\_tool.py|
| users_2017.tsv | AT-supplied input CSV |

# Usage
Once the code is installed, you can run from the command line with

```bash
% python at_user_date_diff.py <output-file.csv>
```

The program runs and produces a log similar to the following:

```
(py39) edoxtator@Eds-MacBook-Air alltrails % python at_user_date_diff.py test_output.csv 
INFO-2021-08-22 14:39:06,416: Loading data from recordings_2017.tsv...
INFO-2021-08-22 14:39:11,419: Cleaning dataframe...
INFO-2021-08-22 14:39:11,420: Validating dataframe...
INFO-2021-08-22 14:39:11,477: Loading data from users_2017.tsv...
INFO-2021-08-22 14:39:16,306: Cleaning dataframe...
INFO-2021-08-22 14:39:16,307: Validating dataframe...
INFO-2021-08-22 14:39:16,439: Joining 2 dataframes... 
INFO-2021-08-22 14:39:20,557: Dataframes joined. After joining, shape is (360202, 10)
INFO-2021-08-22 14:39:20,810: Extracting summary data from 360202 rows...
INFO-2021-08-22 14:39:23,942: Summary retrieved. 7018 rows without summary data.
INFO-2021-08-22 14:39:25,863: After adding summary info, shape is (360202, 20)
INFO-2021-08-22 14:39:25,863: Cleaning dataframe...
INFO-2021-08-22 14:39:26,452: Filtering out invalid rows...
INFO-2021-08-22 14:39:26,754: After filtering, shape is: (83839, 23)
INFO-2021-08-22 14:39:26,754: Writing dataframe to test_output.csv...
INFO-2021-08-22 14:39:31,049: Done.

```


# Unit Tests

All unit tests were written under pytest. To run all the unit tests, run pytest as follows:

```bash
% python -m pytest -v test_at_tool.py
```

The pytest-sugar module is mentioned as an add-on module. It makes pytest logs easier to read, but it is not required. pytest captures the log messges, so they will not be logged to the console.

# Assumptions
A number of assumptions were made to complete this assignment:

1. The input filenames are static. If this were a real production program, these names should be overridable through command line parameters.
2. The application runs in a single directory for simplicity and the app does not clean up after itself-- any detrius from previous runs is left in the application directory.
3. We make a lot of assumptions about the data's validity. If the data is internally sourced, then there may be processes in place that clean the data prior to this application's processing. If the data is externally sourced, then we cannot vouch for the cleanliness of the dataset. The main cleaning occurs when:
	* Normalizing the column names (so they match more closely with database column naming standards)
	* When appending the summary data to the user + recording dataset, if there is no valid JSON summary data, the additional summary columns for that row are defaulted
	* After the final dataset is complete, the dataset is filtered on a the date time delta column (start date - signup date). If the time delta is null, the row is dropped from the output file


