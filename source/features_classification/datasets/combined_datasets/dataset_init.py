import os
import torch

from config.cfg_loader import proj_paths_json
# from features_classification.config_origin import options
from features_classification.augmentation.augmentation_funcs import torch_aug, albumentations_aug, augmix_aug


def initialize(options, data_transforms):
    if options.dataset in ['combined_datasets', 'aug_combined_datasets', 'image_lesion_combined_datasets']:
        from features_classification.datasets.combined_datasets.all_datasets import All_Pathology_Datasets as data

    # Get classes
    classes = data.classes

    # Load Dataset root
    data_root = proj_paths_json['DATA']['root']
    # CBIS-DDSM
    processed_cbis_ddsm_root = os.path.join(
        data_root, proj_paths_json['DATA']['processed_CBIS_DDSM'])

    ddsm_mass_data_dir = os.path.join(
        data_root, processed_cbis_ddsm_root,
        proj_paths_json['DATA']['CBIS_DDSM_lesions']['mass_feats']['mass_pathology'])
    ddsm_calc_data_dir = os.path.join(
        data_root, processed_cbis_ddsm_root,
        proj_paths_json['DATA']['CBIS_DDSM_lesions']['calc_feats']['calc_pathology'])
    ddsm_bg_data_dir = os.path.join(
        data_root, processed_cbis_ddsm_root,
        proj_paths_json['DATA']['CBIS_DDSM_lesions']['background']['bg_tfds'])

    # CBIS-DDSM aug
    ddsm_aug_mass_data_dir = os.path.join(
        data_root, processed_cbis_ddsm_root,
        proj_paths_json['DATA']['CBIS_DDSM_lesions']['mass_feats']['mass_pathology_tfds']
    )
    ddsm_aug_calc_data_dir = os.path.join(
        data_root, processed_cbis_ddsm_root,
        proj_paths_json['DATA']['CBIS_DDSM_lesions']['calc_feats']['calc_pathology_tfds'])

    # Inbreast
    inbreast_root = os.path.join(
        data_root, proj_paths_json['DATA']['INbreast']['root'])

    inbreast_mass_data_dir = os.path.join(inbreast_root, proj_paths_json['DATA']['INbreast']['mass_feats']['mass_pathology']) 
    inbreast_calc_data_dir = os.path.join(inbreast_root, proj_paths_json['DATA']['INbreast']['calc_feats']['calc_pathology'])
    inbreast_cluster_data_dir = os.path.join(inbreast_root, proj_paths_json['DATA']['INbreast']['cluster_feats']['cluster_pathology'])
    inbreast_distortion_data_dir = os.path.join(inbreast_root, proj_paths_json['DATA']['INbreast']['distortion_feats']['distortion_pathology'])
    inbreast_spiculated_data_dir = os.path.join(inbreast_root, proj_paths_json['DATA']['INbreast']['spiculated_feats']['spiculated_pathology'])
    inbreast_asymetry_data_dir = os.path.join(inbreast_root, proj_paths_json['DATA']['INbreast']['asymetry_feats']['asymetry_pathology'])
    inbreast_bg_data_dir = os.path.join(inbreast_root, proj_paths_json['DATA']['INbreast']['background']['bg_tfds'])

    # INbreast aug
    inbreast_aug_mass_data_dir = os.path.join(inbreast_root, proj_paths_json['DATA']['INbreast']['mass_feats']['aug_mass_pathology']) 
    inbreast_aug_calc_data_dir = os.path.join(inbreast_root, proj_paths_json['DATA']['INbreast']['calc_feats']['aug_calc_pathology'])
    inbreast_aug_cluster_data_dir = os.path.join(inbreast_root, proj_paths_json['DATA']['INbreast']['cluster_feats']['aug_cluster_pathology'])
    inbreast_aug_distortion_data_dir = os.path.join(inbreast_root, proj_paths_json['DATA']['INbreast']['distortion_feats']['aug_distortion_pathology'])
    inbreast_aug_spiculated_data_dir = os.path.join(inbreast_root, proj_paths_json['DATA']['INbreast']['spiculated_feats']['aug_spiculated_pathology'])
    inbreast_aug_asymetry_data_dir = os.path.join(inbreast_root, proj_paths_json['DATA']['INbreast']['asymetry_feats']['aug_asymetry_pathology'])

    # BCDR
    bcdr_root = os.path.join(
        data_root, proj_paths_json['DATA']['BCDR']['root'])
    bcdr_film_data_dir = os.path.join(bcdr_root, proj_paths_json['DATA']['BCDR']['film']['root'])
    bcdr_digital_data_dir = os.path.join(bcdr_root, proj_paths_json['DATA']['BCDR']['digital']['root'])
    bcdr_data_type = 'pathology'
    # BCDR aug
    aug_bcdr_data_type = 'aug_pathology'

    # BCDR aug


    # CSAWS
    csaws_root = os.path.join(
        data_root, proj_paths_json['DATA']['CSAW-S']['root'])

    csaws_cancer_data_dir = os.path.join(csaws_root, proj_paths_json['DATA']['CSAW-S']['cancer'])
    csaws_calc_data_dir = os.path.join(csaws_root, proj_paths_json['DATA']['CSAW-S']['calcifications'])
    csaws_axillary_data_dir = os.path.join(csaws_root, proj_paths_json['DATA']['CSAW-S']['axillary_lymph_nodes'])
    csaws_bg_data_dir = os.path.join(csaws_root, proj_paths_json['DATA']['CSAW-S']['background']['bg_tfds'])

    # CSAWS aug
    csaws_aug_cancer_data_dir = os.path.join(csaws_root, proj_paths_json['DATA']['CSAW-S']['aug_cancer'])
    csaws_aug_calc_data_dir = os.path.join(csaws_root, proj_paths_json['DATA']['CSAW-S']['aug_calcifications'])
    csaws_aug_axillary_data_dir = os.path.join(csaws_root, proj_paths_json['DATA']['CSAW-S']['aug_axillary_lymph_nodes'])

    # CSAWM
    csawm_root = os.path.join(
        data_root, proj_paths_json['DATA']['CSAW-M']['root']
    )
    csawm_bg_data_dir = os.path.join(csawm_root, proj_paths_json['DATA']['CSAW-M']['background']['bg_tfds'])

    # CMMD
    cmmd_root = os.path.join(
        data_root, proj_paths_json['DATA']['CMMD']['root']
    )
    cmmd_bg_data_dir = os.path.join(cmmd_root, proj_paths_json['DATA']['CMMD']['background']['bg_tfds'])

    # Create dataset
    if options.dataset in ['combined_datasets']:
        image_datasets = {'train': data(os.path.join(ddsm_mass_data_dir, 'train'),
                                        os.path.join(ddsm_calc_data_dir, 'train'),
                                        os.path.join(ddsm_bg_data_dir, 'train'),
                                        inbreast_mass_data_dir, inbreast_calc_data_dir,
                                        inbreast_spiculated_data_dir,
                                        inbreast_asymetry_data_dir,
                                        inbreast_distortion_data_dir,
                                        inbreast_cluster_data_dir,
                                        inbreast_bg_data_dir,

                                        bcdr_film_data_dir, bcdr_digital_data_dir,
                                        bcdr_data_type,

                                        csaws_cancer_data_dir,
                                        csaws_calc_data_dir,
                                        csaws_axillary_data_dir,
                                        csaws_bg_data_dir,

                                        transform=data_transforms['train'])}
    elif options.dataset in ['aug_combined_datasets']:
        image_datasets = {'train': data(os.path.join(ddsm_aug_mass_data_dir, 'train'),
                                        os.path.join(ddsm_aug_calc_data_dir, 'train'),
                                        os.path.join(ddsm_bg_data_dir, 'train'),
                                        inbreast_aug_mass_data_dir, inbreast_aug_calc_data_dir,
                                        inbreast_aug_spiculated_data_dir,
                                        inbreast_aug_asymetry_data_dir,
                                        inbreast_aug_distortion_data_dir,
                                        inbreast_aug_cluster_data_dir,
                                        inbreast_bg_data_dir,

                                        bcdr_film_data_dir, bcdr_digital_data_dir,
                                        aug_bcdr_data_type,

                                        csaws_aug_cancer_data_dir,
                                        csaws_aug_calc_data_dir,
                                        csaws_aug_axillary_data_dir,
                                        csaws_bg_data_dir,

                                        transform=data_transforms['train'])}
        
    elif options.dataset in ['image_lesion_combined_datasets']:
        image_datasets = {'train': data(os.path.join(ddsm_mass_data_dir, 'train'),
                                        os.path.join(ddsm_calc_data_dir, 'train'),
                                        os.path.join(ddsm_bg_data_dir, 'train'),
                                        inbreast_mass_data_dir, inbreast_calc_data_dir,
                                        inbreast_spiculated_data_dir,
                                        inbreast_asymetry_data_dir,
                                        inbreast_distortion_data_dir,
                                        inbreast_cluster_data_dir,
                                        inbreast_bg_data_dir,

                                        bcdr_film_data_dir, bcdr_digital_data_dir,
                                        bcdr_data_type,

                                        csaws_cancer_data_dir,
                                        csaws_calc_data_dir,
                                        csaws_axillary_data_dir,
                                        csaws_bg_data_dir,

                                        os.path.join(csawm_bg_data_dir, 'train'),
                                        cmmd_bg_data_dir,

                                        transform=data_transforms['train'],
                                        use_bcdr_dn01=True
                                        )}

    return data, image_datasets, classes

    
    
if __name__ == '__main__':
    input_size = 224
    data_transforms = torch_aug(input_size)
    data, image_datasets, classes = initialize(options, data_transforms)
    print(classes)

    dataloader = torch.utils.data.DataLoader(image_datasets['train'], batch_size=1)

    freq_dict = dict()
    for sample in dataloader:
        freq_dict[classes[sample['label']]] = freq_dict.get(classes[sample['label']], 0) + 1

    for key, value in freq_dict.items():
        print(key, value)
