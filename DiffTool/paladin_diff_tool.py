import pandas as pd
import ast
import builtins
import json
from types import FunctionType

from PaladinEngine.archive.archive import Archive
from PaladinUI.paladin_server.paladin_server import PaladinServer

TIMES_COLUMN_NAME = 'Time Range'
GREEN_COLOR = '#B7F9A2'
RED_COLOR = '#FAA085'


# ---------------------------------------------------------------------------------------------#
# ------------------------- CLASSES -----------------------------------------------------------#
# ---------------------------------------------------------------------------------------------#


class TableInfo:
    def __init__(self, csv_file_path, suffix):
        self.csv_file_path = csv_file_path
        self.suffix = suffix


class MergeTableInstance:
    def __init__(self, table, table_info, merge_condition, result_condition):
        self.table = table
        self.table_info = table_info
        self.merge_condition = merge_condition
        self.result_condition = result_condition
        self.columns = self.table.columns.values.tolist()

    def add_suffix_to_conditions(self):
        self.merge_condition = [item + self.table_info.suffix for item in self.merge_condition]
        self.result_condition = [item + self.table_info.suffix for item in self.result_condition]


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

    special_types = {'list': list, 'dict': dict, 'tuple': tuple, 'set': set}
    if record_key.stub_name == "__AS__" and row.rtype in special_types.keys():
        value_of_record = ast.literal_eval(row.value)
        type_of_record = row.rtype
    elif row.rtype == 'function':
        value_of_record = row.value
        type_of_record = FunctionType
    elif row.rtype == 'bool':
        value_of_record = True if row.value == 'True' else False
        type_of_record = bool
    elif row.rtype in special_types.keys():
        value_of_record = ast.literal_eval(row.value)
        type_of_record = special_types[row.rtype]
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
    result = query_result['result']['query']
    if result == '""':
        raise Exception("Empty query result!")
    json_data = json.loads(result)
    json_data.pop('keys')
    result_df = pd.DataFrame.from_dict(json_data, orient="index")
    result_df.reset_index(inplace=True)
    result_df = result_df.rename(columns={'index': TIMES_COLUMN_NAME})
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


def _are_matching_rows(merge_table_instance_1, merge_table_instance_2, row1, row2):
    row1 = row1.reset_index(drop=True)
    row2 = row2.reset_index(drop=True)

    sub_row1 = row1[merge_table_instance_1.merge_condition]
    sub_row2 = row2[merge_table_instance_2.merge_condition]
    sub_row1.columns = [i for i in range(sub_row1.shape[1])]
    sub_row2.columns = [i for i in range(sub_row2.shape[1])]
    body_condition = sub_row1.equals(sub_row2)

    sub_result_row1 = row1[merge_table_instance_1.result_condition]
    sub_result_row2 = row2[merge_table_instance_2.result_condition]
    sub_result_row1.columns = [i for i in range(sub_result_row1.shape[1])]
    sub_result_row2.columns = [i for i in range(sub_result_row2.shape[1])]
    result_condition = sub_result_row1.notna().values.all() and \
                       sub_result_row2.notna().values.all() and \
                       sub_result_row1.equals(sub_result_row2)

    return body_condition or result_condition


def _collect_unmatching_rows(merge_table_instance_1, merge_table_instance_2, row1, row2, index1, index2):
    table1_unmatched_rows = [(row1, index1)]
    table2_unmatched_rows = [(row2, index2)]
    is_match_found = False
    while not is_match_found and (index1 < len(merge_table_instance_1.table) or index2 < len(merge_table_instance_2.table)):
        is_match_found, table1_unmatched_rows, table2_unmatched_rows, index1 = _search_for_next_match(
            merge_table_instance_1, merge_table_instance_2,
            index1, table1_unmatched_rows, table2_unmatched_rows
        )
        if is_match_found:
            break
        is_match_found, table2_unmatched_rows, table1_unmatched_rows, index2 = _search_for_next_match(
            merge_table_instance_2, merge_table_instance_1,
            index2, table2_unmatched_rows, table1_unmatched_rows
        )
    index1 = table1_unmatched_rows[-1][1]
    index2 = table2_unmatched_rows[-1][1]
    if is_match_found:
        # Exclude the found row from each list, so it isn't added as part of the unmatched block
        table1_unmatched_rows = table1_unmatched_rows[:-1]
        table2_unmatched_rows = table2_unmatched_rows[:-1]
    return index1, index2, table1_unmatched_rows, table2_unmatched_rows


def _search_for_next_match(merge_table_instance_a, merge_table_instance_b, index_a, table_a_unmatched_rows, table_b_unmatched_rows):
    index_a += 1

    if index_a >= len(merge_table_instance_a.table):
        return False, table_a_unmatched_rows, table_b_unmatched_rows, index_a

    row_a = merge_table_instance_a.table.iloc[[index_a]]
    table_a_unmatched_rows.append((row_a, index_a))
    is_match_found = False
    for i, (row2_unmatched, index2_unmatched) in enumerate(table_b_unmatched_rows):
        if _are_matching_rows(merge_table_instance_a, merge_table_instance_b, row_a, row2_unmatched):
            is_match_found = True
            table_b_unmatched_rows = table_b_unmatched_rows[:i + 1]
            break
    return is_match_found, table_a_unmatched_rows, table_b_unmatched_rows, index_a


def _dataframe_from_rows(rows, table1_columns):
    df = pd.DataFrame(columns=table1_columns)
    for row in rows:
        df = pd.concat([df, row])
    df = df.reset_index(drop=True)
    return df


def _add_matching_rows_to_result(result, row1, row2):
    row1 = row1.reset_index(drop=True)
    row2 = row2.reset_index(drop=True)
    merged_row = pd.concat([row1, row2], axis=1)
    result = pd.concat([result, merged_row], ignore_index=True)
    match_indices = result.tail(len(merged_row)).index.tolist()
    return result, match_indices


def _add_unmatching_rows_to_result(result, rows1, rows2):
    merged_block = pd.concat([rows1, rows2], axis=1)
    result = pd.concat([result, merged_block], ignore_index=True)
    diff_indices = result.tail(len(merged_block)).index.tolist()
    return result, diff_indices


# ---------------------------------------------------------------------------------------------#
# ------------------------- INTERACTIVE FUNCTIONS ---------------------------------------------#
# ---------------------------------------------------------------------------------------------#


def get_data(table_info, query_vars, start_time=0, end_time=500):
    query = f"Union({','.join(query_vars)})"
    dataframe = _create_dataframe_from_csv(table_info.csv_file_path, query, start_time, end_time)
    columns = [TIMES_COLUMN_NAME] + query_vars
    dataframe = dataframe[columns]
    dataframe = dataframe.add_suffix(table_info.suffix)
    return dataframe


def merge_tables(table_info_1, table_info_2, table1, table2, merge_condition_1, merge_condition_2, result_condition_1, result_condition_2):
    merge_table_instance_1 = MergeTableInstance(table1, table_info_1, merge_condition_1, result_condition_1)
    merge_table_instance_2 = MergeTableInstance(table2, table_info_2, merge_condition_2, result_condition_2)

    all_columns = merge_table_instance_1.columns + merge_table_instance_2.columns
    result = pd.DataFrame(columns=all_columns)
    merge_table_instance_1.add_suffix_to_conditions()
    merge_table_instance_2.add_suffix_to_conditions()

    match_indices = []
    diff_indices = []
    index1 = 0
    index2 = 0
    while index1 < len(table1) and index2 < len(table2):
        row1 = table1.iloc[[index1]]
        row2 = table2.iloc[[index2]]
        if _are_matching_rows(merge_table_instance_1, merge_table_instance_2, row1, row2):
            result, indices = _add_matching_rows_to_result(result, row1, row2)
            match_indices += indices
            index1 += 1
            index2 += 1
        else:
            index1, index2, table1_unmatched_rows, table2_unmatched_rows = _collect_unmatching_rows(
                merge_table_instance_1, merge_table_instance_2, row1, row2, index1, index2
            )
            # Add the unmatching block to result
            table1_unmatched_rows_df = _dataframe_from_rows([item[0] for item in table1_unmatched_rows], merge_table_instance_1.columns)
            table2_unmatched_rows_df = _dataframe_from_rows([item[0] for item in table2_unmatched_rows], merge_table_instance_2.columns)
            result, indices = _add_unmatching_rows_to_result(result, table1_unmatched_rows_df, table2_unmatched_rows_df)
            diff_indices += indices

    return result, match_indices, diff_indices
