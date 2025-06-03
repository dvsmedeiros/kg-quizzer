# CÓDIGO UTILIZADO PARA CALCULAR AS MÉTRICAS DE TEXTO 

# -*- coding: utf-8 -*-
import text_metrics
import csv
import os
import tqdm

def get_metrics(text):

    raw = text.replace('{{quotes}}', '"')
    raw = raw.replace('{{exclamation}}', '!')
    raw = raw.replace('{{enter}}', '\n')
    raw = raw.replace('{{sharp}}', '#')
    raw = raw.replace('{{ampersand}}', '&')
    raw = raw.replace('{{percent}}', '%')
    raw = raw.replace('{{dollar}}', '$')

    raw = raw.encode("utf-8", "surrogateescape").decode("utf-8")
    t = text_metrics.Text(raw)
    metrics = text_metrics.final_metric_done.values_for_text(t).as_flat_dict()

    metrics_simple_word_ratio = f"{text_metrics.manual.SimpleWords().value_for_text(t):.3f}"

    metrics_used = ['brunet','ttr','yngve']

    result = '' 
    for f in metrics:
        if f not in metrics_used:
            continue

        # m = "%s:%s," % (f, metrics[f])
        m = "%s," % (metrics[f])
        result += m

    final_print = result + metrics_simple_word_ratio

    return final_print

def reformat_filename(original_filename):
    """
    Reformat filename from:
    {code}_{number}_{name}_{technique}_{format}_{model}_{more_info}.csv
    to:
    {name}_{technique}_{format}_{model}.csv
    
    Args:
        original_filename (str): Original filename to reformat
    
    Returns:
        str: Reformatted filename
    
    Example:
        >>> reformat_filename("5ad0e5d5_117_Computational_complexity_theory_few-shot_NA_NA_140_deepseek-r1:1.5b_0.7_0.95_40.csv")
        'Computational_complexity_theory_few-shot_NA_NA_140_deepseek-r1:1.5b.csv'
    """
    # Remove file extension if present
    if original_filename.endswith('.csv'):
        filename_without_ext = original_filename[:-4]
        extension = '.csv'
    else:
        filename_without_ext = original_filename
        extension = ''
    
    # Split by underscore
    parts = filename_without_ext.split('_')
    
    if len(parts) < 6:
        raise ValueError("Filename doesn't match expected format")
    
    # Remove first two parts (code and number)
    # Find the model part (contains colon or ends with version info)
    model_idx = -1
    for i in range(2, len(parts)):
        # Look for model indicators like colon or version patterns
        if ':' in parts[i] or any(char.isdigit() and '.' in parts[i] for char in parts[i]):
            model_idx = i
            break
    
    if model_idx == -1:
        # If no clear model found, assume it's the 6th element (index 5)
        model_idx = min(5, len(parts) - 1)
    
    # Extract name, technique, format, model (from index 2 to model_idx inclusive)
    new_parts = parts[2:model_idx + 1]
    
    # Join and add extension back
    return '_'.join(new_parts) + extension

# Define the folder path INSIDE THE CONTAINER
folder_path = '/opt/resultados/5ad0e5d5'

# Get a list of all files in the folder
files = os.listdir(folder_path)

files.sort(reverse=True)

# Remove files that don't end with ".csv"
files = [f for f in files if f.endswith('.csv')]
new_files_names = [reformat_filename(f) for f in files]

folder_path_output = '/opt/metrics/data' # This is the directory for output INSIDE the container

# Loop through all files

for idx, file in enumerate(tqdm.tqdm(files)):

    # Define the file path
    csv_file_path_input = os.path.join(folder_path, file)
    csv_file_path_output = os.path.join(folder_path_output, f"metrics_{new_files_names[idx]}")

    # Open and read the CSV file
    with open(csv_file_path_input, mode='r', newline='') as file:
        reader = csv.reader(file)

        # Write new data to a new csv file

        metrics_csv = [
            ['Question', 'Answer', 'Q_brunet', 'Q_ttr', 'Q_yngve', 'Q_simple_word_ratio', 'A_brunet', 'A_ttr', 'A_yngve', 'A_simple_word_ratio']
        ]

        for idx, row in enumerate(reader):

            if idx == 0:
                continue

            data = []

            try:
                input = row[0].split(';')
                question = input[0].replace('"', '')
                answer = input[1].replace('"', '')

                question_metrics = get_metrics(question).split(',')
                answer_metrics = get_metrics(answer).split(',')

                data.append(question)
                data.append(answer)

                for qm in question_metrics:
                    data.append(qm)

                for am in answer_metrics:
                    data.append(am)

                metrics_csv.append(data)

            except:
                continue

        with open(csv_file_path_output, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Write the data to the CSV
            writer.writerows(metrics_csv)