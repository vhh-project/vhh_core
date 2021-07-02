import os.path
import csv
import json

def make_filepath_unique(input_path_filename, file_extension):
    """
    This method generates a unique filepath by increasing numbers to it

    :param path_filename: The filepath and filename, for example '/data/share/USERANME/results'
    :param file_extension: The extension of the file, for example '.csv'
    :return: A unique file name, for example '/data/share/USERANME/results_2.csv'
    """
    if not os.path.exists(input_path_filename + file_extension):
        return input_path_filename + file_extension
    
    number = 2
    file_path = input_path_filename + "_" + str(number) + file_extension
    while(os.path.exists(file_path)):
        number += 1
        file_path = input_path_filename + "_" + str(number) + file_extension
    return file_path

def store_csv(filepath, data):
    """
    Stores data in a csv file.

    :param filepath: The path of the filename in which you want to store the data, for example '/data/share/USERNAME/results/data.csv'
    param data: The data as a list of dictionaries (all dictionaries should have the same keys), for example '[{'id':1, 'name':'One'}, {'id':2, 'name':'Two'}}]

    """
    keys = data[0].keys()
    with open(filepath, 'w', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def store_json(filepath, data):
    """
    Stores data in a json file.

    :param filepath: The path of the filename in which you want to store the data, for example '/data/share/USERNAME/results/data.json'
    param data: The data as a list of dictionaries (all dictionaries should have the same keys), for example '[{'id':1, 'name':'One'}, {'id':2, 'name':'Two'}]'

    """
    with open(filepath, 'w') as output_file:
        json.dump(data , output_file)