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


def _print_matching_rows(row1, row2):
    merge_row = pd.concat([row1, row2])
    print(merge_row)


def _print_unmatching_rows(rows1, rows2):
    pass #TODO: IMPLEMENT


# ---------------------------------------------------------------------------------------------#
# ------------------------- INTERACTIVE FUNCTIONS ---------------------------------------------#
# ---------------------------------------------------------------------------------------------#


def get_data(csv_file_path, query, suffix, start_time=0, end_time=500):
    dataframe = _create_dataframe_from_csv(csv_file_path, query, start_time, end_time)
    dataframe = dataframe.add_suffix(suffix)
    return dataframe


def merge_tables(table1, table2, merge_condition_1, merge_condition_2, suffix1, suffix2):
    merge_condition_1 = [item + suffix1 for item in merge_condition_1]
    merge_condition_2 = [item + suffix2 for item in merge_condition_2]

    index1 = 0
    index2 = 0
    while index1 < len(table1) and index2 < len(table2):
        row1 = table1.iloc[[index1]]
        row2 = table2.iloc[[index2]]
        if _are_matching_rows(row1, row2, merge_condition_1, merge_condition_2):
            _print_matching_rows(row1, row2)
            index1 += 1
            index2 += 1
        else:
            table1_unmatched_rows = [(row1, index1)]
            table2_unmatched_rows = [(row2, index2)]
            is_match_found = False
            while not is_match_found:
                index1 += 1
                row1 = table1.iloc[[index1]]
                for row2_unmatched, index2_unmatched in table2_unmatched_rows:
                    if _are_matching_rows(row1, row2_unmatched, merge_condition_1, merge_condition_2):
                        is_match_found = True
                        index1 += 1
                        index2 = index2_unmatched + 1
                        _print_unmatching_rows(table1_unmatched_rows, table2_unmatched_rows) #TODO: table2 from index 0 to index2_unmatched; pass only rows without indices
                        break
                if is_match_found:
                    break
                table1_unmatched_rows.append((row1, index1))

                index2 += 1
                row2 = table2.iloc[[index2]]
                for row1_unmatched, index1_unmatched in table1_unmatched_rows:
                    if _are_matching_rows(row2, row1_unmatched, merge_condition_2, merge_condition_1):
                        is_match_found = True
                        index2 += 1
                        index1 = index1_unmatched + 1
                        _print_unmatching_rows(table2_unmatched_rows, table1_unmatched_rows) #TODO: table1 from index 0 to index1_unmatched; pass only rows without indices

                if is_match_found:
                    break
                table2_unmatched_rows.append((row2, index2))

            #TODO: inside for loop whem match is found - update the unmatched_rows lists to contain only relevant items,
            #TODO: and then here take the last index +1 and update index1, index2 and also print from here
