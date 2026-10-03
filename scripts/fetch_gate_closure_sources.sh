#!/bin/sh
# Public primary-source snapshots. Existing files are small evidence, not signals.
set -eu
cd "$(dirname "$0")/.."
dest=docs/research/dataset_exploration/evidence
fetch() { curl -LsS --fail --max-time 25 "$2" -o "$dest/$1"; }
fetch gate_closure_upstream_main.json https://api.github.com/repos/madjens/bbbd-dataset/commits/main
fetch gate_closure_osf_analysis_root.json https://api.osf.io/v2/nodes/d4k3q/files/osfstorage/
fetch gate_closure_osf_d4k3q_code.json 'https://api.osf.io/v2/nodes/d4k3q/files/osfstorage/61e1f56d466d15030bd5772e/'
fetch gate_closure_osf_d4k3q_data.json 'https://api.osf.io/v2/nodes/d4k3q/files/osfstorage/61e1f57353349e03345f9c81/'
fetch gate_closure_osf_d4k3q_helpers.json 'https://api.osf.io/v2/nodes/d4k3q/files/osfstorage/61e1f5ca95a0300340ed23d9/?page%5Bsize%5D=100'
fetch gate_closure_osf_d4k3q_routines.json 'https://api.osf.io/v2/nodes/d4k3q/files/osfstorage/61e1f5dc95a0300340ed241b/?page%5Bsize%5D=100'
fetch gate_closure_osf_m7gj4_root.json https://api.osf.io/v2/nodes/m7gj4/files/
fetch gate_closure_osf_m7gj4_files.json 'https://api.osf.io/v2/nodes/m7gj4/files/osfstorage/?page%5Bsize%5D=100'
fetch gate_closure_osf_m7gj4_data.json 'https://api.osf.io/v2/nodes/m7gj4/files/osfstorage/5fda7c520694b7048df3636b/?page%5Bsize%5D=100'
fetch gate_closure_osf_m7gj4_code.json 'https://api.osf.io/v2/nodes/m7gj4/files/osfstorage/5fda7c4b149e750435028ba7/?page%5Bsize%5D=100'
fetch gate_closure_osf_m7gj4_exp1.json 'https://api.osf.io/v2/nodes/m7gj4/files/osfstorage/5fda7cf8149e75043c02761f/?page%5Bsize%5D=100'
fetch gate_closure_osf_m7gj4_exp2.json 'https://api.osf.io/v2/nodes/m7gj4/files/osfstorage/5fda7cfe149e75043b0275ce/?page%5Bsize%5D=100'
fetch gate_closure_osf_m7gj4_helpers.json 'https://api.osf.io/v2/nodes/m7gj4/files/osfstorage/5fda7c70f0df54044b2ef52a/?page%5Bsize%5D=100'
fetch gate_closure_Education_questions.xlsx https://osf.io/download/fjxaq/
fetch gate_closure_P01_Experiment_2_Points.mat https://osf.io/download/6prma/
fetch gate_closure_P01_Experiment_2_questionnaire.mat https://osf.io/download/5fda7edc0694b7048ef36b8a/
fetch gate_closure_P01_figure_1.m https://osf.io/download/txcpd/
fetch gate_closure_P01_figure_2.m https://osf.io/download/njgvd/
fetch gate_closure_P01_Experiment_2_demographics.mat https://osf.io/download/5fda7ed6149e75043b0279dc/
fetch gate_closure_P01_Experiment_2_stimuli_order.mat https://osf.io/download/5fda7edd0694b70491f36170/
fetch gate_closure_p03_preprocessEEGdata.m https://osf.io/download/h6a7w/
fetch gate_closure_official_experiments.html https://bbbd.pythonanywhere.com/experiments-page
fetch gate_closure_official_experiments.js https://bbbd.pythonanywhere.com/static/experiments_script.js
fetch gate_closure_official_stars_quiz.tsv https://bbbd.pythonanywhere.com/static/questionnaires/stars_quiz.tsv
# Follow with bundled-Python workbook extraction and gate_closure.sources().
# The latter refuses changed OSF bytes against the retained official hashes.
