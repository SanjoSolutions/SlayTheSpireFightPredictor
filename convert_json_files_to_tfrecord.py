import sys
from multiprocessing import Process, Pool
import json
import os
import tensorflow as tf
from tensorflow.train import Example, Features, Feature, BytesList, Int64List
from pathlib import Path
from math import floor


def main():
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    input_paths = gather_file_paths(input_path)

    total_number_of_files = float(len(input_paths))
    number_of_files_processed = 0
    last_reported_percentage_of_files_processed = 0

    Path(output_path).unlink(missing_ok=True)

    with tf.io.TFRecordWriter(output_path) as file_writer:
        with Pool(8) as pool:
            for examples in pool.imap_unordered(process, input_paths, chunksize=1):
                for example in examples:
                    file_writer.write(example)

                number_of_files_processed += 1
                percentage_of_files_processed = number_of_files_processed / total_number_of_files
                if percentage_of_files_processed - last_reported_percentage_of_files_processed >= 0.10:
                    print(str(floor(percentage_of_files_processed * 100)) + '% of files processed.')
                    last_reported_percentage_of_files_processed = percentage_of_files_processed


def gather_file_paths(folder_path):
    file_paths = []
    for root_path, _, file_names in os.walk(folder_path):
        for file_name in file_names:
            file_path = os.path.join(root_path, file_name)
            file_paths.append(file_path)
    return file_paths


def process(input_path):
    examples = []
    with open(input_path, 'r', encoding='utf8') as file:
        entries = json.load(file)
        for entry in entries:
            record_bytes = Example(features=Features(feature={
                'cards': Feature(bytes_list=BytesList(value=to_byte_strings(entry['cards']))),
                'relics': Feature(bytes_list=BytesList(value=to_byte_strings(entry['relics']))),
                'max_hp': Feature(int64_list=Int64List(value=[entry['max_hp']])),
                'entering_hp': Feature(int64_list=Int64List(value=[entry['entering_hp']])),
                'character': Feature(bytes_list=BytesList(value=[to_byte_string(entry['character'])])),
                'ascension': Feature(int64_list=Int64List(value=[entry['ascension']])),
                'enemies': Feature(bytes_list=BytesList(value=[to_byte_string(entry['enemies'])])),
                'potion_used': Feature(int64_list=Int64List(value=[entry['potion_used']])),
                'floor': Feature(int64_list=Int64List(value=[entry['floor']])),
                'damage_taken': Feature(int64_list=Int64List(value=[entry['damage_taken']])),
            })).SerializeToString()
            examples.append(record_bytes)
    return examples


def to_byte_strings(strings):
    return list(map(to_byte_string, strings))


def to_byte_string(string):
    return string.encode('utf-8')


if __name__ == '__main__':
    main()
