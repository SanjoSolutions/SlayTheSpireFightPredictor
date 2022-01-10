import tensorflow as tf
import sys
from random import random
from tensorflow.data.experimental import TFRecordWriter
import os

test_dataset_percentage = 0.2
train_dataset_percentage = 1.0 - test_dataset_percentage

def main():
    input_path = sys.argv[1]

    dataset = tf.data.TFRecordDataset(filenames=[input_path])

    write_dataset_with_percentage_of_data(dataset, test_dataset_percentage, input_path, '_test')
    write_dataset_with_percentage_of_data(dataset, train_dataset_percentage, input_path, '_train')


def write_dataset_with_percentage_of_data(dataset, percentage, input_path, save_suffix):
    output_dataset = dataset.filter(create_goes_into_dataset(percentage))
    output_path = generate_file_path(input_path, save_suffix)
    write_dataset(output_dataset, output_path)


def generate_file_path(base_file_path, suffix):
    path, extension = os.path.splitext(base_file_path)
    file_path = path + suffix + extension
    return file_path


def write_dataset(dataset, file_path):
    tf.data.experimental.save(dataset, file_path)


def create_goes_into_dataset(threshold):
    return lambda x: goes_into_dataset(threshold)


def goes_into_dataset(threshold):
    return random() <= threshold


if __name__ == '__main__':
    main()
