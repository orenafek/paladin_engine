import pandas as pd
import ast
import builtins
import json
from types import FunctionType

from PaladinEngine.archive.archive import Archive
from PaladinUI.paladin_server.paladin_server import PaladinServer


# ---------------------------------------------------------------------------------------------#
# ------------------------- DATAFRAMES CREATION -----------------------------------------------#
# ---------------------------------------------------------------------------------------------#

def _create_archive_from_csv(csv_path):
    dataframe = _load_csv_to_dataframe(csv_path)
    archive_from_csv = Archive()
    rows = dataframe.to_records()
    for row in rows:
        record_key, record_value = _create_record_key_value(row)
        archive_from_csv.store_with_original_time(record_key, record_value)
    return archive_from_csv


def _load_csv_to_dataframe(csv_path):
    dataframe = pd.read_csv(csv_path)
    dataframe = dataframe.fillna('')
    return dataframe


def _create_record_key_value(row):
    row_field = int(row.field) if row.field.isnumeric() else row.field
    record_key = Archive.Record.RecordKey(
        int(row.container_id), row_field, row.stub_name, Archive.Record.StoreKind[row.kind]
    )

    if record_key.stub_name == "__AS__" and row.rtype in ['list', 'dict', 'tuple', 'set']:
        value_of_record = ast.literal_eval(row.value)
        type_of_record = row.rtype
    elif row.rtype == 'function':
        value_of_record = row.value
        type_of_record = FunctionType
    elif row.rtype == 'list':
        value_of_record = ast.literal_eval(row.value)
        type_of_record = list
    elif row.rtype == 'bool':
        value_of_record = True if row.value == 'True' else False
        type_of_record = bool
    elif row.rtype == 'dict':
        value_of_record = ast.literal_eval(row.value)
        type_of_record = dict #TODO: add same for tuple and set
    elif record_key.stub_name == "__BREAK__":
        value_of_record = None
        type_of_record = object
    else:
        value_of_record = getattr(builtins, row.rtype)(row.value)
        type_of_record = type(value_of_record)

    record_value = Archive.Record.RecordValue(
        record_key, type_of_record, value_of_record, row.expression,
        int(row.line_no), int(row.time), row.extra
    )
    return record_key, record_value


def _convert_query_result_to_presentable_table(query_result):
    print(query_result)
    result = query_result['result']['query']
    if result == '""':
        raise Exception("Empty query result!")
    json_data = json.loads(result)
    json_data.pop('keys')
    result_df = pd.DataFrame.from_dict(json_data, orient="index")
    result_df.reset_index(inplace=True)
    times_column_name = 'Time Range'
    result_df = result_df.rename(columns={'index': times_column_name})
    return result_df


def _create_dataframe_from_csv(csv_file_path, query, start_time, end_time):
    csv_archive = _create_archive_from_csv(csv_file_path)
    server = PaladinServer.create('', csv_archive)
    raw_result = server.query(query, start_time, end_time)
    presentable_df = _convert_query_result_to_presentable_table(raw_result)
    return presentable_df


# ---------------------------------------------------------------------------------------------#
# ------------------------- MERGING -----------------------------------------------------------#
# ---------------------------------------------------------------------------------------------#


def _are_matching_rows(row1, row2, merge_condition_1, merge_condition_2):
    sub_row1 = row1[merge_condition_1]
    sub_row2 = row2[merge_condition_2]
    sub_row1.columns = [i for i in range(sub_row1.shape[1])]
    sub_row2.columns = [i for i in range(sub_row2.shape[1])]
    return sub_row1.equals(sub_row2)


def _search_for_next_match(table_a, index_a, table_a_unmatched_rows, table_b_unmatched_rows, merge_condition_a, merge_condition_b):
    index_a += 1

    if index_a >= len(table_a):
        return False, table_a_unmatched_rows, table_b_unmatched_rows, index_a

    row_a = table_a.iloc[[index_a]]
    table_a_unmatched_rows.append((row_a, index_a))
    is_match_found = False
    for i, (row2_unmatched, index2_unmatched) in enumerate(table_b_unmatched_rows):
        if _are_matching_rows(row_a, row2_unmatched, merge_condition_a, merge_condition_b):
            is_match_found = True
            table_b_unmatched_rows = table_b_unmatched_rows[:i + 1]
            break
    return is_match_found, table_a_unmatched_rows, table_b_unmatched_rows, index_a


def _print_matching_rows(result, row1, row2):
    row1.reset_index(drop=True)
    row2.reset_index(drop=True)
    merged_row = pd.concat([row1, row2], axis=1)
    result = pd.concat([result, merged_row], ignore_index=True)
    # print(result)
    return result


def _print_unmatching_rows(result, rows1, rows2, table1_columns, table2_columns):
    df1 = pd.DataFrame(columns=table1_columns)
    print(len(rows1), len(rows2))
    if not rows1.empty:
        print(type(rows1), rows1)
        for row in rows1:
            print(row, type(row), row.empty)
            df1 = pd.concat([df1, row])
        df1.reset_index(drop=True)
    df2 = pd.DataFrame(columns=table2_columns)
    if not len(rows2):
        for row in rows2:
            df2 = pd.concat([df2, row])
        df2.reset_index(drop=True)

    merged_block = pd.concat([df1, df2], axis=1)
    print(merged_block)
    print(result)
    result = pd.concat([result, merged_block], ignore_index=True)
    return result

# ---------------------------------------------------------------------------------------------#
# ------------------------- INTERACTIVE FUNCTIONS ---------------------------------------------#
# ---------------------------------------------------------------------------------------------#


def get_data(csv_file_path, query, suffix, start_time=0, end_time=500):
    dataframe = _create_dataframe_from_csv(csv_file_path, query, start_time, end_time)
    dataframe = dataframe.add_suffix(suffix)
    return dataframe


def merge_tables(table1, table2, merge_condition_1, merge_condition_2, suffix1, suffix2):
    table1_columns = table1.columns.values.tolist()
    table2_columns = table2.columns.values.tolist()
    all_columns = table1_columns + table2_columns
    result = pd.DataFrame(columns=all_columns)

    merge_condition_1 = [item + suffix1 for item in merge_condition_1]
    merge_condition_2 = [item + suffix2 for item in merge_condition_2]

    index1 = 0
    index2 = 0
    while index1 < len(table1) and index2 < len(table2):
        row1 = table1.iloc[[index1]]
        row2 = table2.iloc[[index2]]
        if _are_matching_rows(row1, row2, merge_condition_1, merge_condition_2):
            result = _print_matching_rows(result, row1, row2)
            index1 += 1
            index2 += 1
        else:
            table1_unmatched_rows = [(row1, index1)]
            table2_unmatched_rows = [(row2, index2)]
            is_match_found = False
            while not is_match_found and (index1 < len(table1) or index2 < len(table2)):
                is_match_found, table1_unmatched_rows, table2_unmatched_rows, index1 = _search_for_next_match(
                    table1, index1, table1_unmatched_rows, table2_unmatched_rows, merge_condition_1, merge_condition_2
                )
                if is_match_found:
                    break
                is_match_found, table2_unmatched_rows, table1_unmatched_rows, index2 = _search_for_next_match(
                    table2, index2, table2_unmatched_rows, table1_unmatched_rows, merge_condition_2, merge_condition_1
                )
            index1 = table1_unmatched_rows[-1][1] + 1
            index2 = table2_unmatched_rows[-1][1] + 1
            # Print the unmatched block
            table1_unmatched_rows_data = [item[0] for item in table1_unmatched_rows]
            table2_unmatched_rows_data = [item[0] for item in table2_unmatched_rows]
            result = _print_unmatching_rows(result, table1_unmatched_rows_data, table2_unmatched_rows_data, table1_columns, table2_columns)
    # Print remaining rows
    # print(table1.iloc[index1:])
    # print(table2.iloc[index2:])
    result = _print_unmatching_rows(result, table1.iloc[index1:], table2.iloc[index2:], table1_columns, table2_columns)

    print(result)
