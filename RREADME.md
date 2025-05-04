AATune

/lus/grand/projects/EE-ECP/araf/llms/mistral

qsub -l walltime=1:00:00 -l select=1:system=polaris -l filesystems=home -A EE-ECP -q debug -N debug -I

module use /soft/modulefiles ; module load conda; conda activate base

omp_threads = 4, 8, 16, 24, 32, 40, 48
omp_proc_bing = true, false, close, spread
omp_schedule = static, dynamic, guided
