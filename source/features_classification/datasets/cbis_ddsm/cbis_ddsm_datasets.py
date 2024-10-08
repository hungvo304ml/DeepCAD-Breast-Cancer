import os
import glob
import pandas as pd
import torch
import numpy as np
import math
import random
import cv2
import albumentations

from torch.utils.data import Dataset
from PIL import Image
from sklearn.preprocessing import label_binarize
from natsort import natsorted

from features_classification.train.train_utils import compute_classes_weights
from features_classification.train.train_utils import compute_classes_weights_mass_calc
from features_classification.train.train_utils import compute_classes_weights_mass_calc_pathology_4class
from features_classification.train.train_utils import compute_classes_weights_mass_calc_pathology_5class


def get_info_lesion(df, ROI_ID):
    _, _, patient_id, left_or_right, image_view, abnormality_id = ROI_ID.split(
        '_')

    rslt_df = df[(df['patient_id'] == ('P_' + patient_id)) &
                 (df['left or right breast'] == left_or_right) &
                 (df['image view'] == image_view) &
                 (df['abnormality id'] == int(abnormality_id))]

    return rslt_df


class Mass_Shape_Dataset(Dataset):
    classes = np.array(['ROUND', 'OVAL', 'IRREGULAR',
                        'LOBULATED', 'ARCHITECTURAL_DISTORTION',
                        'ASYMMETRIC_BREAST_TISSUE', 'LYMPH_NODE',
                        'FOCAL_ASYMMETRIC_DENSITY'])
                              
    combined_classes = np.array(['IRREGULAR-ARCHITECTURAL_DISTORTION',
                                 'IRREGULAR-ASYMMETRIC_BREAST_TISSUE',
                                 'IRREGULAR-FOCAL_ASYMMETRIC_DENSITY',
                                 'LOBULATED-ARCHITECTURAL_DISTORTION',
                                 'LOBULATED-IRREGULAR',
                                 'LOBULATED-LYMPH_NODE',
                                 'LOBULATED-OVAL',
                                 'OVAL-LOBULATED',
                                 'OVAL-LYMPH_NODE',
                                 'ROUND-IRREGULAR-ARCHITECTURAL_DISTORTION',
                                 'ROUND-LOBULATED',
                                 'ROUND-OVAL'])

    @staticmethod
    def convert_label_to_multilabel(class_name):
        '''Convert class name to zero-one vector'''
        multilabel = np.zeros(Mass_Shape_Dataset.classes.shape)
        for label in class_name.split('-'):
            multilabel += (Mass_Shape_Dataset.classes == label).astype(float)
        return multilabel

    @staticmethod
    def convert_multilabel_to_label(multilabel):
        '''Convert zero-one vector to class name'''
        labels_idx = np.where(multilabel == 1)

        labels_set = set()

        for label_idx in labels_idx[0]:
            labels_set.add(Mass_Shape_Dataset.classes[label_idx])

        all_classes = np.concatenate((Mass_Shape_Dataset.classes,
                                      Mass_Shape_Dataset.combined_classes))
        for _class in all_classes:
            _class_set = set()

            for single_class in _class.split('-'):
                _class_set.add(single_class)

            if labels_set == _class_set:
                return _class

        # for predicted combined class that does not exist in our dataset
        new_combined_class = '-'.join(natsorted(list(labels_set)))
        return new_combined_class


    def __init__(self, root_dir, transform=None, train_rate=1):
        self.root_dir = root_dir
        self.transform = transform
        self.train_rate = train_rate

        self.images_list = []
        self.labels = []

        self.all_classes = np.concatenate((Mass_Shape_Dataset.classes,
                                           Mass_Shape_Dataset.combined_classes))

        for idx, mass_shape in enumerate(self.all_classes):
            images = glob.glob(os.path.join(root_dir, mass_shape, '*.png'))

            # For training using part of data
            images_len = len(images)
            images = images[:int(images_len*self.train_rate)]

            self.images_list += images
            self.labels += [idx] * len(images)


    def get_classes_weights(self):
        classes_weights = compute_classes_weights(
            data_root=self.root_dir,
            classes_names=Mass_Shape_Dataset.classes,
            combined_classes_names=Mass_Shape_Dataset.combined_classes
        )
        return classes_weights

    def __len__(self):
        return len(self.images_list)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_path = self.images_list[idx]
        img_name, _ = os.path.splitext(os.path.basename(img_path))
        image = Image.open(img_path)

        if image.mode == 'L':
            image = image.convert("RGB")

        label = self.labels[idx]
        binarized_multilabel = Mass_Shape_Dataset.convert_label_to_multilabel(
            self.all_classes[label])

        if self.transform:
            if isinstance(self.transform, albumentations.core.composition.Compose):
                res = self.transform(image=np.array(image))
                image = res['image'].astype(np.float32)
                image = image.transpose(2, 0, 1)
            else:
                image = self.transform(image)

        return {'image': image, 'label': label, 'binarized_multilabel': binarized_multilabel, 'img_path': img_path}


class Mass_Margins_Dataset(Dataset):
    classes = np.array(['ILL_DEFINED',
                        'CIRCUMSCRIBED',
                        'SPICULATED',
                        'MICROLOBULATED',
                        'OBSCURED'])
    combined_classes = np.array([
        'CIRCUMSCRIBED-ILL_DEFINED',
        'CIRCUMSCRIBED-OBSCURED',
        'CIRCUMSCRIBED-OBSCURED-ILL_DEFINED',
        'CIRCUMSCRIBED-MICROLOBULATED',
        'CIRCUMSCRIBED-MICROLOBULATED-ILL_DEFINED',
        'CIRCUMSCRIBED-SPICULATED',
        'ILL_DEFINED-SPICULATED',
        'MICROLOBULATED-ILL_DEFINED',
        'MICROLOBULATED-ILL_DEFINED-SPICULATED',
        'MICROLOBULATED-SPICULATED',
        'OBSCURED-CIRCUMSCRIBED',
        'OBSCURED-ILL_DEFINED',
        'OBSCURED-ILL_DEFINED-SPICULATED',
        'OBSCURED-SPICULATED'
    ])

    @staticmethod
    def convert_label_to_multilabel(class_name):
        '''Convert class name to zero-one vector'''
        multilabel = np.zeros(Mass_Margins_Dataset.classes.shape)
        for label in class_name.split('-'):
            multilabel += (Mass_Margins_Dataset.classes == label).astype(float)
        return multilabel

    @staticmethod
    def convert_multilabel_to_label(multilabel):
        '''Convert zero-one vector to class name'''
        labels_idx = np.where(multilabel == 1)

        labels_set = set()

        for label_idx in labels_idx[0]:
            labels_set.add(Mass_Margins_Dataset.classes[label_idx])

        all_classes = np.concatenate((Mass_Margins_Dataset.classes,
                                      Mass_Margins_Dataset.combined_classes))
        for _class in all_classes:
            _class_set = set()

            for single_class in _class.split('-'):
                _class_set.add(single_class)

            if labels_set == _class_set:
                return _class

        # for predicted combined class that does not exist in our dataset
        new_combined_class = '-'.join(natsorted(list(labels_set)))
        return new_combined_class


    def __init__(self, root_dir, transform=None, train_rate=1):
        self.root_dir = root_dir
        self.transform = transform
        self.train_rate = train_rate

        self.images_list = []
        self.labels = []

        self.all_classes = np.concatenate((Mass_Margins_Dataset.classes,
                                           Mass_Margins_Dataset.combined_classes))

        for idx, mass_margins in enumerate(self.all_classes):
            images = glob.glob(os.path.join(root_dir, mass_margins, '*.png'))

            # For training using part of data
            images_len = len(images)
            images = images[:int(images_len*self.train_rate)]

            self.images_list += images
            self.labels += [idx] * len(images)


    def get_classes_weights(self):
        classes_weights = compute_classes_weights(
            data_root=self.root_dir,
            classes_names=Mass_Margins_Dataset.classes,
            combined_classes_names=Mass_Margins_Dataset.combined_classes
        )
        return classes_weights

    def __len__(self):
        return len(self.images_list)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_path = self.images_list[idx]
        img_name, _ = os.path.splitext(os.path.basename(img_path))
        image = Image.open(img_path)

        if image.mode == 'L':
            image = image.convert("RGB")

        label = self.labels[idx]
        binarized_multilabel = Mass_Margins_Dataset.convert_label_to_multilabel(
            self.all_classes[label])

        if self.transform:
            if isinstance(self.transform, albumentations.core.composition.Compose):
                res = self.transform(image=np.array(image))
                image = res['image'].astype(np.float32)
                image = image.transpose(2, 0, 1)
            else:
                image = self.transform(image)

        return {'image': image, 'label': label, 'binarized_multilabel': binarized_multilabel, 'img_path': img_path}


class Calc_Type_Dataset(Dataset):
    classes = np.array(["AMORPHOUS", "PUNCTATE", "VASCULAR",
                        "LARGE_RODLIKE", "DYSTROPHIC", "SKIN",
                        "MILK_OF_CALCIUM", "EGGSHELL", "PLEOMORPHIC",
                        "COARSE", "FINE_LINEAR_BRANCHING",
                        "LUCENT_CENTER", "ROUND_AND_REGULAR",
                        ])
    combined_classes = np.array([
        'AMORPHOUS-PLEOMORPHIC',
        'AMORPHOUS-ROUND_AND_REGULAR',
        'COARSE-LUCENT_CENTER',
        'COARSE-PLEOMORPHIC',
        'COARSE-ROUND_AND_REGULAR',
        'COARSE-ROUND_AND_REGULAR-LUCENT_CENTER',
        'LARGE_RODLIKE-ROUND_AND_REGULAR',
        'LUCENT_CENTER-PUNCTATE',
        'PLEOMORPHIC-AMORPHOUS',
        'PLEOMORPHIC-FINE_LINEAR_BRANCHING',
        'PUNCTATE-AMORPHOUS',
        'PUNCTATE-AMORPHOUS-PLEOMORPHIC',
        'PUNCTATE-FINE_LINEAR_BRANCHING',
        'PUNCTATE-LUCENT_CENTER',
        'PUNCTATE-PLEOMORPHIC',
        'PUNCTATE-ROUND_AND_REGULAR',
        'ROUND_AND_REGULAR-AMORPHOUS',
        'ROUND_AND_REGULAR-EGGSHELL',
        'ROUND_AND_REGULAR-LUCENT_CENTER',
        'ROUND_AND_REGULAR-LUCENT_CENTER-DYSTROPHIC',
        'ROUND_AND_REGULAR-LUCENT_CENTER-PUNCTATE',
        'ROUND_AND_REGULAR-PLEOMORPHIC',
        'ROUND_AND_REGULAR-PUNCTATE',
        'ROUND_AND_REGULAR-PUNCTATE-AMORPHOUS',
        'SKIN-COARSE-ROUND_AND_REGULAR',
        'SKIN-PUNCTATE',
        'SKIN-PUNCTATE-ROUND_AND_REGULAR',
        'VASCULAR-COARSE',
        'VASCULAR-COARSE-LUCENT_CENTER',
        'VASCULAR-COARSE-LUCENT_CENTER-ROUND_AND_REGULAR-PUNCTATE'
    ])

    @staticmethod
    def convert_label_to_multilabel(class_name):
        '''Convert class name to zero-one vector'''
        multilabel = np.zeros(Calc_Type_Dataset.classes.shape)
        for label in class_name.split('-'):
            multilabel += (Calc_Type_Dataset.classes == label).astype(float)
        return multilabel

    @staticmethod
    def convert_multilabel_to_label(multilabel):
        '''Convert zero-one vector to class name'''
        labels_idx = np.where(multilabel == 1)

        labels_set = set()

        for label_idx in labels_idx[0]:
            labels_set.add(Calc_Type_Dataset.classes[label_idx])

        all_classes = np.concatenate((Calc_Type_Dataset.classes,
                                      Calc_Type_Dataset.combined_classes))
        for _class in all_classes:
            _class_set = set()

            for single_class in _class.split('-'):
                _class_set.add(single_class)

            if labels_set == _class_set:
                return _class

        # for predicted combined class that does not exist in our dataset
        new_combined_class = '-'.join(natsorted(list(labels_set)))
        return new_combined_class


    def __init__(self, root_dir, transform=None, train_rate=1):
        self.root_dir = root_dir
        self.transform = transform
        self.train_rate = train_rate

        self.images_list = []
        self.labels = []

        self.all_classes = np.concatenate((Calc_Type_Dataset.classes,
                                           Calc_Type_Dataset.combined_classes))

        for idx, calc_type in enumerate(self.all_classes):
            images = glob.glob(os.path.join(root_dir, calc_type, '*.png'))

            # For training using part of data
            images_len = len(images)
            images = images[:int(images_len*self.train_rate)]

            self.images_list += images
            self.labels += [idx] * len(images)


    def get_classes_weights(self):
        classes_weights = compute_classes_weights(
            data_root=self.root_dir,
            classes_names=Calc_Type_Dataset.classes,
            combined_classes_names=Calc_Type_Dataset.combined_classes
        )
        return classes_weights

    def __len__(self):
        return len(self.images_list)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_path = self.images_list[idx]
        img_name, _ = os.path.splitext(os.path.basename(img_path))
        image = Image.open(img_path)

        if image.mode == 'L':
            image = image.convert("RGB")

        label = self.labels[idx]
        binarized_multilabel = Calc_Type_Dataset.convert_label_to_multilabel(
            self.all_classes[label])

        if self.transform:
            if isinstance(self.transform, albumentations.core.composition.Compose):
                res = self.transform(image=np.array(image))
                image = res['image'].astype(np.float32)
                image = image.transpose(2, 0, 1)
            else:
                image = self.transform(image)

        return {'image': image, 'label': label, 'binarized_multilabel': binarized_multilabel, 'img_path': img_path}


class Calc_Dist_Dataset(Dataset):
    classes = np.array(["CLUSTERED",
                       "LINEAR",
                       "REGIONAL",
                       "DIFFUSELY_SCATTERED",
                       "SEGMENTAL"])
    combined_classes = np.array([
        'CLUSTERED-LINEAR',
        'CLUSTERED-SEGMENTAL',
        'LINEAR-SEGMENTAL'
    ])

    @staticmethod
    def convert_label_to_multilabel(class_name):
        '''Convert class name to zero-one vector'''
        multilabel = np.zeros(Calc_Dist_Dataset.classes.shape)
        for label in class_name.split('-'):
            multilabel += (Calc_Dist_Dataset.classes == label).astype(float)
        return multilabel

    @staticmethod
    def convert_multilabel_to_label(multilabel):
        '''Convert zero-one vector to class name'''
        labels_idx = np.where(multilabel == 1)

        labels_set = set()

        for label_idx in labels_idx[0]:
            labels_set.add(Calc_Dist_Dataset.classes[label_idx])

        all_classes = np.concatenate((Calc_Dist_Dataset.classes,
                                      Calc_Dist_Dataset.combined_classes))
        for _class in all_classes:
            _class_set = set()

            for single_class in _class.split('-'):
                _class_set.add(single_class)

            if labels_set == _class_set:
                return _class

        # for predicted combined class that does not exist in our dataset
        new_combined_class = '-'.join(natsorted(list(labels_set)))
        return new_combined_class


    def __init__(self, root_dir, transform=None, train_rate=1):
        self.root_dir = root_dir
        self.transform = transform
        self.train_rate = train_rate

        self.images_list = []
        self.labels = []

        self.all_classes = np.concatenate((Calc_Dist_Dataset.classes,
                                           Calc_Dist_Dataset.combined_classes))

        for idx, mass_shape in enumerate(self.all_classes):
            images = glob.glob(os.path.join(root_dir, mass_shape, '*.png'))

            # For training using part of data
            images_len = len(images)
            images = images[:int(images_len*self.train_rate)]

            self.images_list += images
            self.labels += [idx] * len(images)


    def get_classes_weights(self):
        classes_weights = compute_classes_weights(
            data_root=self.root_dir,
            classes_names=Calc_Dist_Dataset.classes,
            combined_classes_names=Calc_Dist_Dataset.combined_classes
        )
        return classes_weights

    def __len__(self):
        return len(self.images_list)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_path = self.images_list[idx]
        img_name, _ = os.path.splitext(os.path.basename(img_path))
        image = Image.open(img_path)

        if image.mode == 'L':
            image = image.convert("RGB")

        label = self.labels[idx]
        binarized_multilabel = Calc_Dist_Dataset.convert_label_to_multilabel(
            self.all_classes[label])

        if self.transform:
            if isinstance(self.transform, albumentations.core.composition.Compose):
                res = self.transform(image=np.array(image))
                image = res['image'].astype(np.float32)
                image = image.transpose(2, 0, 1)
            else:
                image = self.transform(image)

        return {'image': image, 'label': label, 'binarized_multilabel': binarized_multilabel, 'img_path': img_path}


class Breast_Density_Dataset(Dataset):
    classes = np.array(['1', '2', '3', '4'])

    def __init__(self, mass_root_dir, calc_root_dir, transform=None, train_rate=1):
        self.mass_root_dir = mass_root_dir
        self.calc_root_dir = calc_root_dir
        self.transform = transform
        self.train_rate = train_rate

        self.images_list = []
        self.labels = []

        for idx, breast_density in enumerate(Breast_Density_Dataset.classes):
            #### Mass ####
            mass_images = glob.glob(os.path.join(
                mass_root_dir, str(breast_density), '*.png'))

            # For training using part of data
            mass_images_len = len(mass_images)
            mass_images = mass_images[:int(mass_images_len*self.train_rate)]

            self.images_list += mass_images
            self.labels += [idx] * len(mass_images)

            #### Calc ####
            calc_images = glob.glob(os.path.join(
                calc_root_dir, str(breast_density), '*.png'))

            # For training using part of data
            calc_images_len = len(calc_images)
            calc_images = calc_images[:int(calc_images_len*self.train_rate)]

            self.images_list += calc_images
            self.labels += [idx] * len(calc_images)

    def get_classes_weights(self):
        classes_weights = compute_classes_weights_mass_calc(
            mass_root=self.mass_root_dir,
            calc_root=self.calc_root_dir,
            classes_names=Breast_Density_Dataset.classes
        )
        return classes_weights

    def __len__(self):
        return len(self.images_list)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_path = self.images_list[idx]
        img_name, _ = os.path.splitext(os.path.basename(img_path))
        image = Image.open(img_path)
        label = self.labels[idx]

        if self.transform:
            image = self.transform(image)

        return {'image': image, 'label': label, 'img_path': img_path}


class Pathology_Dataset(Dataset):
    classes = np.array(['BENIGN', 'MALIGNANT'])

    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform

        self.images_list = []
        self.labels = []

        for idx, pathology in enumerate(Pathology_Dataset.classes):
            images = glob.glob(os.path.join(root_dir, pathology, '*.png'))
            self.images_list += images
            self.labels += [idx] * len(images)

    def get_classes_weights(self):
        classes_weights = compute_classes_weights(
            data_root=self.root_dir,
            classes_names=Pathology_Dataset.classes)
        return classes_weights

    def __len__(self):
        return len(self.images_list)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_path = self.images_list[idx]
        img_name, _ = os.path.splitext(os.path.basename(img_path))
        image = Image.open(img_path)
        label = self.labels[idx]

        if self.transform:
            image = self.transform(image)

        return {'image': image, 'label': label, 'img_path': img_path}


class Mass_Calc_Pathology_Dataset(Dataset):
    classes = np.array(['BENIGN', 'MALIGNANT'])

    def __init__(self, mass_root_dir, calc_root_dir, transform=None, train_rate=1):
        self.transform = transform
        self.mass_root_dir = mass_root_dir
        self.calc_root_dir = calc_root_dir

        self.images_list = []
        self.labels = []

        for idx, pathology in enumerate(Mass_Calc_Pathology_Dataset.classes):
            mass_images = glob.glob(os.path.join(
                mass_root_dir, pathology, '*.png'))
            self.images_list += mass_images
            self.labels += [idx] * len(mass_images)

            calc_images = glob.glob(os.path.join(
                calc_root_dir, pathology, '*.png'))
            self.images_list += calc_images
            self.labels += [idx] * len(calc_images)

    def get_classes_weights(self):
        classes_weights = compute_classes_weights_mass_calc(
            mass_root=self.mass_root_dir,
            calc_root=self.calc_root_dir,
            classes_names=Mass_Calc_Pathology_Dataset.classes
        )
        return classes_weights

    def __len__(self):
        return len(self.images_list)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_path = self.images_list[idx]
        img_name, _ = os.path.splitext(os.path.basename(img_path))
        image = Image.open(img_path)
        label = self.labels[idx]

        if self.transform:
            image = self.transform(image)

        return {'image': image, 'label': label, 'img_path': img_path}


class Four_Classes_Mass_Calc_Pathology_Dataset(Dataset):
    classes = np.array(['BENIGN_MASS', 'MALIGNANT_MASS', 'BENIGN_CALC', 'MALIGNANT_CALC'])

    def __init__(self, mass_root_dir, calc_root_dir, transform=None, train_rate=1):
        '''
        Args:
        train_rate(float) - part of training data you want to use for training. This is for plotting the learning curve
        '''
        self.transform = transform
        self.train_rate = train_rate
        self.mass_root_dir = mass_root_dir
        self.calc_root_dir = calc_root_dir

        self.images_list = []
        self.labels = []

        for idx, class_name in enumerate(Four_Classes_Mass_Calc_Pathology_Dataset.classes):
            pathology, lesion_type = class_name.split('_')

            if lesion_type == 'MASS':
                mass_images = glob.glob(os.path.join(
                    mass_root_dir, pathology, '*.png'))

                if self.train_rate is not None:
                    mass_images_len = len(mass_images)
                    mass_images = mass_images[:int(mass_images_len * self.train_rate)]

                self.images_list += mass_images
                self.labels += [idx] * len(mass_images)
            elif lesion_type == 'CALC':
                calc_images = glob.glob(os.path.join(
                    calc_root_dir, pathology, '*.png'))

                if self.train_rate is not None:
                    calc_images_len = len(calc_images)
                    calc_images = calc_images[:int(calc_images_len * self.train_rate)]

                self.images_list += calc_images
                self.labels += [idx] * len(calc_images)

    def get_classes_weights(self):
        classes_weights = compute_classes_weights_mass_calc_pathology_4class(
            mass_root=self.mass_root_dir,
            calc_root=self.calc_root_dir,
            classes_names=Four_Classes_Mass_Calc_Pathology_Dataset.classes
        )
        return classes_weights

    def __len__(self):
        return len(self.images_list)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_path = self.images_list[idx]
        img_name, _ = os.path.splitext(os.path.basename(img_path))

        image = Image.open(img_path)

        if image.mode == 'L':
            image = image.convert("RGB")

        label = self.labels[idx]

        if self.transform:
            if isinstance(self.transform, albumentations.core.composition.Compose):
                res = self.transform(image=np.array(image))
                image = res['image'].astype(np.float32)
                image = image.transpose(2, 0, 1)
            else:
                image = self.transform(image)

        return {'image': image, 'label': label, 'img_path': img_path}


class Five_Classes_Mass_Calc_Pathology_Dataset(Dataset):
    classes = np.array(['BACKGROUND', 'BENIGN_MASS', 'MALIGNANT_MASS', 'BENIGN_CALC', 'MALIGNANT_CALC'])

    def __init__(self, mass_root_dir, calc_root_dir, bg_root_dir, transform=None):
        self.transform = transform
        self.mass_root_dir = mass_root_dir
        self.calc_root_dir = calc_root_dir
        self.bg_root_dir = bg_root_dir

        self.images_list = []
        self.labels = []


        for idx, class_name in enumerate(Five_Classes_Mass_Calc_Pathology_Dataset.classes):
            if class_name == 'BACKGROUND':
                bg_images = glob.glob(os.path.join(bg_root_dir, class_name, '*.png'))
                self.images_list += bg_images
                self.labels += [idx] * len(bg_images)

                if len(bg_images) == 0:
                    raise ValueError
            else:
                pathology, lesion_type = class_name.split('_')

                if lesion_type == 'MASS':
                    mass_images = glob.glob(os.path.join(
                        mass_root_dir, pathology, '*.png'))
                    self.images_list += mass_images
                    self.labels += [idx] * len(mass_images)

                    if len(mass_images) == 0:
                        raise ValueError
                elif lesion_type == 'CALC':
                    calc_images = glob.glob(os.path.join(
                        calc_root_dir, pathology, '*.png'))
                    self.images_list += calc_images
                    self.labels += [idx] * len(calc_images)

                    if len(calc_images) == 0:
                        raise ValueError

    def get_images_list(self):
        return self.images_list

    def get_labels(self):
        return self.labels

    def get_weights(self):
        classes_weights = compute_classes_weights_mass_calc_pathology_5class(
            mass_root=self.mass_root_dir,
            calc_root=self.calc_root_dir,
            bg_root=os.path.join(self.bg_root_dir, 'train'),
            classes_names=Five_Classes_Mass_Calc_Pathology_Dataset.classes
        )
        return classes_weights

    def __len__(self):

        return len(self.images_list)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_path = self.images_list[idx]
        img_name, _ = os.path.splitext(os.path.basename(img_path))
        image = Image.open(img_path)

        if image.mode == 'L':
            image = image.convert("RGB")

        label = self.labels[idx]

        if self.transform:
            if isinstance(self.transform, albumentations.core.composition.Compose):
                res = self.transform(image=np.array(image))
                image = res['image'].astype(np.float32)
                image = image.transpose(2, 0, 1)
            else:
                image = self.transform(image)


        return {'image': image, 'label': label, 'img_path': img_path}


class  Four_Classes_Features_Pathology_Dataset(Dataset):
    classes = np.array(['BENIGN_MASS', 'MALIGNANT_MASS', 'BENIGN_CALC', 'MALIGNANT_CALC'])

    def __init__(self, mass_annotation_file, mass_root_dir, calc_annotation_file, calc_root_dir, uncertainty=0, missed_feats_num=0, missing_feats_fill='zeroes', transform=None, train_rate=1):
        self.mass_annotations = pd.read_csv(mass_annotation_file)
        self.calc_annotations = pd.read_csv(calc_annotation_file)
        self.uncertainty = uncertainty
        self.missed_feats_num = missed_feats_num
        self.missing_feats_fill = missing_feats_fill
        self.transform = transform
        self.train_rate = train_rate

        self.mass_root_dir = mass_root_dir
        self.calc_root_dir = calc_root_dir

        self.images_list = []
        self.labels = []
        self.lesion_types = []

        for idx, cls in enumerate(Four_Classes_Features_Pathology_Dataset.classes):
            pathology, lesion_type = cls.split("_")
            if lesion_type == "MASS":
                mass_images = glob.glob(os.path.join(
                    mass_root_dir, pathology, '*.png'))

                if self.train_rate is not None:
                    mass_images_len = len(mass_images)
                    mass_images = mass_images[:int(mass_images_len * self.train_rate)]

                self.images_list += mass_images
                self.labels += [idx] * len(mass_images)
                self.lesion_types += ['MASS'] * len(mass_images)
            else:
                calc_images = glob.glob(os.path.join(
                    calc_root_dir, pathology, '*.png'))

                if self.train_rate is not None:
                    calc_images_len = len(calc_images)
                    calc_images = calc_images[:int(calc_images_len * self.train_rate)]

                self.images_list += calc_images
                self.labels += [idx] * len(calc_images)
                self.lesion_types += ['CALC'] * len(calc_images)

        # For random feature values
        self.mass_feats_dist = Four_Classes_Features_Pathology_Dataset.get_mass_feats_empirical_dist(self.images_list, self.lesion_types, self.mass_annotations)
        self.calc_feats_dist = Four_Classes_Features_Pathology_Dataset.get_calc_feats_empirical_dist(self.images_list, self.lesion_types, self.calc_annotations)


    def get_classes_weights(self):
        classes_weights = compute_classes_weights_mass_calc_pathology_4class(
            mass_root=self.mass_root_dir,
            calc_root=self.calc_root_dir,
            classes_names=Four_Classes_Mass_Calc_Pathology_Dataset.classes
        )
        return classes_weights


    @staticmethod
    def convert_mass_feats_1hot(breast_density, mass_shape, mass_margins, ignore_vector=None):
        '''
        parameters:
        ignore_vector: the 3-d vector of zeros and ones. Each of the 3 dimension represents for either: breast_density, mass_shape or mass_margins
        '''
        BREAST_DENSITY_TYPES = np.array([1, 2, 3, 4])
        BREAST_MASS_SHAPES = np.array(['ROUND', 'OVAL', 'IRREGULAR', 'LOBULATED', 'ARCHITECTURAL_DISTORTION',
                                       'ASYMMETRIC_BREAST_TISSUE', 'LYMPH_NODE', 'FOCAL_ASYMMETRIC_DENSITY'])
        BREAST_MASS_MARGINS = np.array(
            ['ILL_DEFINED', 'CIRCUMSCRIBED', 'SPICULATED', 'MICROLOBULATED', 'OBSCURED'])

        # Breast Density
        one_hot_breast_density = (
            BREAST_DENSITY_TYPES == breast_density).astype('int')

        total_ones = 0

        # Mass Shape
        if (mass_shape is None) or (type(mass_shape) is float and math.isnan(mass_shape)):
            one_hot_mass_shape = np.zeros(BREAST_MASS_SHAPES.shape, dtype=int)
        else:
            if '-' in mass_shape:
                one_hot_mass_shape = np.zeros(BREAST_MASS_SHAPES.shape, dtype=int)
                for shape in mass_shape.split('-'):
                    one_hot_mass_shape += (BREAST_MASS_SHAPES == shape).astype('int')
                    total_ones += 1
            else:
                one_hot_mass_shape = (BREAST_MASS_SHAPES == mass_shape).astype('int')
                total_ones += 1

        # Mass Margin
        if (mass_margins is None) or (type(mass_margins) is float and math.isnan(mass_margins)):
            one_hot_mass_margins = np.zeros(BREAST_MASS_MARGINS.shape, dtype=int)
        else:
            if '-' in mass_margins:
                one_hot_mass_margins = np.zeros(BREAST_MASS_MARGINS.shape, dtype=int)
                for margin in mass_margins.split('-'):
                    one_hot_mass_margins += (BREAST_MASS_MARGINS == margin).astype('int')
                    total_ones += 1
            else:
                one_hot_mass_margins = (BREAST_MASS_MARGINS ==
                                        mass_margins).astype('int')
                total_ones += 1

        if ignore_vector is not None:
            if ignore_vector[0] == 1:
                one_hot_breast_density = np.zeros(one_hot_breast_density.shape)
            if ignore_vector[1] == 1:
                one_hot_mass_shape = np.zeros(one_hot_mass_shape.shape)
            if ignore_vector[2] == 1:
                one_hot_mass_margins = np.zeros(one_hot_mass_margins.shape)
                
        ret = np.concatenate((one_hot_mass_shape, one_hot_mass_margins))

        if ignore_vector is None:
            assert np.sum(ret) == total_ones

        return ret, one_hot_breast_density 

    @staticmethod
    def convert_calc_feats_1hot(breast_density, calc_type, calc_distribution, ignore_vector=None):
        '''
        parameters:
        ignore_vector: the 3-d vector of zeros and ones. Each of the 3 dimension represents for either: breast_density, calc_type or calc_distribution
        '''
        if breast_density == 0:
            breast_density = 1  # one test sample is false labelling

        BREAST_DENSITY_TYPES = np.array([1, 2, 3, 4])
        BREAST_CALC_TYPES = np.array(["AMORPHOUS", "PUNCTATE", "VASCULAR", "LARGE_RODLIKE", "DYSTROPHIC", "SKIN", "MILK_OF_CALCIUM",
                                      "EGGSHELL", "PLEOMORPHIC", "COARSE", "FINE_LINEAR_BRANCHING", "LUCENT_CENTER", "ROUND_AND_REGULAR", "LUCENT_CENTERED"])
        BREAST_CALC_DISTS = np.array(
            ["CLUSTERED", "LINEAR", "REGIONAL", "DIFFUSELY_SCATTERED", "SEGMENTAL"])

        # Breast Density
        one_hot_breast_density = (
            BREAST_DENSITY_TYPES == breast_density).astype('int')
        total_ones = 0 

        # Calc Type
        if (calc_type is None) or (type(calc_type) is float and math.isnan(calc_type)):
            one_hot_calc_type = np.zeros(BREAST_CALC_TYPES.shape, dtype=int)
        else:
            if '-' in calc_type:
                one_hot_calc_type = np.zeros(BREAST_CALC_TYPES.shape, dtype=int)
                for ctype in calc_type.split('-'):
                    one_hot_calc_type += (BREAST_CALC_TYPES == ctype).astype('int')
                    total_ones += 1
            else:
                one_hot_calc_type = (BREAST_CALC_TYPES == calc_type).astype('int')
                total_ones += 1

        # Calc Dist
        if (calc_distribution is None) or (type(calc_distribution) is float and math.isnan(calc_distribution)):
            one_hot_calc_distribution = np.zeros(BREAST_CALC_DISTS.shape, dtype=int)
        else:
            if '-' in calc_distribution:
                one_hot_calc_distribution = np.zeros(BREAST_CALC_DISTS.shape, dtype=int)
                for dist in calc_distribution.split('-'):
                    one_hot_calc_distribution += (BREAST_CALC_DISTS == dist).astype('int')
                    total_ones += 1
            else:
                one_hot_calc_distribution = (BREAST_CALC_DISTS == calc_distribution).astype('int')
                total_ones += 1

        if ignore_vector is not None:
            if ignore_vector[0] == 1:
                one_hot_breast_density = np.zeros(one_hot_breast_density.shape)
            if ignore_vector[1] == 1:
                one_hot_calc_type = np.zeros(one_hot_calc_type.shape)
            if ignore_vector[2] == 1:
                one_hot_calc_distribution = np.zeros(one_hot_calc_distribution.shape)

        ret = np.concatenate(
            (one_hot_calc_type, one_hot_calc_distribution))

        if ignore_vector is None:
            assert np.sum(ret) == total_ones

        return ret, one_hot_breast_density

    @staticmethod
    def get_mass_feats_empirical_dist(images_list, lesion_types, mass_annotations):
        mass_feats_empirical_dist = set()

        for img_path, lesion_type in zip(images_list, lesion_types):
            if lesion_type == 'CALC':
                continue

            img_name, _ = os.path.splitext(os.path.basename(img_path))

            roi_idx = 0
            while True:
                roi_idx += 1
                rslt_df = get_info_lesion(mass_annotations, f'{img_name}')

                if len(rslt_df) > 0:
                    break

            mass_shape = rslt_df['mass shape'].to_numpy()[0]
            mass_margins = rslt_df['mass margins'].to_numpy()[0]

            mass_feats_empirical_dist.add((mass_shape, mass_margins))

        return mass_feats_empirical_dist

    @staticmethod
    def get_calc_feats_empirical_dist(images_list, lesion_types, calc_annotations):
        calc_feats_empirical_dist = set()

        for img_path, lesion_type in zip(images_list, lesion_types):
            if lesion_type == 'MASS':
                continue

            img_name, _ = os.path.splitext(os.path.basename(img_path))

            roi_idx = 0
            while True:
                roi_idx += 1
                rslt_df = get_info_lesion(calc_annotations, f'{img_name}')

                if len(rslt_df) > 0:
                    break

            calc_type = rslt_df['calc type'].to_numpy()[0]
            calc_distribution = rslt_df['calc distribution'].to_numpy()[0]

            calc_feats_empirical_dist.add((calc_type, calc_distribution))

        return calc_feats_empirical_dist

    def __len__(self):
        return len(self.images_list)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_path = self.images_list[idx]
        lesion_type = self.lesion_types[idx]
        img_name, _ = os.path.splitext(os.path.basename(img_path))
        image = Image.open(img_path)
        label = self.labels[idx]

        ignore_vector = None
        if self.missed_feats_num > 0:
            avail_feats_num = 3 - self.missed_feats_num
            ignore_vector = [0] * avail_feats_num + [1] * self.missed_feats_num
            ignore_vector = np.random.permutation(ignore_vector)


        if lesion_type == 'MASS':
            roi_idx = 0
            while True:
                roi_idx += 1
                rslt_df = get_info_lesion(self.mass_annotations, f'{img_name}')

                if len(rslt_df) > 0:
                    break

            breast_density = rslt_df['breast_density'].to_numpy()[0]
            mass_shape = rslt_df['mass shape'].to_numpy()[0]
            mass_margins = rslt_df['mass margins'].to_numpy()[0]
            feature_vector, breast_density_1hot = Four_Classes_Features_Pathology_Dataset.convert_mass_feats_1hot(
                breast_density, mass_shape, mass_margins, ignore_vector)

            if self.missing_feats_fill == 'zeroes':
                feature_vector = np.concatenate((breast_density_1hot, feature_vector, np.zeros(19)))
            elif self.missing_feats_fill == 'emp_sampling':
                calc_type, calc_distribution = random.choice(tuple(self.calc_feats_dist))
                missing_calc_feature_vector, _ = Four_Classes_Features_Pathology_Dataset.convert_calc_feats_1hot(
                    1, calc_type, calc_distribution, ignore_vector=None) # We dont use the parameter 'Breast Density', so just
                                                                    # set it to random value. (for e.g.: 1)
                feature_vector = np.concatenate((breast_density_1hot, feature_vector, missing_calc_feature_vector))

            if random.random() < self.uncertainty:
                feature_vector = np.zeros(feature_vector.shape)
        elif lesion_type == 'CALC':
            roi_idx = 0
            while True:
                roi_idx += 1
                rslt_df = get_info_lesion(self.calc_annotations, f'{img_name}')

                if len(rslt_df) > 0:
                    break

            breast_density = rslt_df['breast density'].to_numpy()[0]
            calc_type = rslt_df['calc type'].to_numpy()[0]
            calc_distribution = rslt_df['calc distribution'].to_numpy()[0]
            feature_vector, breast_density_1hot = Four_Classes_Features_Pathology_Dataset.convert_calc_feats_1hot(
                breast_density, calc_type, calc_distribution, ignore_vector)

            if self.missing_feats_fill == 'zeroes':
                feature_vector = np.concatenate((breast_density_1hot, np.zeros(13), feature_vector))
            elif self.missing_feats_fill == 'emp_sampling':
                mass_shape, mass_margins = random.choice(tuple(self.mass_feats_dist))
                missing_mass_feature_vector, _ = Four_Classes_Features_Pathology_Dataset.convert_mass_feats_1hot(
                    1, mass_shape, mass_margins, ignore_vector=None)

                feature_vector = np.concatenate((breast_density_1hot, missing_mass_feature_vector, feature_vector))

            if random.random() < self.uncertainty:
                feature_vector = np.zeros(feature_vector.shape)

        if self.transform:
            image = self.transform(image)

        return {'image': image, 'label': label, 'feature_vector': feature_vector, 'img_path': img_path}
