cd ..
export CUDA_VISIBLE_DEVICES=0,1,2,3

python run.py \
       --exp_name pathology_birads34_4class_mae \
       -d four_classes_mass_calc_pathology_birads34 \
       --one_stage_training \
       --njobs 5 \
       -m 'mae_vit_base_patch16'\
       --ckpt '/home/hqvo2/Projects/Breast_Cancer/libs/mae/jobdir/vit_base_patch16_e500_input224_five_classes_mass_calc_pathology/checkpoint-499.pth' \
       -b 32 \
       -e 100 -i 224 --opt adam --wc --ws --crt ce\
       --use_lr_scheduler \
       --first_stage_freeze -1 \
       --first_stage_lr 0.00001 \
       --best_ckpt_metric macro_auc

python run.py \
       --exp_name pathology_birads34_4class_mae \
       -d four_classes_mass_calc_pathology_birads34 \
       --one_stage_training \
       --njobs 5 \
       -m 'mae_vit_base_patch16'\
       --ckpt '/home/hqvo2/Projects/Breast_Cancer/libs/mae/jobdir/vit_base_patch16_e500_input224_combined_datasets/checkpoint-499.pth' \
       -b 32 \
       -e 100 -i 224 --opt adam --wc --ws --crt ce\
       --use_lr_scheduler \
       --first_stage_freeze -1 \
       --first_stage_lr 0.00001 \
       --best_ckpt_metric macro_auc

python run.py \
       --exp_name pathology_birads34_4class_mae \
       -d four_classes_mass_calc_pathology_birads34 \
       --one_stage_training \
       --njobs 5 \
       -m 'mae_vit_base_patch16'\
       --ckpt '/home/hqvo2/Projects/Breast_Cancer/libs/mae/jobdir/vit_base_patch16_e500_input224_image_lesion_combined_datasets/checkpoint-499.pth' \
       -b 32 \
       -e 100 -i 224 --opt adam --wc --ws --crt ce\
       --use_lr_scheduler \
       --first_stage_freeze -1 \
       --first_stage_lr 0.00001 \
       --best_ckpt_metric macro_auc

