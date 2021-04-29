module load cudatoolkit/10.1

four_classes_mass_calc_pathology_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/four_classes_mass_calc_pathology'
four_classes_mass_calc_pathology_histeq_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/four_classes_mass_calc_pathology_histeq'

mass_shape_comb_feats_omit_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/mass_shape_comb_feats_omit'
mass_margins_comb_feats_omit_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/mass_margins_comb_feats_omit'
mass_breast_density_lesion_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/mass_breast_density_lesion'

calc_type_comb_feats_omit_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/calc_type_comb_feats_omit'
calc_dist_comb_feats_omit_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/calc_dist_comb_feats_omit'
calc_breast_density_lesion_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/calc_breast_density_lesion'

# with segmentation
mass_shape_comb_feats_omit_segm_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/mass_shape_comb_feats_omit_segm'
mass_margins_comb_feats_omit_segm_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/mass_margins_comb_feats_omit_segm'
mass_breast_density_lesion_segm_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/mass_breast_density_lesion_segm'

calc_type_comb_feats_omit_segm_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/calc_type_comb_feats_omit_segm'
calc_dist_comb_feats_omit_segm_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/calc_dist_comb_feats_omit_segm'
calc_breast_density_lesion_segm_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/calc_breast_density_lesion_segm'

# with mask
mass_shape_comb_feats_omit_mask_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/mass_shape_comb_feats_omit_mask'
mass_margins_comb_feats_omit_mask_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/mass_margins_comb_feats_omit_mask'
mass_breast_density_lesion_mask_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/mass_breast_density_lesion_mask'

calc_type_comb_feats_omit_mask_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/calc_type_comb_feats_omit_mask'
calc_dist_comb_feats_omit_mask_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/calc_dist_comb_feats_omit_mask'
calc_breast_density_lesion_mask_save_root='/home/hqvo2/Projects/Breast_Cancer/experiments/cbis_ddsm/calc_breast_density_lesion_mask'

mkdir -p ${four_classes_mass_calc_pathology_save_root}
mkdir -p ${four_classes_mass_calc_pathology_histeq_save_root}
mkdir -p ${mass_shape_comb_feats_omit_save_root}
mkdir -p ${mass_margins_comb_feats_omit_save_root}
mkdir -p ${mass_breast_density_lesion_save_root}
mkdir -p ${calc_type_comb_feats_omit_save_root}
mkdir -p ${calc_dist_comb_feats_omit_save_root}
mkdir -p ${calc_breast_density_lesion_save_root}
mkdir -p ${mass_shape_comb_feats_omit_segm_save_root}
mkdir -p ${mass_margins_comb_feats_omit_segm_save_root}
mkdir -p ${mass_breast_density_lesion_segm_save_root}
mkdir -p ${calc_type_comb_feats_omit_segm_save_root}
mkdir -p ${calc_dist_comb_feats_omit_segm_save_root}
mkdir -p ${calc_breast_density_lesion_segm_save_root}
mkdir -p ${mass_shape_comb_feats_omit_mask_save_root}
mkdir -p ${mass_margins_comb_feats_omit_mask_save_root}
mkdir -p ${mass_breast_density_lesion_mask_save_root}
mkdir -p ${calc_type_comb_feats_omit_mask_save_root}
mkdir -p ${calc_dist_comb_feats_omit_mask_save_root}
mkdir -p ${calc_breast_density_lesion_mask_save_root}

cd ..


# python train.py -d mass_shape_comb_feats_omit \
#        -m dilated_resnet50 \
#        --rnet_dil_2nd --rnet_dil_3rd --rnet_dil_4th\
#        -b 32 \
#        -e 100 -i 224 --opt adam --wc --ws \
#        -s ${mass_shape_comb_feats_omit_save_root}/dilated_r50_b32_e100_224x224_adam_wc_ws_"$(LC_TIME="EN.UTF-8" date)"

# python train.py -d mass_shape_comb_feats_omit \
#        -m dilated_resnet50 \
#        --rnet_dil_2nd --rnet_dil_3rd --rnet_dil_4th\
#        -b 32 \
#        -e 100 -i 256 --opt adam --wc --ws \
#        -s ${mass_shape_comb_feats_omit_save_root}/dilated_r50_b32_e100_256x256_adam_wc_ws_"$(LC_TIME="EN.UTF-8" date)"

# python train.py -d mass_shape_comb_feats_omit \
#        -m dilated_resnet50 \
#        --rnet_dil_2nd --rnet_dil_3rd --rnet_dil_4th\
#        -b 32 \
#        -e 100 -i 224 --opt adam --wc --ws \
#        --crt bce \
#        -s ${mass_shape_comb_feats_omit_save_root}/dilated_r50_b32_e100_224x224_adam_bce_wc_ws_"$(LC_TIME="EN.UTF-8" date)"

# python train.py -d mass_shape_comb_feats_omit \
#        -m dilated_resnet50 \
#        --rnet_dil_2nd --rnet_dil_3rd --rnet_dil_4th\
#        -b 32 \
#        -e 100 -i 224 --opt adam --wc --ws \
#        --aug_type albumentations \
#        -s ${mass_shape_comb_feats_omit_save_root}/dilated_r50_b32_e100_224x224_adam_wc_ws_aug-albumentations_"$(LC_TIME="EN.UTF-8" date)"

# python train.py -d mass_shape_comb_feats_omit \
#        -m dilated_resnet50 \
#        --rnet_dil_2nd --rnet_dil_3rd --rnet_dil_4th\
#        -b 32 \
#        -e 100 -i 224 --opt adam --wc --ws \
#        --crt bce \
#        --aug_type albumentations \
#        -s ${mass_shape_comb_feats_omit_save_root}/dilated_r50_b32_e100_224x224_adam_bce_wc_ws_aug-albumentations_"$(LC_TIME="EN.UTF-8" date)"

# python train.py -d mass_shape_comb_feats_omit \
#        -m dilated_resnet50 \
#        --rnet_dil_2nd --rnet_dil_3rd --rnet_dil_4th\
#        -b 32 \
#        -e 100 -i 256 --opt adam --wc --ws \
#        --crt bce \
#        --aug_type albumentations \
#        -s ${mass_shape_comb_feats_omit_save_root}/dilated_r50_b32_e100_256x256_adam_bce_wc_ws_aug-albumentations_"$(LC_TIME="EN.UTF-8" date)"

# python train.py -d mass_shape_comb_feats_omit \
#        -m dilated_resnet50 \
#        --rnet_dil_2nd --rnet_dil_3rd --rnet_dil_4th\
#        -b 32 \
#        -e 100 -i 256 --opt adam --wc --ws \
#        --crt bce \
#        -s ${mass_shape_comb_feats_omit_save_root}/dilated_r50_b32_e100_256x256_adam_bce_wc_ws_"$(LC_TIME="EN.UTF-8" date)"

# python train.py -d mass_margins_comb_feats_omit \
#        -m dilated_resnet50 \
#        --rnet_dil_2nd --rnet_dil_3rd --rnet_dil_4th\
#        -b 32 \
#        -e 100 -i 224 --opt adam --wc --ws \
#        --crt bce \
#        -s ${mass_margins_comb_feats_omit_save_root}/dilated_r50_b32_e100_224x224_adam_bce_wc_ws_"$(LC_TIME="EN.UTF-8" date)"

python train.py -d calc_type_comb_feats_omit \
       -m dilated_resnet50 \
       --rnet_dil_2nd --rnet_dil_3rd --rnet_dil_4th\
       -b 32 \
       -e 100 -i 224 --opt adam --wc --ws \
       --crt bce \
       -s ${calc_type_comb_feats_omit_save_root}/dilated_r50_b32_e100_224x224_adam_bce_wc_ws_"$(LC_TIME="EN.UTF-8" date)"

# python train.py -d calc_dist_comb_feats_omit \
#        -m dilated_resnet50 \
#        --rnet_dil_2nd --rnet_dil_3rd --rnet_dil_4th\
#        -b 32 \
#        -e 100 -i 224 --opt adam --wc --ws \
#        --crt bce \
#        -s ${calc_dist_comb_feats_omit_save_root}/dilated_r50_b32_e100_224x224_adam_bce_wc_ws_"$(LC_TIME="EN.UTF-8" date)"