#!/bin/bash
# Start Strata on .5 (V100):
#  - STRATA_EXPERIMENTAL_SM60=1: the upstream experimental Pascal/Volta build (needs CUDA 12.x)
#  - STRATA_PROMPT_ATTN_OLD=1:   skip qsa_prompt_attn_batch, whose sm_70 guard bug traps the GPU
#                                (upstream issue #371; on sm_70 the MMA path can never run anyway)
export STRATA_EXPERIMENTAL_SM60=1
export STRATA_PROMPT_ATTN_OLD=1
cd /home/eamon/Strata || exit 1
exec ./setup.sh "$@"
