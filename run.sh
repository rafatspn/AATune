#!/bin/bash

python3 /home/rafatspn/AATune/utils/get_best_subset_of_params.py -csv=performance_data/all_results_intel.csv -executable=3mm_kernel_p1 -o=best_3mm_kernel_p1_intel.json

python3 /home/rafatspn/AATune/seed/sd_pkr_agent.py -ir=/home/rafatspn/AATune/llvm-ir/3mm_kernel_p1.ll 