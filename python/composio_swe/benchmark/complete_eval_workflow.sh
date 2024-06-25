#!/bin/bash

set -ex

# Function to display usage instructions
show_usage() {
    echo "Usage: $0 <prediction_path_dir> <dataset_path_or_name>"
    echo "Example: $0 /path/to/prediction/dir /path/to/dataset/dir"
}
# Usage: ./complete_eval_workflow.sh <prediction_path_dir> <dataset_path_or_name>
if [ "$#" -ne 2 ]; then
    show_usage
    exit 1
fi

# Usage: ./complete_eval_workflow.sh <prediction_path_dir> <dataset_path_or_name>
prediction_path_dir=$1  #
dataset_path_or_name=$2
dataset_on_disk_path="$prediction_path_dir/dataset"
predictions_json_path="$prediction_path_dir/patches.json"
log_dir_path="$prediction_path_dir/logs"

# Generate related files
python ./setup_test_bed.py --prediction_path_dir "$prediction_path_dir" --dataset_path_or_name "$dataset_path_or_name"

# Save current directory and change to home directory
#pushd ~
## Clone the SWE-bench-docker repository
#git clone https://github.com/aorwall/SWE-bench-docker.git
#
## Navigate into the cloned directory
#cd SWE-bench-docker
#
## Run the evaluation
#python run_evaluation.py --predictions_path "{$predictions_json_path}" --log_dir "{$log_dir_path}" --swe_bench_tasks "{$dataset_on_disk_path}" --namespace aorwall
#popd

python ./get_score_card.py --log_dir "$log_dir_path" --prediction_path_dir "$prediction_path_dir" --swe_bench_path "$dataset_on_disk_path"


# Note: Replace <logs_dir_generated_by_run_evaluation> with the actual log directory path generated by the run_evaluation script.