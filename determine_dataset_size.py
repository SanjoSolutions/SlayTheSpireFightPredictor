import sys
from tensorflow.data import TFRecordDataset


def main():
    input_path = sys.argv[1]

    dataset = TFRecordDataset(filenames=[input_path])
    size = dataset.reduce(0, lambda size, _: size + 1).numpy()
    print(size)


if __name__ == '__main__':
    main()
